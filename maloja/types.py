#!/usr/bin/env python
#   -*- encoding: UTF-8 -*-

from collections import namedtuple

App = namedtuple("App", ["name", "type", "href"])
Catalog = namedtuple("Catalog", ["name", "type", "href", "dateCreated"])
Node = namedtuple("Node", ["name", "type", "href"])
Org = namedtuple("Org", ["name", "type", "href", "fullName"])
Template = namedtuple("Template", ["name", "type", "href", "dateCreated"])
Vdc = namedtuple("Vdc", ["name", "type", "href", "description"])
