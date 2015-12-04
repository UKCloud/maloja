#!/usr/bin/env python
#   -*- encoding: UTF-8 -*-

from collections import namedtuple

Credentials = namedtuple("Credentials", ["url", "user", "password"])
Plugin = namedtuple("Plugin", ["name", "description", "selector", "workflow"])
Status = namedtuple("Status", ["id", "job", "level"])
Stop = namedtuple("Stop", [])
Survey = namedtuple("Survey", ["path"])
Token = namedtuple("Token", ["t", "url", "key", "value"])
