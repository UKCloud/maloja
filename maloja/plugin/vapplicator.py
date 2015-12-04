#!/usr/bin/env python
#   -*- encoding: UTF-8 -*-

from collections import namedtuple

from maloja.model import Template
from maloja.model import Vm
from maloja.workflow.utils import Path

Plugin = namedtuple("Plugin", ["name", "description", "selector", "workflow"])

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
        self.paths = paths  # TODO: Formulate tasks
        self.results = results
        self.executor = executor

    def __call__(self, session, token, callback=None, status=None, **kwargs):
        pass

plugin = Plugin(
    "vapplicator",
    __doc__,
    selector,
    Workflow
)
