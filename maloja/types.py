#!/usr/bin/env python
#   -*- encoding: UTF-8 -*-

from collections import namedtuple

Credentials = namedtuple("Credentials", ["url", "user", "password"])
Design = namedtuple("Design", ["objects"])

Plugin = namedtuple(
    "Plugin",
    ["name", "description", "selector", "workflow"]
)
Plugin.__doc__ = """`{}`
Represents a plugin module. The first two attributes of this class
provide information to the user on the nature of the plugin.
""".format(Plugin.__doc__)

Status = namedtuple("Status", ["id", "job", "level"])
Stop = namedtuple("Stop", [])
Survey = namedtuple("Survey", ["path"])
Token = namedtuple("Token", ["t", "url", "key", "value"])
Workflow = namedtuple("Workflow", ["plugin", "paths"])
