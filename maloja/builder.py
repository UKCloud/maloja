#!/usr/bin/env python
#   -*- encoding: UTF-8 -*-

# Copyright Skyscape Cloud Services
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import concurrent.futures
import itertools
import logging
import sys
from threading import Event
import time
import uuid
import warnings
import xml.etree.ElementTree as ET

from maloja.model import Gateway
from maloja.model import Network
from maloja.model import Org
from maloja.model import Task
from maloja.model import Template
from maloja.model import VApp
from maloja.model import Vdc
from maloja.model import Vm
from maloja.planner import check_objects
from maloja.planner import read_objects
from maloja.types import Credentials
from maloja.types import Stop
from maloja.workflow.utils import find_xpath
from maloja.workflow.utils import group_by_type

from chameleon import PageTemplateFile
import pkg_resources

class Builder:
    """
    The Builder accepts a sequence of objects from the
    :ref:`data model <data model>` and uses them to construct
    new virtual infrastructure.

    """

    @staticmethod
    def check_response(done, not_done):
        log = logging.getLogger("maloja.builder.check_response")
        response = None
        try:
            response = done.pop().result()
            if response.status_code == 400:
                if "DUPLICATE_NAME" in response.text:
                    log.warning("Request refused: duplicate name.")
                else:
                    log.warning(response.status_code)
                    log.warning(response.text)
            else:
                log.debug(response.status_code)
                log.debug(response.text)
        except KeyError:
            log.warning("Response incomplete.")
            log.debug(getattr(response, "status_code", "No status code."))
            log.debug(getattr(response, "text", "No text."))
        except Exception as e:
            log.error(e)
        finally:
            return response

    @staticmethod
    def get_tasks(response):
        if response is None:
            return iter(tuple())
        tree = ET.fromstring(response.text)
        return (
            Task().feed_xml(elem)
            for elem in find_xpath(
                "./*/*/[@type='application/vnd.vmware.vcloud.task+xml']",
                tree
            )
        )

    def monitor(self, task, session, status=None, backoff=1):
        """
        The builder launches this method whenever a VMware task is
        initiated. The method tracks the progress of the task.

        """
        log = logging.getLogger("maloja.builder.monitor")

        while True:
            self.send_status(status)
            try:
                time.sleep(backoff)
                backoff = min(backoff + 2, 20)

                log.info("{0.operationName} is {0.status}.".format(task))
                if task.status != "running":
                    return task
            except Exception as e:
                log.error(e)

            # Get next task
            response = None
            while response is None:
                response = Builder.check_response(
                    *Builder.wait_for(
                        session.get(task.owner.href),
                        timeout=6
                    )
                )
            else:
                try:
                    task = next(Builder.get_tasks(response))
                except (AttributeError, StopIteration, TypeError):
                    log.warning("No task in response.")
                    return task
                except Exception as e:
                    log.error(e)
                    response = None

    @staticmethod
    def wait_for(*args, timeout=30):
        log = logging.getLogger("maloja.builder.wait_for")
        done, not_done = concurrent.futures.wait(
            args, timeout=timeout,
            return_when=concurrent.futures.FIRST_EXCEPTION
        )
        return (done, not_done)

    def __init__(self, objs, results, executor=None, loop=None, **kwargs):
        """
        :param objs: a sequence of Maloja objects
        :param results: a queue to which status reports will be pushed
        :param executor: a `concurrent.futures.Executor` object

        """
        log = logging.getLogger("maloja.builder.Builder")
        self.plans = group_by_type(objs)
        self.results = results
        self.executor = executor
        self.token = None
        self.tasks = {}
        self.seq = itertools.count(1)
        self.working = False

    def __call__(self, session, token, callback=None, status=None, **kwargs):
        """
        A Builder is a callable object which runs in its own thread.

        It gets started up like this::

            executor.submit(builder, session, token, callback, status)

        :param session: a *requests.futures* session object.
        :param token: an authorization Token for the VMware API.
        :param callback: a function to be called when
            the builder is done.
        :param status: the current status at the point the builder
            is invoked.

        """
        log = logging.getLogger("maloja.builder")

        self.working = True
        self.executor.submit(self.heartbeat, session, None, self.results, status)
        self.create_orgvdcnetwork_isolated(session, token, status=status)
        self.update_networks(session, token, status=status)
        self.instantiate_vapptemplates(session, token, status=status)
        self.recompose_vapp(session, token, status=status)
        self.working = False
        return

        # Step 2: Get Recompose Link

        op = session.get(task.owner.href)
        done, not_done = self.wait_for(op)
        response = self.check_response(done, not_done)
        link = next(find_xpath(
            "./*/[@type='application/vnd.vmware.vcloud.recomposeVAppParams+xml']",
            ET.fromstring(response.text),
            rel="recompose"
        ), None)

        # Step 3: Add Vms
        # TODO: All VMs at once
        data = {
            "appliance": {
                "name": task.owner.name,
                "description": "Created by Maloja builder",
                "vms": [self.plans[Vm][1]],
            },
            "networks": self.plans[Network],
        }

        macro = PageTemplateFile(
            pkg_resources.resource_filename(
                "maloja.workflow", "RecomposeVAppParams.pt"
            )
        )

        url = link.attrib.get("href")
        xml = macro(**data)
        session.headers.update(
            {"Content-Type": "application/vnd.vmware.vcloud.recomposeVAppParams+xml"}
        )
        op = session.post(url, data=xml)
        log.debug(xml)
        done, not_done = self.wait_for(op)

        response = self.check_response(done, not_done)
        for task in self.get_tasks(response):
            self.tasks[task.owner.href] = self.executor.submit(self.monitor, task, session)

        self.wait_for(*self.tasks.values(), timeout=300)

        # Step 4: Rename VApp
        data = {
            "appliance": {
                "name": prototypes[0].name,
                "description": "Created by Maloja builder",
                "vms": [],
            },
            "networks": [],
        }

        xml = macro(**data)
        op = session.post(url, data=xml)

        done, not_done = self.wait_for(op)
        response = self.check_response(done, not_done)

        self.send_status(status, stop=True)

    def heartbeat(self, session, response, results=None, status=None):
        while self.working:
            time.sleep(15)
            self.send_status(status)

    def create_orgvdcnetwork_isolated(self, session, token, callback=None, status=None, **kwargs):
        log = logging.getLogger("maloja.builder.create_orgvdcnetwork_isolated")

        vdc = self.plans[Vdc][0]
        orgVdcNetwork = self.plans[Network][0]
        macro = PageTemplateFile(
            pkg_resources.resource_filename(
                "maloja.workflow", "OrgVdcNetwork.pt"
            )
        )
        data = {"gateway": None, "network": orgVdcNetwork}
        url = "{service}/{endpoint}".format(
            service=vdc.href.replace("/vdc/", "/admin/vdc/", 1),
            endpoint="networks"
        )
        xml = macro(**data)
        session.headers.update(
            {"Content-Type": "application/vnd.vmware.vcloud.orgVdcNetwork+xml"})

        try:
            response = self.check_response(
                *self.wait_for(
                    session.post(url, data=xml)
                )
            )
            task = next(self.get_tasks(response))
            #event = Event()
            #self.executor.submit(Builder.monitor, task, session, event)

            #log.info("Waiting...")
            #if not event.wait():
            #    # No timeout specified for now
            #    log.warning("Timed out while monitoring {0}".format(vars(task)))
            #else:
            #    log.info("Task complete.")
        except StopIteration:
            # No task related to network suggests one already exists.
            # If so, that will be logged by check_response.
            return
        except TypeError:
            self.send_status(status, stop=True)
            return

    def create_orgvdcnetwork_routed(self, session, token, callback=None, status=None, **kwargs):
        log = logging.getLogger("maloja.builder.create_orgvdcnetwork_routed")
        vdc = self.plans[Vdc][0]
        orgVdcNetwork = self.plans[Network][0]
        macro = PageTemplateFile(
            pkg_resources.resource_filename(
                "maloja.workflow", "OrgVdcNetwork.pt"
            )
        )
        data = {"gateway": None, "network": orgVdcNetwork}
        url = "{service}/{endpoint}".format(
            service=vdc.href.replace("/vdc/", "/admin/vdc/", 1),
            endpoint="networks"
        )
        xml = macro(**data)
        session.headers.update(
            {"Content-Type": "application/vnd.vmware.vcloud.orgVdcNetwork+xml"})
        return

    def instantiate_vapptemplates(self, session, token, callback=None, status=None, **kwargs):
        log = logging.getLogger("maloja.builder.instantiate_vapptemplates")

        macro = PageTemplateFile(
            pkg_resources.resource_filename(
                "maloja.workflow", "InstantiateVAppTemplateParams.pt"
            )
        )

        for n, template in enumerate(self.plans[Template]):
            data = {
                "appliance": {
                    "name": uuid.uuid4().hex,
                    "description": "Created by Maloja builder",
                    "vms": [],
                },
                "networks": self.plans[Network],
                "template": {
                    "name": template.name,
                    "href": template.href
                }
            }

            url = "{vdc.href}/{endpoint}".format(
                vdc=self.plans[Vdc][0],
                endpoint="action/instantiateVAppTemplate"
            )
            xml = macro(**data)
            session.headers.update(
                {"Content-Type": "application/vnd.vmware.vcloud.instantiateVAppTemplateParams+xml"})

            log.info("Instantiating...")
            try:
                response = self.check_response(
                    *self.wait_for(
                        session.post(url, data=xml),
                        timeout=None
                    )
                )
                tree = ET.fromstring(response.text)
                self.plans[VApp].append(
                    VApp().feed_xml(
                        tree, ns="{http://www.vmware.com/vcloud/v1.5}"
                    )
                )
                task = next(self.get_tasks(response))
                log.info("Waiting...")
                self.monitor(task, session, status=status)
                log.info("Task complete.")
            except IndexError:
                log.error("No VApp to match template")
                self.send_status(status, stop=True)
            except (StopIteration, TypeError) as e:
                log.error(e)
                self.send_status(status, stop=True)

    def recompose_vapp(self, session, token, callback=None, status=None, **kwargs):
        log = logging.getLogger("maloja.builder.recompose_vapp")

        macro = PageTemplateFile(
            pkg_resources.resource_filename(
                "maloja.workflow", "RecomposeVAppParams.pt"
            )
        )

        vapp = self.plans[VApp][0]
        template = self.plans[Template][0]
        # TODO: Decide on naming system
        for vm in self.plans[Vm]:
            vm.name = uuid.uuid4().hex
        data = {
            "appliance": {
                "name": vapp.name,
                "description": "Created by Maloja builder",
                "vms": self.plans[Vm],
            },
            "networks": self.plans[Network],
            "template": {
                "name": template.name,
                "href": template.href
            }
        }
        xml = macro(**data)
        log.debug(xml)
        url = "{vapp.href}/{endpoint}".format(
            vapp=vapp,
            endpoint="action/recomposeVApp"
        )
        session.headers.update(
            {"Content-Type": "application/vnd.vmware.vcloud.recomposeVAppParams+xml"}
        )
        log.info("Recomposing...")
        try:
            response = self.check_response(
                *self.wait_for(
                    session.post(url, data=xml),
                    timeout=None
                )
            )
            log.debug(response.text)
            tree = ET.fromstring(response.text)
            task = next(
                self.get_tasks(response),
                Task().feed_xml(
                    tree, ns="{http://www.vmware.com/vcloud/v1.5}"
                )
            )
            log.debug(vars(task))
            log.info("Waiting...")
            self.monitor(task, session, status=status)
            log.info("Task complete.")
        except (StopIteration, TypeError) as e:
            log.error(e)
            self.send_status(status, stop=True)

    def update_networks(self, session, token, callback=None, status=None, **kwargs):
        log = logging.getLogger("maloja.builder.update_networks")
        ns = "{http://www.vmware.com/vcloud/v1.5}"
        try:
            response = self.check_response(
                *self.wait_for(
                    session.get(self.plans[Vdc][0].href)
                )
            )
        except (StopIteration, TypeError):
            self.send_status(status, stop=True)
        else:
            tree = ET.fromstring(response.text)
            for elem in tree.iter(ns + "Network"):
                for net in self.plans[Network]:
                    if net.name == elem.attrib.get("name"):
                        net.href = elem.attrib.get("href")

    def send_status(self, status, stop=False):
        reply = Stop() if stop else None
        seq = next(self.seq)
        status = status._replace(job=seq) or Status(1, seq, None)
        self.results.put((status, reply))
