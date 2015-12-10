#!/usr/bin/env python
#   -*- encoding: UTF-8 -*-

from collections import defaultdict
from collections import namedtuple
import concurrent.futures
import functools
import logging
import os
import os.path
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

import maloja.types
from maloja.types import Status

from maloja.workflow.utils import split_to_path


def find_xpath(xpath, tree, namespaces={}, **kwargs):
    elements = tree.iterfind(xpath, namespaces=namespaces)
    if not kwargs:
        return elements
    else:
        query = set(kwargs.items())
        return (i for i in elements if query.issubset(set(i.attrib.items())))


def filter_records(*args, root="", key="", value=""):
    """
    Reads files from the argument list, turns them into objects and yields
    those which match key, value criteria.

    Matching of attributes flattens the object hierarchy. Attributes at the top
    level of the object take precedence over those with the same name further
    down in its children.

    Return values are 2-tuples of object and path.

    """
    for fP in args:
        path = split_to_path(fP, root)
        name = os.path.splitext(path.file)[0]
        try:
            typ, pattern = Surveyor.patterns[name]
        except KeyError:
            continue

        with open(fP, 'r') as data:
            obj = typ(**yaml_loads(data.read()))
            if obj is None:
                continue
            if not key:
                yield (obj, path)
                continue
            else:
                data = dict(
                    [(k, getattr(item, k))
                    for seq in [
                        i for i in vars(obj).values() if isinstance(i, list)
                    ]
                    for item in seq
                    for k in getattr(item, "_fields", [])],
                    **vars(obj)
                )
                match = data.get(key.strip(), "")
                if value.strip() in str(match):
                    yield (obj, path)


class Surveyor:

    patterns = {
        "org": (Org, "*/org.yaml"),
        "catalog": (Catalog, "*/*/catalog.yaml"),
        "vdc": (Vdc, "*/*/vdc.yaml"),
        "vapp": (VApp, "*/*/*/vapp.yaml"),
        "template": (Template, "*/*/*/template.yaml"),
        "vm": (Vm, "*/*/*/*/vm.yaml"),
    }

    locks = defaultdict(threading.Lock)

    @staticmethod
    def on_vmrecords(path, session, response, results=None, status=None):
        log = logging.getLogger("maloja.surveyor.on_vmrecords")

        ns = "{http://www.vmware.com/vcloud/v1.5}"
        tree = ET.fromstring(response.text)
        for elem in tree.iter(ns + "VMRecord"):
            obj = Vm().feed_xml(elem, ns=ns)
            try:
                path = path._replace(node=obj.name, file="vm.yaml")
                os.makedirs(
                    os.path.join(
                        path.root, path.project, path.org, path.dc,
                        path.app, path.node
                    ),
                    exist_ok=True
                )
                fP = os.path.join(
                    path.root, path.project, path.org,
                    path.dc, path.app, path.node, path.file
                )
            except TypeError:
                log.error("Insufficient data from {0}".format(elem.attrib.get("href", "?")))
                continue

            try:
                Surveyor.locks[path].acquire()
                if os.path.isfile(fP):
                    with open(fP, "r") as input_:
                        data = yaml_loads(input_.read())
                        obj = Vm(**data).feed_xml(elem, ns=ns)
                        log.debug("Loaded existing object: {0}".format(vars(obj)))

                with open(fP, "w") as output:
                    data = yaml_dumps(obj)
                    output.write(data)
                    output.flush()
            except Exception as e:
                log.error(e)
            finally:
                Surveyor.locks[path].release()

        if results and status:
            results.put((status, None))

    @staticmethod
    def on_vm(path, session, response, results=None, status=None):
        log = logging.getLogger("maloja.surveyor.on_vm")
        if status:
            child = status._replace(level=status.level + 1)
        else:
            child = Status(1, 1, 1)

        ns = "{http://www.vmware.com/vcloud/v1.5}"
        tree = ET.fromstring(response.text)
        path = path._replace(file="vm.yaml")
        os.makedirs(
            os.path.join(
                path.root, path.project, path.org, path.dc,
                path.app, path.node
            ),
            exist_ok=True
        )
        fP = os.path.join(
            path.root, path.project, path.org,
            path.dc, path.app, path.node, path.file
        )
        try:
            Surveyor.locks[path].acquire()
            if os.path.isfile(fP):
                with open(fP, "r") as input_:
                    data = yaml_loads(input_.read())
                    obj = Vm(**data)
                    log.debug("Loaded existing object: {0}".format(vars(obj)))
            else:
                obj = Vm()

            obj.feed_xml(tree, ns=ns)
            with open(fP, "w") as output:
                data = yaml_dumps(obj)
                output.write(data)
                output.flush()
        except Exception as e:
            log.error(e)
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

        tree = ET.fromstring(response.text)
        obj = Template().feed_xml(tree, ns="{http://www.vmware.com/vcloud/v1.5}")
        path = path._replace(file="template.yaml")
        os.makedirs(os.path.join(path.root, path.project, path.org, path.dc, path.app), exist_ok=True)
        try:
            Surveyor.locks[path].acquire()
            with open(
                os.path.join(path.root, path.project, path.org, path.dc, path.app, path.file), "w"
            ) as output:
                try:
                    data = yaml_dumps(obj)
                except Exception as e:
                    log.error(e)
                output.write(data)
                output.flush()
        finally:
            Surveyor.locks[path].release()

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

        templates = find_xpath(
            ".//*[@type='application/vnd.vmware.vcloud.vAppTemplate+xml']",
            ET.fromstring(response.text)
        )
        templates = list(templates)
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
    def on_edgeGateway(path, session, response, results=None, status=None):
        log = logging.getLogger("maloja.surveyor.on_edgeGateway")
        if status:
            child = status._replace(level=status.level + 1)
        else:
            child = Status(1, 1, 1)
        log.debug(response.text)
        if results and status:
            results.put((status, None))


    @staticmethod
    def on_vapp(path, session, response, results=None, status=None):
        log = logging.getLogger("maloja.surveyor.on_vapp")
        if status:
            child = status._replace(level=status.level + 1)
        else:
            child = Status(1, 1, 1)

        tree = ET.fromstring(response.text)
        obj = VApp().feed_xml(tree, ns="{http://www.vmware.com/vcloud/v1.5}")
        path = path._replace(file="vapp.yaml")
        os.makedirs(os.path.join(path.root, path.project, path.org, path.dc, path.app), exist_ok=True)
        try:
            Surveyor.locks[path].acquire()
            with open(
                os.path.join(path.root, path.project, path.org, path.dc, path.app, path.file), "w"
            ) as output:
                try:
                    data = yaml_dumps(obj)
                except Exception as e:
                    log.error(e)
                output.write(data)
                output.flush()
        finally:
            Surveyor.locks[path].release()

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

        tree = ET.fromstring(response.text)
        obj = Vdc().feed_xml(tree, ns="{http://www.vmware.com/vcloud/v1.5}")
        path = path._replace(file="vdc.yaml")
        os.makedirs(os.path.join(path.root, path.project, path.org, path.dc), exist_ok=True)
        try:
            Surveyor.locks[path].acquire()
            with open(
                os.path.join(path.root, path.project, path.org, path.dc, path.file), "w"
            ) as output:
                try:
                    data = yaml_dumps(obj)
                except Exception as e:
                    log.error(e)
                output.write(data)
                output.flush()
        finally:
            Surveyor.locks[path].release()

        edgeGWs = find_xpath(
            "./*/[@type='application/vnd.vmware.vcloud.query.records+xml']",
            tree,
            rel="edgeGateways"
        )

        vapps = find_xpath(
            "./*/*/[@type='application/vnd.vmware.vcloud.vApp+xml']",
            tree
        )
        ops = [session.get(
            edgeGW.attrib.get("href"),
            background_callback=functools.partial(
                Surveyor.on_edgeGateway,
                path,
                results=results,
                status=child._replace(job=child.job + n)
            )
        ) for n, edgeGW in enumerate(edgeGWs)] + [
            session.get(
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

        tree = ET.fromstring(response.text)
        obj = Catalog().feed_xml(tree, ns="{http://www.vmware.com/vcloud/v1.5}")
        path = path._replace(file="catalog.yaml")
        os.makedirs(os.path.join(path.root, path.project, path.org, path.dc), exist_ok=True)
        try:
            Surveyor.locks[path].acquire()
            with open(
                os.path.join(path.root, path.project, path.org, path.dc, path.file), "w"
            ) as output:
                try:
                    data = yaml_dumps(obj)
                except Exception as e:
                    log.error(e)
                output.write(data)
                output.flush()
        finally:
            Surveyor.locks[path].release()

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

        tree = ET.fromstring(response.text)
        obj = Org().feed_xml(tree, ns="{http://www.vmware.com/vcloud/v1.5}")
        path = path._replace(file="org.yaml")
        os.makedirs(os.path.join(path.root, path.project, path.org), exist_ok=True)
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
