#!/usr/bin/env python
#   -*- encoding: UTF-8 -*-

from collections import defaultdict
from collections import namedtuple
import concurrent.futures
import functools
import logging
import os
import threading
from urllib.parse import quote as urlquote
from urllib.parse import urlparse
import xml.etree.ElementTree as ET
import xml.sax.saxutils

from maloja.model import Catalog
from maloja.model import Template
from maloja.model import Org
from maloja.model import VApp
from maloja.model import Vdc
from maloja.model import Vm
from maloja.model import yaml_dumps
from maloja.model import yaml_loads
from maloja.builder import find_xpath

import maloja.types
from maloja.types import Status


class Builder:

    @staticmethod
    def on_vmrecords(path, session, response, results=None, status=None):
        log = logging.getLogger("maloja.builder.on_vmrecords")
        if results and status:
            results.put((status, None))

    @staticmethod
    def on_vm(path, session, response, results=None, status=None):
        log = logging.getLogger("maloja.builder.on_vm")
        if results and status:
            results.put((status, None))

    @staticmethod
    def on_template(path, session, response, results=None, status=None):
        log = logging.getLogger("maloja.builder.on_template")
        if results and status:
            results.put((status, None))

    @staticmethod
    def on_catalogitem(path, session, response, results=None, status=None):
        log = logging.getLogger("maloja.builder.on_catalogitem")
        if results and status:
            results.put((status, None))

    @staticmethod
    def on_vapp(path, session, response, results=None, status=None):
        log = logging.getLogger("maloja.builder.on_vapp")
        if results and status:
            results.put((status, None))

    @staticmethod
    def on_vdc(path, session, response, results=None, status=None):
        log = logging.getLogger("maloja.builder.on_vdc")
        if results and status:
            results.put((status, None))

    @staticmethod
    def on_catalog(path, session, response, results=None, status=None):
        log = logging.getLogger("maloja.builder.on_catalog")
        if results and status:
            results.put((status, None))

    @staticmethod
    def on_org(path, session, response, results=None, status=None):
        log = logging.getLogger("maloja.builder.on_org")
        if results and status:
            results.put((status, None))

    @staticmethod
    def on_org_list(path, session, response, results=None, status=None):
        log = logging.getLogger("maloja.builder.on_org_list")
        if results and status:
            results.put((status, None))
