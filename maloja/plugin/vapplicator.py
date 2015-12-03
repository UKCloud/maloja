#!/usr/bin/env python
#   -*- encoding: UTF-8 -*-

from collections import namedtuple

Plugin = namedtuple("Plugin", ["name", "description", "selector"])

__doc__ = """
This is a demo plugin for Maloja.

It starts with an empty VApp and adds VMs to it.

"""

def selector(*objs):
    return True

plugin = Plugin(
    "vapplicator",
    __doc__,
    selector
)
