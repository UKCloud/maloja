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
import time
from urllib.parse import quote as urlquote
from urllib.parse import urlparse
import uuid
import warnings
import xml.etree.ElementTree as ET

from maloja.builder import Builder
from maloja.model import Gateway
from maloja.model import Network
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


class Inspector(Builder):
    """
    The Inspector accepts a sequence of objects from the
    :ref:`data model <data model>` and uses them to check
    existing virtual infrastructure.

    """

    @staticmethod
    def inspection_handler(
        msg, session, token, callback=None, results=None, status=None, **kwargs
    ):
        log = logging.getLogger("maloja.inspection.handler")
        try:
            inspector = Inspector(msg.objects, results, session.executor)
        except Exception as e:
            log.error(str(getattr(e, "args", e) or e))
            return tuple()
        else:
            headers = {
                "Accept": "application/*+xml;version=5.5",
                token.key: token.value,
            }
            session.headers.update(headers)
            return (
                session.executor.submit(
                    inspector, session, token, callback, status, name=msg.name
                ),
            )

    def __init__(self, objs, results, executor=None, loop=None, **kwargs):
        """
        :param objs: a sequence of Maloja objects
        :param results: a queue to which status reports will be pushed
        :param executor: a `concurrent.futures.Executor` object

        """
        super().__init__(objs, results, executor=None, loop=None, **kwargs)

    def __call__(self, session, token, callback=None, status=None, name=None):
        """
        An Inspector is a callable object which runs in its own thread.

        It gets started up like this::

            executor.submit(inspector, session, token, callback, status)

        :param session: a *requests.futures* session object.
        :param token: an authorization Token for the VMware API.
        :param callback: a function to be called when
            the inspector is done.
        :param status: the current status at the point the inspector
            is invoked.

        """
        log = logging.getLogger("maloja.inspector")

        self.check_orgvdcnetwork(session, token, status=status)
        self.check_vapp(session, token, status=status, name=name)
        self.check_vms(session, token, status=status, name=name)
        self.check_gateway(session, token, status=status)

    def check_orgvdcnetwork(self, session, token, callback=None, status=None, **kwargs):
        log = logging.getLogger("maloja.inspector.check_orgvdcnetwork")

        ns = "{http://www.vmware.com/vcloud/v1.5}"
        vdc = self.plans[Vdc][0]
        networksUrl = None
        try:
            response = self.check_response(*self.wait_for(session.get(vdc.href)))
        except (StopIteration, TypeError):
            self.send_status(status, stop=True)
            return

        tree = ET.fromstring(response.text)
        networksUrl = next(find_xpath(
            "./*/[@type='application/vnd.vmware.vcloud.query.records+xml']",
            tree,
            rel="orgVdcNetworks"
        ), None)

        try:
            response = self.check_response(*self.wait_for(
                session.get(networksUrl.attrib.get("href"))
            ))
        except (StopIteration, TypeError):
            self.send_status(status, stop=True)
            return

        tree = ET.fromstring(response.text)
        nets = {}
        for elem in tree.iter(ns + "OrgVdcNetworkRecord"):
            try:
                response = self.check_response(*self.wait_for(
                    session.get(elem.attrib.get("href"))
                ))
            except (StopIteration, TypeError):
                self.send_status(status, stop=True)
            else:
                tree = ET.fromstring(response.text)
                obj = Network().feed_xml(tree)
                nets[obj.name] = obj

        target = self.plans[Network][0]
        net = nets.get(target.name, None)
        if net is None:
            log.warning("Network '{0}' not found.".format(target.name))
            self.send_status(status, stop=True)
            return

        missing = (
            set([(n, str(v)) for n, v in target.elements]) -
            set([(n, str(v)) for n, v in net.elements])
        )
        for n, v in missing:
            log.warning("Missing {0}: {1}".format(n, v))

        if not missing:
            log.info("Network '{0.name}' OK.".format(target))

    def check_vapp(self, session, token, callback=None, status=None, **kwargs):
        log = logging.getLogger("maloja.inspector.check_vapp")

        ns = "{http://www.vmware.com/vcloud/v1.5}"
        tgt = self.plans[Template][0]
        try:
            response = self.check_response(*self.wait_for(session.get(tgt.href)))
        except (StopIteration, TypeError):
            self.send_status(status, stop=True)
            return

        tree = ET.fromstring(response.text)
        obj = VApp().feed_xml(tree)

        truth = set([(n, str(v)) for n, v in obj.elements])
        goal = set([(n, str(v)) for n, v in tgt.elements])
        unfit = truth.difference(goal)
        if not unfit:
            log.info("VApp '{0.name}' OK.".format(tgt))

        for n, v in unfit:
            if n not in ("dateCreated", "href"):
                log.warning("Found {0}: '{1}', expected {2}".format(
                    n, getattr(obj, n, ""), getattr(tgt, n, "")))

    def check_vms(self, session, token, callback=None, status=None, name=None, **kwargs):
        log = logging.getLogger("maloja.inspector.check_vms")

        ns = "{http://www.vmware.com/vcloud/v1.5}"
        vdc = self.plans[Vdc][0]
        try:
            response = self.check_response(*self.wait_for(session.get(vdc.href)))
        except (StopIteration, TypeError):
            self.send_status(status, stop=True)
            return

        tree = ET.fromstring(response.text)
        ref = next(find_xpath(
            "./*/*/[@type='application/vnd.vmware.vcloud.vApp+xml']",
            tree,
            name=name
        ), None)
        try:
            response = self.check_response(*self.wait_for(
                session.get(ref.attrib.get("href"))
            ))
        except (AttributeError, StopIteration, TypeError):
            self.send_status(status, stop=True)
            return

        tree = ET.fromstring(response.text)
        obj = VApp().feed_xml(tree)

        url = urlparse(response.url)
        query = "/".join((
            url.scheme + "://" + url.netloc,
            "api/vms/query?filter=(container=={0})".format(urlquote(response.url))
        ))
        vms = list(find_xpath(
            "./*/*/[@type='application/vnd.vmware.vcloud.vm+xml']",
            ET.fromstring(response.text)
        ))

        if len(vms) > len(self.plans[Vm]):
            log.warning("VApp contains extra VMs.")
        elif len(vms) < len(self.plans[Vm]):
            log.warning("VM missing from VApp.")

        for ref in vms:
            fault = False
            try:
                response = self.check_response(*self.wait_for(
                    session.get(ref.attrib.get("href"))
                ))
            except (AttributeError, StopIteration, TypeError):
                self.send_status(status, stop=True)
                return

            tree = ET.fromstring(response.text)
            obj = Vm().feed_xml(tree)

            picks = {}
            truth = set([(n, str(v)) for n, v in obj.elements])
            for tgt in self.plans[Vm]:
                goal = set([(n, str(v)) for n, v in tgt.elements])
                unfit = truth.difference(goal)
                picks[len(unfit)] = {k: getattr(tgt, k, None) for k, v in unfit}

            pick = picks[min(picks.keys())]
            for n, v in pick.items():
                if n not in ("dateCreated", "href", "mac", "macAddress"):
                    fault = True
                    log.warning("Found {0}: '{1}', expected {2}".format(
                        n, getattr(obj, n, ""), v)
                    )

            if not fault:
                log.info("VM '{0.name}' OK.".format(obj))

    def check_gateway(self, session, token, callback=None, status=None, **kwargs):
        log = logging.getLogger("maloja.inspector.check_gateway")

        ns = "{http://www.vmware.com/vcloud/v1.5}"
        gw = self.plans[Gateway][0]
        try:
            response = self.check_response(*self.wait_for(session.get(gw.href)))
        except (StopIteration, TypeError):
            self.send_status(status, stop=True)
            return

        tree = ET.fromstring(response.text)
        obj = Gateway().feed_xml(tree)

        truth = set([(n, str(v)) for n, v in obj.elements])
        goal = set([(n, str(v)) for n, v in gw.elements])
        unfit = truth.difference(goal)
        if not unfit:
            log.info("Gateway '{0.name}' OK.".format(gw))

        for n, v in unfit:
            if n not in ("dateCreated", "href"):
                log.warning("Found {0}: '{1}', expected {2}".format(
                    n, getattr(obj, n, ""), getattr(gw, n, ""))
                )

