#!/usr/bin/env python
#   -*- encoding: UTF-8 -*-

import concurrent.futures
import functools
import logging
import os
import xml.etree.ElementTree as ET
import xml.sax.saxutils

import ruamel.yaml

import maloja.types
from maloja.workflow.utils import record

def find_xpath(xpath, tree, namespaces={}, **kwargs):
    elements = tree.iterfind(xpath, namespaces=namespaces)
    if not kwargs:
        return elements
    else:
        query = set(kwargs.items())
        return (i for i in elements if query.issubset(set(i.attrib.items())))

def survey_loads(xml):
    namespace = "{http://www.vmware.com/vcloud/v1.5}"
    tree = ET.fromstring(xml)
    typ = {
        namespace + "Org": maloja.types.Org,
        namespace + "Vdc": maloja.types.Vdc
    }.get(tree.tag)
    attribs = (tree.attrib.get(f, None) for f in typ._fields)
    body = (
        item.text if item is not None else None
        for item in [
            tree.find(namespace + f[0].capitalize() + f[1:]) for f in typ._fields
        ]
    )
    data = (b if b is not None else a for a, b in zip(attribs, body))
    yield typ(*data)

class Surveyor:

    @staticmethod
    def on_org(path, session, response):
        log = logging.getLogger("maloja.surveyor.on_org")
        os.makedirs(os.path.join(path.root, path.project, path.org), exist_ok=True)
        # survey_loads(response.text)
        tree = ET.fromstring(response.text)
        # TODO: Inline
        data = {}
        namespace = "{http://www.vmware.com/vcloud/v1.5}"
        permitted = {i.lower(): i for i in maloja.types.Org._fields}
        for item in tree:
            key = item.tag.replace(namespace, "").lower()
            field = permitted.pop(key, None)
            log.debug(field)
            if field is not None:
                data[field] = item.text
        org = maloja.types.Org(**data)

        log.debug(org)
        path = path._replace(file="org.yaml")
        with record(
            path.file,
            parent=os.path.join(path.root, path.project, path.org)
        ) as output:
            output.write(ruamel.yaml.dump(org))
            output.flush()

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
