#!/usr/bin/env python
#   -*- encoding: UTF-8 -*-

from collections import defaultdict
from collections import namedtuple
from collections import OrderedDict
import concurrent.futures
import logging
import os.path
import uuid
import warnings

from maloja.model import Org
from maloja.model import Template
from maloja.model import Vdc
from maloja.model import Vm

from maloja.surveyor import Surveyor
from maloja.surveyor import yaml_loads

from maloja.types import Plugin

from maloja.workflow.path import Path

from chameleon import PageTemplateFile
import pkg_resources


__doc__ = """
This is a demo plugin for Maloja.

It starts with an empty VApp and adds VMs to it.

"""

def selector(*objs):
    """
    Your selector function accepts one or more objects from
    the Maloja :ref:`data model <data model>`.

    If these are not sufficient for the operation of your workflow,
    the function should return
    :py:class:`maloja.workflow.utils.Path` objects to indicate
    what is required to satisfy selection.

    Your function returns a Workflow class if the objects satisfy
    your selection criteria.
    """
    rv = []
    if not any(obj for obj in objs if isinstance(obj, Vdc)):
        rv.append(Path(None, None, None, None, None, None, None, "vdc.yaml"))
    if not any(obj for obj in objs if isinstance(obj, Vm)):
        rv.append(Path(None, None, None, None, None, None, None, "vm.yaml"))
    if not len([obj for obj in objs if isinstance(obj, Template)]):
        rv.append(Path(None, None, None, None, None, None, None, "template.yaml"))
    return rv or Workflow


class Workflow:

    def __init__(self, paths, results, executor=None, loop=None, **kwargs):
        """
        Initialise the workflow.

        """
        self.context = defaultdict(OrderedDict)
        self.results = results
        self.executor = executor

        """
        for path in paths:
            typ = Surveyor.patterns[os.path.splitext(path.file)[0]][0]
            fP = os.path.join(*(i for i in path if i is not None))
            with open(fP, "r") as data:
                obj = typ(**yaml_loads(data.read()))
                if obj is None:
                    continue
                else:
                    self.context[typ][obj] = path
        """

        # FIXME: Untested
        for path in paths:
            obj = found = None
            try:
                found, obj = next(find_ypath(path))
            except StopIteration:
                warnings.warn("Can't follow path {0}".format(path))
            else:
                if found != path:
                    warnings.warn("Path {0} led to {1}".format(path, found))
            finally:
                self.context[type(obj)][obj] = found

    def __call__(self, session, token, callback=None, status=None, **kwargs):
        """
        Perform the workflow.

        """
        log = logging.getLogger("maloja.plugin.vapplicator")
        log.debug(self.context)

        if type(None) in self.context:
            log.error("Workflow is misconfigured.")

        macro = PageTemplateFile(
            pkg_resources.resource_filename(
                "maloja.workflow", "InstantiateVAppTemplateParams.pt"
            )
        )

        template = list(self.context[Template].keys())[0]
        data = {
            "appliance": {
                "name": uuid.uuid4().hex,
                "description": "Created by Maloja vapplicator",
                "vms": [],
            },
            "networks": [],
            "template": {
                "name": template.name,
                "href": template.href
            }
        }

        url = "{vdc}/{endpoint}".format(
            vdc=list(self.context[Vdc].keys())[0].href,
            endpoint="action/instantiateVAppTemplate"
        )
        xml = macro(**data)
        op = session.post(
            url,
            data=xml
        )
        session.headers.update(
            {"Content-Type": "application/vnd.vmware.vcloud.instantiateVAppTemplateParams+xml"})

        log.debug(session.headers)
        log.debug(xml)
        done, not_done = concurrent.futures.wait(
            [op], timeout=3,
            return_when=concurrent.futures.FIRST_EXCEPTION
        )
        response = done.pop().result()
        log.info(response.status_code)

        if self.results and status:
            self.results.put((status, None))

plugin = Plugin(
    "vapplicator",
    __doc__,
    selector,
    Workflow
)
"""
This module-level variable provides the entry point to your plugin
script.

"""
