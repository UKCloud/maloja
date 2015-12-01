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

import ruamel.yaml

from maloja.model import App
from maloja.model import Catalog
from maloja.model import Template
from maloja.model import Org
from maloja.model import Vdc
from maloja.model import Vm
from maloja.model import yaml_dumps
from maloja.model import yaml_loads

import maloja.types
from maloja.types import Status


def find_xpath(xpath, tree, namespaces={}, **kwargs):
    elements = tree.iterfind(xpath, namespaces=namespaces)
    if not kwargs:
        return elements
    else:
        query = set(kwargs.items())
        return (i for i in elements if query.issubset(set(i.attrib.items())))


def survey_loads(xml, types={}):
    namespace = "{http://www.vmware.com/vcloud/v1.5}"
    tree = ET.fromstring(xml)
    typ = (types or {
        namespace + "VApp": App,
        namespace + "Catalog": Catalog,
        namespace + "Vm": Vm,
        namespace + "Org": Org,
        namespace + "VAppTemplate": Template,
        namespace + "Vdc": Vdc
    }).get(tree.tag)
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

    locks = defaultdict(threading.Lock)

    @staticmethod
    def on_vmrecords(path, session, response, results=None, status=None):
        log = logging.getLogger("maloja.surveyor.on_vmrecords")

        log.debug(response.status_code)
        log.debug(response.text)
        if results and status:
            results.put((status, None))

    @staticmethod
    def on_vm(path, session, response, results=None, status=None):
        log = logging.getLogger("maloja.surveyor.on_vm")
        if status:
            child = status._replace(level=status.level + 1)
        else:
            child = Status(1, 1, 1)

        log.info(response.text)
        os.makedirs(
            os.path.join(
                path.root, path.project, path.org, path.dc,
                path.app, path.node
            ),
            exist_ok=True
        )
        for obj in survey_loads(response.text):
            path = path._replace(file="node.yaml")
            try:
                Surveyor.locks[path].acquire()
                with open(
                    os.path.join(
                        path.root, path.project, path.org, path.dc,
                        path.app, path.node, path.file
                    ), "w"
                ) as output:
                    output.write(yaml_dumps(obj))
                    output.flush()
            finally:
                Surveyor.locks[path].release()

        if results and status:
            results.put((status, None))

    @staticmethod
    def on_template(path, session, response, results=None, status=None):
        log = logging.getLogger("maloja.surveyor.on_template")
        if status:
            child = status._replace(level=status.level + 1)
        else:
            child = Status(1, 1, 1)

        os.makedirs(os.path.join(path.root, path.project, path.org, path.dc, path.app), exist_ok=True)
        for obj in survey_loads(response.text):
            path = path._replace(file="{0}.yaml".format(type(obj).__name__.lower()))
            with open(
                os.path.join(path.root, path.project, path.org, path.dc, path.app, path.file), "w"
            ) as output:
                output.write(yaml_dumps(obj))
                output.flush()

        vms = find_xpath(
            "./*/*/[@type='application/vnd.vmware.vcloud.vm+xml']",
            ET.fromstring(response.text)
        )
        ops = [session.get(
            vm.attrib.get("href"),
            background_callback=functools.partial(
                Surveyor.on_vm,
                path._replace(node=vm.attrib.get("name")),
                results=results,
                status=child._replace(job=child.job + n)
            )
        ) for n, vm in enumerate(vms)]
        tasks = concurrent.futures.wait(
            ops, timeout=3 * len(ops),
            return_when=concurrent.futures.FIRST_EXCEPTION
        )
        if results and status:
            results.put((status, None))

    @staticmethod
    def on_catalogitem(path, session, response, results=None, status=None):
        log = logging.getLogger("maloja.surveyor.on_catalogitem")
        if status:
            child = status._replace(level=status.level + 1)
        else:
            child = Status(1, 1, 1)
        log.debug(path)

        templates = find_xpath(
            ".//*[@type='application/vnd.vmware.vcloud.vAppTemplate+xml']",
            ET.fromstring(response.text)
        )
        templates = list(templates)
        log.debug(templates)
        ops = [session.get(
            tmplt.attrib.get("href"),
            background_callback=functools.partial(
                Surveyor.on_template,
                path._replace(app=tmplt.attrib.get("name")),
                results=results,
                status=child._replace(job=child.job + n)
            )
        ) for n, tmplt in enumerate(templates)]
        tasks = concurrent.futures.wait(
            ops, timeout=3 * len(ops),
            return_when=concurrent.futures.FIRST_EXCEPTION
        )
        if results and status:
            results.put((status, None))

    @staticmethod
    def on_vapp(path, session, response, results=None, status=None):
        log = logging.getLogger("maloja.surveyor.on_vapp")
        if status:
            child = status._replace(level=status.level + 1)
        else:
            child = Status(1, 1, 1)

        os.makedirs(os.path.join(path.root, path.project, path.org, path.dc, path.app), exist_ok=True)
        for obj in survey_loads(response.text):
            path = path._replace(file="{0}.yaml".format(type(obj).__name__.lower()))
            with open(
                os.path.join(path.root, path.project, path.org, path.dc, path.app, path.file), "w"
            ) as output:
                output.write(yaml_dumps(obj))
                output.flush()

        url = urlparse(response.url)
        query = "/".join((
            url.scheme + "://" + url.netloc,
            "api/vms/query?filter=(container=={0})".format(urlquote(response.url))
        ))
        vms = find_xpath(
            "./*/*/[@type='application/vnd.vmware.vcloud.vm+xml']",
            ET.fromstring(response.text)
        )
        try:
            ops = [session.get(
                vm.attrib.get("href"),
                background_callback=functools.partial(
                    Surveyor.on_vm,
                    path._replace(node=vm.attrib.get("name")),
                    results=results,
                    status=child._replace(job=child.job + n)
                )
            ) for n, vm in enumerate(vms)] + [session.get(
                query,
                background_callback=functools.partial(
                    Surveyor.on_vmrecords,
                    path,
                    results=results,
                    status=status._replace(id=status.id + 1, job=status.job + 1)
                )
            )]
        except Exception as e:
            log.error(e)
        tasks = concurrent.futures.wait(
            ops, timeout=3 * len(ops),
            return_when=concurrent.futures.FIRST_EXCEPTION
        )
        if results and status:
            results.put((status, None))

    @staticmethod
    def on_vdc(path, session, response, results=None, status=None):
        log = logging.getLogger("maloja.surveyor.on_vdc")
        if status:
            child = status._replace(level=status.level + 1)
        else:
            child = Status(1, 1, 1)

        os.makedirs(os.path.join(path.root, path.project, path.org, path.dc), exist_ok=True)
        for obj in survey_loads(response.text):
            path = path._replace(file="{0}.yaml".format(type(obj).__name__.lower()))
            with open(
                os.path.join(path.root, path.project, path.org, path.dc, path.file), "w"
            ) as output:
                output.write(yaml_dumps(obj))
                output.flush()

        vapps = find_xpath(
            "./*/*/[@type='application/vnd.vmware.vcloud.vApp+xml']",
            ET.fromstring(response.text)
        )
        ops = [session.get(
            vapp.attrib.get("href"),
            background_callback=functools.partial(
                Surveyor.on_vapp,
                path._replace(app=vapp.attrib.get("name")),
                results=results,
                status=child._replace(job=child.job + n)
            )
        ) for n, vapp in enumerate(vapps)]
        tasks = concurrent.futures.wait(
            ops, timeout=3 * len(ops),
            return_when=concurrent.futures.FIRST_EXCEPTION
        )
        if results and status:
            results.put((status, None))

    @staticmethod
    def on_catalog(path, session, response, results=None, status=None):
        log = logging.getLogger("maloja.surveyor.on_catalog")
        if status:
            child = status._replace(level=status.level + 1)
        else:
            child = Status(1, 1, 1)

        for obj in survey_loads(response.text):
            path = path._replace(file="{0}.yaml".format(type(obj).__name__.lower()))
            os.makedirs(os.path.join(path.root, path.project, path.org, path.dc), exist_ok=True)
            with open(
                os.path.join(path.root, path.project, path.org, path.dc, path.file), "w"
            ) as output:
                output.write(yaml_dumps(obj))
                output.flush()

        items = find_xpath(
            ".//*[@type='application/vnd.vmware.vcloud.catalogItem+xml']",
            ET.fromstring(response.text)
        )
        ops = [session.get(
            item.attrib.get("href"),
            background_callback=functools.partial(
                Surveyor.on_catalogitem, path,
                results=results,
                status=child._replace(job=child.job + n)
            )
        ) for n, item in enumerate(items)]
        tasks = concurrent.futures.wait(
            ops, timeout=3 * len(ops),
            return_when=concurrent.futures.FIRST_EXCEPTION
        )
        if results and status:
            results.put((status, None))

    @staticmethod
    def on_org(path, session, response, results=None, status=None):
        log = logging.getLogger("maloja.surveyor.on_org")
        if status:
            child = status._replace(level=status.level + 1)
        else:
            child = Status(1, 1, 1)

        os.makedirs(os.path.join(path.root, path.project, path.org), exist_ok=True)
        log.debug("Hi")
        for obj in survey_loads(response.text):
            path = path._replace(file="{0}.yaml".format(type(obj).__name__.lower()))
            try:
                Surveyor.locks[path].acquire()
                with open(
                    os.path.join(path.root, path.project, path.org, path.file), "w"
                ) as output:
                    try:
                        data = yaml_dumps(obj)
                    except Exception as e:
                        log.error(e)
                    output.write(data)
                    output.flush()
            finally:
                Surveyor.locks[path].release()

        ctlgs = find_xpath(
            "./*/[@type='application/vnd.vmware.vcloud.catalog+xml']",
            ET.fromstring(response.text)
        )

        vdcs = find_xpath(
            "./*/[@type='application/vnd.vmware.vcloud.vdc+xml']",
            ET.fromstring(response.text)
        )
        ops = [session.get(
            vdc.attrib.get("href"),
            background_callback=functools.partial(
                Surveyor.on_vdc,
                path._replace(dc=vdc.attrib.get("name")),
                results=results,
                status=child._replace(job=child.job + n)
            )
        ) for n, vdc in enumerate(vdcs)] + [
            session.get(
            ctlg.attrib.get("href"),
            background_callback=functools.partial(
                Surveyor.on_catalog,
                path._replace(dc=ctlg.attrib.get("name")),
                results=results,
                status=child._replace(job=child.job + n)
            )
        ) for n, ctlg in enumerate(ctlgs)]

        tasks = concurrent.futures.wait(
            ops, timeout=3 * len(ops),
            return_when=concurrent.futures.FIRST_EXCEPTION
        )
        if results and status:
            results.put((status, None))

    @staticmethod
    def on_org_list(path, session, response, results=None, status=None):
        log = logging.getLogger("maloja.surveyor.on_org_list")
        if status:
            child = status._replace(level=status.level + 1)
        else:
            child = Status(1, 1, 1)

        tree = ET.fromstring(response.text)
        orgs = find_xpath(
            "./*/[@type='application/vnd.vmware.vcloud.org+xml']", tree)
        ops = [session.get(
            org.attrib.get("href"),
            background_callback=functools.partial(
                Surveyor.on_org,
                path._replace(org=org.attrib.get("name")),
                results=results,
                status=child._replace(job=child.job + n)
            )
        ) for n, org in enumerate(orgs)]
        tasks = concurrent.futures.wait(
            ops, timeout=3 * len(ops),
            return_when=concurrent.futures.FIRST_EXCEPTION
        )
        if results and status:
            results.put((status, None))
