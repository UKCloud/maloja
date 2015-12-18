#!/usr/bin/env python
#   -*- encoding: UTF-8 -*-

import concurrent.futures
import itertools
import logging
import sys
import uuid
import warnings

from maloja.model import Gateway
from maloja.model import Network
from maloja.model import Template
from maloja.model import VApp
from maloja.model import Vdc
from maloja.model import Vm
from maloja.planner import check_objects
from maloja.planner import read_objects
from maloja.types import Credentials
from maloja.types import Stop
from maloja.workflow.utils import group_by_type

from chameleon import PageTemplateFile
import pkg_resources

__doc__ = """
The builder module modifies cloud assets according to a design file.

"""

class Builder:

    def __init__(self, objs, results, executor=None, loop=None, **kwargs):
        log = logging.getLogger("maloja.builder.Builder")
        self.plans = group_by_type(objs)
        self.results = results
        self.token = None
        self.seq = itertools.count(1)

    def __call__(self, session, token, callback=None, status=None, **kwargs):
        log = logging.getLogger("maloja.builder")

        # Debug
        op = session.get(self.plans[Template][0].href)
        done, not_done = concurrent.futures.wait(
            [op], timeout=6,
            return_when=concurrent.futures.FIRST_EXCEPTION
        )
        response = done.pop().result()
        log.debug(response.text)
        # End debug

        prototypes = self.plans[VApp] + self.plans[Template]
        data = {
            "appliance": {
                "name": prototypes[0].name,
                "description": "Created by Maloja builder",
                #"vms": self.plans[Vm],
                "vms": [],
            },
            "networks": self.plans[Network],
            "template": self.plans[Template][0]
        }

        macro = PageTemplateFile(
            pkg_resources.resource_filename(
                "maloja.workflow", "ComposeVAppParams.pt"
            )
        )

        url = "{vdc.href}/{endpoint}".format(
            vdc=self.plans[Vdc][0],
            endpoint="action/composeVApp"
        )
        xml = macro(**data)
        op = session.post(url, data=xml)
        session.headers.update(
            {"Content-Type": "application/vnd.vmware.vcloud.composeVAppParams+xml"}
        )

        done, not_done = concurrent.futures.wait(
            [op], timeout=6,
            return_when=concurrent.futures.FIRST_EXCEPTION
        )

        try:
            response = done.pop().result()
            if response.status_code == 400:
                if "DUPLICATE_NAME" in response.text:
                    log.warning("Request refused: duplicate name.")
        except Exception as e:
            log.error(e)

        if status:
            self.results.put((status, Stop()))

