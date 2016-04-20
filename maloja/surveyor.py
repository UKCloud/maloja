#!/usr/bin/env python
#   -*- encoding: UTF-8 -*-

# Copyright Skyscape Cloud Services
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import concurrent.futures
import functools
import logging
import os
import os.path
import time
from urllib.parse import quote as urlquote
from urllib.parse import urlparse
import xml.etree.ElementTree as ET
import xml.sax.saxutils

from requests.exceptions import HTTPError

from maloja.model import Catalog
from maloja.model import Gateway
from maloja.model import Network
from maloja.model import Template
from maloja.model import Org
from maloja.model import VApp
from maloja.model import Vdc
from maloja.model import Vm
from maloja.model import yaml_dumps
from maloja.model import yaml_loads

import maloja.types
from maloja.types import Status
from maloja.types import Survey

from maloja.workflow.utils import find_xpath
from maloja.workflow.path import cache
from maloja.workflow.path import find_ypath
from maloja.workflow.path import split_to_path


class Surveyor:
    """
    The Surveyor is responsible for exploring a virtual infrastructure.
    It starts at Org level and finds networks and Edge Gateways. It
    descends down through vDCs, via catalogs and vApps to Vms.

    The Surveyor is a singleton; only one survey may run at a time.
    It is stateless; all necessary data is passed on from
    one task to the next, or else saved into YAML files.
    """

    @staticmethod
    def survey_handler(msg, session, token, callback=None, results=None, status=None, **kwargs):
        log = logging.getLogger("maloja.survey.handler")
        if msg.path.project and not any(msg.path[2:-1]):
            endpoints = [
                (
                    "api/org",
                    functools.partial(
                        Surveyor.on_org_list,
                        msg.path,
                        results=results,
                        status=status
                    )
                )
            ]
        else:
            endpoints = [
                ("api/catalogs/query", None)
            ]
        rv = []
        for endpoint, callback in endpoints:
            log.debug("Scheduling  GET to {0}".format(endpoint))
            url = "{url}:{port}/{endpoint}".format(
                url=token.url,
                port=443,
                endpoint=endpoint)

            headers = {
                "Accept": "application/*+xml;version=5.5",
                token.key: token.value,
            }
            session.headers.update(headers)
            rv.append(session.get(url, background_callback=callback))
        return rv


    @staticmethod
    def on_vmrecords(path, session, response, results=None, status=None):
        log = logging.getLogger("maloja.surveyor.on_vmrecords")

        ns = "{http://www.vmware.com/vcloud/v1.5}"
        tree = ET.fromstring(response.text)
        for elem in tree.iter(ns + "VMRecord"):
            obj = Vm().feed_xml(elem, ns=ns)
            path = path._replace(node=obj.name, file="vm.yaml")
            found, obj = next(find_ypath(path, obj), (None, obj))

            if found is not None:
                log.debug("Loaded existing object: {0}".format(vars(obj)))

            # Update the existing object with attributes from the VMRecord
            obj.feed_xml(elem, ns=ns)
            cache(path, obj)

            if results and status:
                results.put((status._replace(path=path), None))

    @staticmethod
    def on_vm(path, session, response, results=None, status=None):
        log = logging.getLogger("maloja.surveyor.on_vm")

        ns = "{http://www.vmware.com/vcloud/v1.5}"
        tree = ET.fromstring(response.text)
        path = path._replace(file="vm.yaml")
        obj = Vm()
        found, obj = next(find_ypath(path, obj), (None, obj))
        if found is not None:
            log.debug("Loaded existing object: {0}".format(vars(obj)))

        # Update the existing object with attributes from the VM
        obj.feed_xml(tree, ns=ns)
        cache(path, obj)

        if results and status:
            results.put((status._replace(path=path), None))

    @staticmethod
    def on_template(path, session, response, results=None, status=None):
        log = logging.getLogger("maloja.surveyor.on_template")

        tree = ET.fromstring(response.text)
        obj = Template().feed_xml(tree, ns="{http://www.vmware.com/vcloud/v1.5}")
        path = path._replace(file="template.yaml")
        cache(path, obj)

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
                status=status._replace(job=status.job + n) if status else None
            )
        ) for n, vm in enumerate(vms)]
        tasks = concurrent.futures.wait(
            ops, timeout=3 * len(ops),
            return_when=concurrent.futures.FIRST_EXCEPTION
        )
        if results and status:
            results.put((status._replace(path=path), None))

    @staticmethod
    def on_catalogitem(path, session, response, results=None, status=None):
        log = logging.getLogger("maloja.surveyor.on_catalogitem")

        templates = find_xpath(
            ".//*[@type='application/vnd.vmware.vcloud.vAppTemplate+xml']",
            ET.fromstring(response.text)
        )
        templates = list(templates)
        ops = [session.get(
            tmplt.attrib.get("href"),
            background_callback=functools.partial(
                Surveyor.on_template,
                path._replace(container=tmplt.attrib.get("name")),
                results=results,
                status=status._replace(job=status.job + n) if status else None
            )
        ) for n, tmplt in enumerate(templates)]
        tasks = concurrent.futures.wait(
            ops, timeout=3 * len(ops),
            return_when=concurrent.futures.FIRST_EXCEPTION
        )
        if results and status:
            results.put((status._replace(path=path), None))

    @staticmethod
    def on_edgeGateway(path, session, response, results=None, status=None):
        log = logging.getLogger("maloja.surveyor.on_edgeGateway")
        log.debug(path)

        obj = None
        ns = "{http://www.vmware.com/vcloud/v1.5}"
        tree = ET.fromstring(response.text)
        backoff = 5
        try:
            elem = next(tree.iter(ns + "EdgeGatewayRecord"))
            while True:
                op = session.get(elem.attrib.get("href"))
                done, not_done = concurrent.futures.wait(
                    [op], timeout=10,
                    return_when=concurrent.futures.FIRST_EXCEPTION
                )
                try:
                    response = done.pop().result()
                    if response.status_code != 200:
                        raise HTTPError(response.status_code)
                except (HTTPError, KeyError):
                    time.sleep(backoff)
                    backoff += 5
                else:
                    tree = ET.fromstring(response.text)
                    log.debug(response.text)
                    obj = Gateway().feed_xml(tree, ns=ns)
                    break

        except Exception as e:
            log.error(e)

        if obj is None:
            log.warning("Found no Edge Gateway.")
        else:
            path = path._replace(file="edge.yaml")
            fP = cache(path, obj)

        if results and status:
            results.put((status._replace(path=path), None))

    @staticmethod
    def on_orgVdcNetwork(path, session, response, results=None, status=None):
        log = logging.getLogger("maloja.surveyor.on_orgVdcNetwork")

        ns = "{http://www.vmware.com/vcloud/v1.5}"
        tree = ET.fromstring(response.text)
        backoff = 5
        try:
            for elem in tree.iter(ns + "OrgVdcNetworkRecord"):
                obj = None
                while True:
                    op = session.get(elem.attrib.get("href"))
                    done, not_done = concurrent.futures.wait(
                        [op], timeout=10,
                        return_when=concurrent.futures.FIRST_EXCEPTION
                    )
                    try:
                        response = done.pop().result()
                        if response.status_code != 200:
                            raise HTTPError(response.status_code)
                    except (HTTPError, KeyError):
                        time.sleep(backoff)
                        backoff += 5
                    else:
                        tree = ET.fromstring(response.text)
                        obj = Network().feed_xml(tree, ns=ns)
                        break

                if obj is not None:
                    path = path._replace(container=obj.name, file="network.yaml")
                    fP = cache(path, obj)

        except Exception as e:
            log.error(e)

        if results and status:
            results.put((status._replace(path=path), None))

    @staticmethod
    def on_vapp(path, session, response, results=None, status=None):
        log = logging.getLogger("maloja.surveyor.on_vapp")

        tree = ET.fromstring(response.text)
        obj = VApp().feed_xml(tree, ns="{http://www.vmware.com/vcloud/v1.5}")
        path = path._replace(file="vapp.yaml")
        fP = cache(path, obj)

        url = urlparse(response.url)
        query = "/".join((
            url.scheme + "://" + url.netloc,
            "api/vms/query?filter=(container=={0})".format(urlquote(response.url))
        ))
        vms = list(find_xpath(
            "./*/*/[@type='application/vnd.vmware.vcloud.vm+xml']",
            ET.fromstring(response.text)
        ))
        try:
            ops = [session.get(
                vm.attrib.get("href"),
                background_callback=functools.partial(
                    Surveyor.on_vm,
                    path._replace(node=vm.attrib.get("name")),
                    results=results,
                    status=status._replace(job=status.job + n) if status else None
                )
            ) for n, vm in enumerate(vms)] + [session.get(
                query,
                background_callback=functools.partial(
                    Surveyor.on_vmrecords,
                    path,
                    results=results,
                    status=status._replace(job=status.job + len(vms) + 1) if status else None
                )
            )]
        except Exception as e:
            log.error(e)
        tasks = concurrent.futures.wait(
            ops, timeout=3 * len(ops),
            return_when=concurrent.futures.FIRST_EXCEPTION
        )
        if results and status:
            results.put((status._replace(path=path), None))

    @staticmethod
    def on_vdc(path, session, response, results=None, status=None):
        log = logging.getLogger("maloja.surveyor.on_vdc")

        tree = ET.fromstring(response.text)
        obj = Vdc().feed_xml(tree, ns="{http://www.vmware.com/vcloud/v1.5}")
        path = path._replace(file="vdc.yaml")
        cache(path, obj)

        edgeGWs = find_xpath(
            "./*/[@type='application/vnd.vmware.vcloud.query.records+xml']",
            tree,
            rel="edgeGateways"
        )

        orgVdcNets = find_xpath(
            "./*/[@type='application/vnd.vmware.vcloud.query.records+xml']",
            tree,
            rel="orgVdcNetworks"
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
                status=status._replace(job=status.job + n) if status else None
            )
        ) for n, edgeGW in enumerate(edgeGWs)] + [session.get(
            orgVdcNet.attrib.get("href"),
            background_callback=functools.partial(
                Surveyor.on_orgVdcNetwork,
                path._replace(
                    category="networks",
                    container=orgVdcNet.attrib.get("name")
                ),
                results=results,
                status=status._replace(job=status.job + n) if status else None
            )
        ) for n, orgVdcNet in enumerate(orgVdcNets)] + [session.get(
            vapp.attrib.get("href"),
            background_callback=functools.partial(
                Surveyor.on_vapp,
                path._replace(
                    category="vapps",
                    container=vapp.attrib.get("name")
                ),
                results=results,
                status=status._replace(job=status.job + n) if status else None
            )
        ) for n, vapp in enumerate(vapps)]

        tasks = concurrent.futures.wait(
            ops, timeout=3 * len(ops),
            return_when=concurrent.futures.FIRST_EXCEPTION
        )
        if results and status:
            results.put((status._replace(path=path), None))

    @staticmethod
    def on_catalog(path, session, response, results=None, status=None):
        log = logging.getLogger("maloja.surveyor.on_catalog")

        tree = ET.fromstring(response.text)
        obj = Catalog().feed_xml(tree, ns="{http://www.vmware.com/vcloud/v1.5}")
        path = path._replace(file="catalog.yaml")
        cache(path, obj)

        items = find_xpath(
            ".//*[@type='application/vnd.vmware.vcloud.catalogItem+xml']",
            ET.fromstring(response.text)
        )
        ops = [session.get(
            item.attrib.get("href"),
            background_callback=functools.partial(
                Surveyor.on_catalogitem, path,
                results=results,
                status=status._replace(job=status.job + n) if status else None
            )
        ) for n, item in enumerate(items)]
        tasks = concurrent.futures.wait(
            ops, timeout=3 * len(ops),
            return_when=concurrent.futures.FIRST_EXCEPTION
        )
        if results and status:
            results.put((status._replace(path=path), None))

    @staticmethod
    def on_org(path, session, response, results=None, status=None):
        log = logging.getLogger("maloja.surveyor.on_org")

        tree = ET.fromstring(response.text)
        obj = Org().feed_xml(tree, ns="{http://www.vmware.com/vcloud/v1.5}")
        path = path._replace(file="org.yaml")
        fP = cache(path, obj)

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
                path._replace(service=vdc.attrib.get("name")),
                results=results,
                status=status._replace(job=status.job + n) if status else None
            )
        ) for n, vdc in enumerate(vdcs)] + [session.get(
            ctlg.attrib.get("href"),
            background_callback=functools.partial(
                Surveyor.on_catalog,
                path._replace(
                    service="catalogs",
                    category=ctlg.attrib.get("name")
                ),
                results=results,
                status=status._replace(job=status.job + n) if status else None
            )
        ) for n, ctlg in enumerate(ctlgs)]

        tasks = concurrent.futures.wait(
            ops, timeout=3 * len(ops),
            return_when=concurrent.futures.FIRST_EXCEPTION
        )
        if results and status:
            results.put((status._replace(path=path), None))

    @staticmethod
    def on_org_list(path, session, response, results=None, status=None):
        log = logging.getLogger("maloja.surveyor.on_org_list")

        tree = ET.fromstring(response.text)
        orgs = find_xpath(
            "./*/[@type='application/vnd.vmware.vcloud.org+xml']", tree)
        ops = [session.get(
            org.attrib.get("href"),
            background_callback=functools.partial(
                Surveyor.on_org,
                path._replace(org=org.attrib.get("name")),
                results=results,
                status=status._replace(job=status.job + n) if status else None
            )
        ) for n, org in enumerate(orgs)]
        tasks = concurrent.futures.wait(
            ops, timeout=3 * len(ops),
            return_when=concurrent.futures.FIRST_EXCEPTION
        )
        if results and status:
            results.put((status._replace(path=path), None))
