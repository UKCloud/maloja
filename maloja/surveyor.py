#!/usr/bin/env python
#   -*- encoding: UTF-8 -*-

import concurrent.futures
import functools
import logging
import os
import xml.etree.ElementTree as ET
import xml.sax.saxutils

def find_xpath(xpath, tree, namespaces={}, **kwargs):
    elements = tree.iterfind(xpath, namespaces=namespaces)
    if not kwargs:
        return elements
    else:
        query = set(kwargs.items())
        return (i for i in elements if query.issubset(set(i.attrib.items())))

class Surveyor:

    @staticmethod
    def on_org(path, session, response):
        log = logging.getLogger("maloja.surveyor.on_org")
        os.makedirs(os.path.join(path.root, path.project, path.org), exist_ok=True)
        tree = ET.fromstring(response.text)
        log.debug(tree)

    @staticmethod
    def on_org_list(path, session, response):
        log = logging.getLogger("maloja.surveyor.on_org_list")
        tree = ET.fromstring(response.text)
        orgs = find_xpath(
            "./*/[@type='application/vnd.vmware.vcloud.org+xml']", tree)
        ops = [session.get(
            org.attrib.get("href"),
            background_callback=functools.partial(
                Surveyor.on_org,
                path._replace(org=org.attrib.get("name"))
            )
        ) for org in orgs]
        log.debug(ops)
        results = concurrent.futures.wait(
            ops, timeout=3 * len(ops),
            return_when=concurrent.futures.FIRST_EXCEPTION
        )
