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

        template = self.plans[Template][0]
        data = {
            "appliance": {
                "name": uuid.uuid4().hex,
                "description": "Created by Maloja builder",
                "vms": [],
            },
            "networks": [],
            "template": {
                "name": template.name,
                "href": template.href
            }
        }

        macro = PageTemplateFile(
            pkg_resources.resource_filename(
                "maloja.workflow", "ComposeVAppParams.pt"
            )
        )

        xml = macro(**data)
        log.debug(xml)
        if status:
            self.results.put((status, Stop()))

