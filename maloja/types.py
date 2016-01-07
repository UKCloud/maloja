#!/usr/bin/env python
#   -*- encoding: UTF-8 -*-

from collections import namedtuple

Credentials = namedtuple("Credentials", ["url", "user", "password"])
Design = namedtuple("Design", ["objects"])

Plugin = namedtuple(
    "Plugin",
    ["name", "description", "selector", "workflow"]
)
"""
This data structure describes a Maloja plugin. It is the type
expected by the `maloja.plugin` interface.

"""

Status = namedtuple("Status", ["id", "job", "level"])
Stop = namedtuple("Stop", [])
Survey = namedtuple("Survey", ["path"])
Token = namedtuple("Token", ["t", "url", "key", "value"])
Workflow = namedtuple("Workflow", ["plugin", "paths"])
