#!/usr/bin/env python
#   -*- encoding: UTF-8 -*-

from collections import defaultdict
from collections import namedtuple
from collections import OrderedDict
import logging
import os.path

from maloja.model import Template
from maloja.model import Vm
from maloja.surveyor import Surveyor
from maloja.surveyor import yaml_loads
from maloja.types import Plugin
from maloja.workflow.utils import Path

from chameleon import PageTemplateFile
import pkg_resources


__doc__ = """
This is a demo plugin for Maloja.

It starts with an empty VApp and adds VMs to it.

"""

def selector(*objs):
    """
    Returns Paths while any are required to satisfy selection.

    Returns Workflow class if objs satisfy selection criteria.
    """
    rv = []
    if not any(obj for obj in objs if isinstance(obj, Vm)):
        rv.append(Path(None, None, None, None, None, None, "vm.yaml"))
    if not len([obj for obj in objs if isinstance(obj, Template)]):
        rv.append(Path(None, None, None, None, None, None, "template.yaml"))
    return rv or Workflow
        

class Workflow:

    def __init__(self, paths, results, executor=None, loop=None, **kwargs):
        self.context = defaultdict(OrderedDict)
        self.results = results
        self.executor = executor

        for path in paths:
            typ = Surveyor.patterns[os.path.splitext(path.file)[0]][0]
            fP = os.path.join(*(i for i in path if not i is None))
            with open(fP, "r") as data:
                obj = typ(**yaml_loads(data.read()))
                if obj is None:
                    continue
                else:
                    self.context[typ][obj] = path

    def __call__(self, session, token, callback=None, status=None, **kwargs):
        log = logging.getLogger("maloja.plugin.vapplicator")
        log.debug(self.context)

        macro = PageTemplateFile(
            pkg_resources.resource_filename(
                "maloja.workflow", "ComposeVAppParams.pt"
            )
        )

        template = next(iter(self.context[Template]), None)
        if template is not None:
            data = {
                "appliance": {
                    "name": "My Test VM",
                    "description": "This VM is for testing",
                    "vms": [],
                },
                "networks": [],
                "template": {
                    "name": template.name,
                    "href": template.href
                }
            }

        xml = macro(**data)
        if self.results and status:
            self.results.put((status, None))

plugin = Plugin(
    "vapplicator",
    __doc__,
    selector,
    Workflow
)
