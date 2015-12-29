#!/usr/bin/env python
#   -*- encoding: UTF-8 -*-

import concurrent.futures
import itertools
import logging
import sys
import time
import uuid
import warnings
import xml.etree.ElementTree as ET

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

from chameleon import PageTemplateFile
import pkg_resources

__doc__ = """
The builder module modifies cloud assets according to a design file.

"""

class Builder:

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
                    log.warning(response.text)
            else:
                log.debug(response.text)
        except Exception as e:
            log.error(e)
        finally:
            return response

    @staticmethod
    def get_tasks(response):
        tree = ET.fromstring(response.text)
        return (
            Task().feed_xml(elem)
            for elem in find_xpath(
                "./*/*/[@type='application/vnd.vmware.vcloud.task+xml']",
                tree
            )
        )

    @staticmethod
    def wait_for(*args, timeout=6):
        done, not_done = concurrent.futures.wait(
            args, timeout=timeout,
            return_when=concurrent.futures.FIRST_EXCEPTION
        )
        return (done, not_done)

    def __init__(self, objs, results, executor=None, loop=None, **kwargs):
        log = logging.getLogger("maloja.builder.Builder")
        self.plans = group_by_type(objs)
        self.results = results
        self.executor = executor
        self.token = None
        self.tasks = {}
        self.seq = itertools.count(1)

    def __call__(self, session, token, callback=None, status=None, **kwargs):
        log = logging.getLogger("maloja.builder")

        # Step 1: Instantiate empty VApp

        prototypes = self.plans[VApp] + self.plans[Template]
        macro = PageTemplateFile(
            pkg_resources.resource_filename(
                "maloja.workflow", "InstantiateVAppTemplateParams.pt"
            )
        )
        data = {
            "appliance": {
                "name": uuid.uuid4().hex,
                "description": "Created by Maloja builder",
                "vms": [],
            },
            "networks": [],
            "template": prototypes[0]
        }
        url = "{vdc.href}/{endpoint}".format(
            vdc=self.plans[Vdc][0],
            endpoint="action/instantiateVAppTemplate"
        )
        xml = macro(**data)
        session.headers.update(
            {"Content-Type": "application/vnd.vmware.vcloud.instantiateVAppTemplateParams+xml"})

        try:
            response = self.check_response(
                *self.wait_for(
                    session.post(url, data=xml)
                )
            )
            task = next(self.get_tasks(response))
            self.tasks[task.owner.href] = self.executor.submit(self.monitor, task, session)
        except (StopIteration, TypeError):
            self.send_status(status, stop=True)
            return

        self.wait_for(*self.tasks.values(), timeout=300)

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

    def monitor(self, task, session):
        log = logging.getLogger("maloja.builder.monitor")
        backoff = 0
        while task.status == "running":
            backoff += 1
            time.sleep(backoff)
            done, not_done = concurrent.futures.wait(
                [session.get(task.href)], timeout=6,
                return_when=concurrent.futures.FIRST_EXCEPTION
            )
            response = done.pop().result()
            task.feed_xml(ET.fromstring(response.text))

        log.debug("Backoff: {0}s".format(backoff))
        return task

    def send_status(self, status, stop=False):
        reply = Stop() if stop else None
        seq = next(self.seq)
        status = status or Status(1, seq, seq)
        self.results.put((status, reply))
