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

from collections import namedtuple
from collections import OrderedDict
import copy
import functools
import logging
import ipaddress
import itertools
from ipaddress import ip_address
from xml.etree import ElementTree as ET

import ruamel.yaml

import maloja.types
from maloja.workflow.utils import find_xpath

__doc__ = """
These classes define objects which Maloja uses internally. All of
them can be saved to file in a YAML representation.

"""

yaml_loads = functools.partial(ruamel.yaml.load, Loader=ruamel.yaml.RoundTripLoader)
yaml_dumps = functools.partial(ruamel.yaml.dump, Dumper=ruamel.yaml.RoundTripDumper)


def dataobject_as_ordereddict(dumper, data, flow_style=False):
    assert isinstance(dumper, ruamel.yaml.RoundTripDumper)
    return dumper.represent_ordereddict(
        OrderedDict([(k, getattr(data, k)) for k, v in data._defaults])
    )

def namedtuple_as_dict(dumper, data, flow_style=False):
    assert isinstance(dumper, ruamel.yaml.RoundTripDumper)
    return dumper.represent_dict(data._asdict())

def object_as_str(dumper, data, flow_style=False):
    assert isinstance(dumper, ruamel.yaml.RoundTripDumper)
    return dumper.represent_str(str(data))

class DataObject:

    _defaults = []

    @staticmethod
    def typecast(val):
        if val in ("true", "false"):
            return val == "true"
        try:
            if val.isdigit():
                return int(val)
        except AttributeError:
            return val
        else:
            return val

    def __init__(self, **kwargs):
        """
        Creates a fresh object, or one with attributes set by
        the `kwargs` dictionary.

        """
        data = copy.deepcopy(self._defaults) + list(kwargs.items())
        for k, v in data:
            setattr(self, k, v)

    def __eq__(self, other):
        tgt = getattr(other, "__dict__", None)
        return self.__dict__ == tgt

    def __hash__(self):
        return id(self)

    @property
    def elements(self):

        def visitor(obj):
            try:
                yield from obj.elements
            except AttributeError:
                if isinstance(obj, str):
                    yield (k, obj)
                    return

            try:
                yield from obj._asdict().items()
            except AttributeError:
                if isinstance(obj, list):
                    for item in obj:
                        yield from visitor(item)

        for k, _ in self._defaults:
            obj = getattr(self, k)
            yield from visitor(obj)

    def feed_xml(self, tree, *args, **kwargs):
        """
        Updates the object by feeding it XML
        from the VMware API.

        """
        ns = kwargs.pop("ns", "")
        fields = [k for k, v in self._defaults if v is None]
        attribs = ((attr, tree.attrib.get(attr)) for attr in tree.attrib if attr in fields)
        tags = [ns + k[0].upper() + k[1:] for k, v in self._defaults if v is None]
        body = (
            (elem.tag.replace(ns, ""), elem.text)
            for elem in tree
            if elem.tag in tags
        )
        for k, v in itertools.chain(attribs, body):
            setattr(self, k[0].lower() + k[1:], self.typecast(v))
        return self

class Project(DataObject):
    """
    Available for storing Maloja project information.

    """

class Catalog(DataObject):
    """
    The Catalog class represents a VMware public or private
    catalog.

    """

    _defaults = [
        ("name", None),
        ("href", None),
        ("type", None),
        ("dateCreated", None),
    ]
    """
    A list of (key, value) pairs which define the defaults for
    a new Catalog object.

    """

class Gateway(DataObject):
    """
    The Gateway class represents a VMware Edge Gateway.
    Here you can find the following:

        * Firewall rules
        * DNAT rules
        * SNAT rules

    """

    FW = namedtuple(
        "FW", ["description", "int_addr", "int_port", "ext_addr", "ext_port"]
    )

    DNAT = namedtuple(
        "DNAT", ["int_addr", "int_port", "ext_addr", "ext_port"]
    )
    SNAT = namedtuple(
        "SNAT", ["int_addr", "int_port", "ext_addr", "ext_port"]
    )

    _defaults = [
        ("name", None),
        ("href", None),
        ("type", None),
        ("fw", []),
        ("dnat", []),
        ("snat", []),
    ]
    """
    A list of (key, value) pairs which define the defaults for
    a new Gateway object.

    """

    @staticmethod
    def servicecast(val):
        val = val.lower()
        if "any" in val:
            return None
        else:
            return list(ipaddress.ip_network(val).hosts()) or [ipaddress.ip_address(val)]

    @staticmethod
    def typecast(val):
        rv = DataObject.typecast(val)
        if isinstance(rv, str):
            try:
                rv = Gateway.servicecast(rv)
            except ValueError:
                pass
        return rv

    def __init__(self, **kwargs):
        """
        Creates a fresh object, or one with attributes set by
        the `kwargs` dictionary.

        """
        for seq, typ in [("fw", Gateway.FW), ("dnat", Gateway.DNAT), ("snat", Gateway.SNAT)]:
            if seq in kwargs:
                kwargs[seq] = [
                    typ(**{k: self.typecast(v) for k, v in i.items()})
                    for i in kwargs[seq]
                ]

        super().__init__(**kwargs)

    def feed_xml(self, tree, ns="{http://www.vmware.com/vcloud/v1.5}"):
        """
        Updates the object by feeding it XML
        from the VMware API.

        """
        log = logging.getLogger("maloja.model.Gateway")
        super().feed_xml(tree, ns=ns)

        config = tree.find(
            "./*/{}EdgeGatewayServiceConfiguration".format(ns)
        )
        if config is None:
            return self

        elem = config.find(ns + "FirewallService")
        for rule in elem.iter(ns + "FirewallRule"):
            int_ip = rule.find(ns + "DestinationIp").text
            self.fw.append(
                Gateway.FW(
                    getattr(rule.find(ns + "Description"), "text", None),
                    self.servicecast(rule.find(ns + "DestinationIp").text),
                    int(getattr(rule.find(ns + "Port"), "text", "0")) or None,
                    self.servicecast(rule.find(ns + "SourceIp").text),
                    int(getattr(rule.find(ns + "SourcePort"), "text", "0")) or None,
                )
            )
        elem = config.find(ns + "NatService")
        for elem in elem.iter(ns + "NatRule"):
            if elem.find(ns + "RuleType").text == "DNAT":
                rule = elem.find(ns + "GatewayNatRule")
                self.dnat.append(
                    Gateway.DNAT(
                        self.servicecast(rule.find(ns + "TranslatedIp").text),
                        int(getattr(rule.find(ns + "TranslatedPort"), "text", "0")) or None,
                        self.servicecast(rule.find(ns + "OriginalIp").text),
                        int(getattr(rule.find(ns + "OriginalPort"), "text", "0")) or None
                    )
                )
            elif elem.find(ns + "RuleType").text == "SNAT":
                rule = elem.find(ns + "GatewayNatRule")
                self.snat.append(
                    Gateway.SNAT(
                        self.servicecast(rule.find(ns + "OriginalIp").text),
                        int(getattr(rule.find(ns + "OriginalPort"), "text", "0")) or None,
                        self.servicecast(rule.find(ns + "TranslatedIp").text),
                        int(getattr(rule.find(ns + "TranslatedPort"), "text", "0")) or None
                    )
                )
        return self

class Network(DataObject):
    """
    The Network class represents a VMware network.
    Here you can find the following:

        * DNS rules
        * DHCP configuration

    """

    DHCP = namedtuple(
        "DHCP", ["pool"]
    )

    _defaults = [
        ("name", None),
        ("href", None),
        ("type", None),
        ("defaultGateway", None),
        ("netmask", None),
        ("dhcp", None),
        ("dnsSuffix", None),
        ("dns", []),
    ]
    """
    A list of (key, value) pairs which define the defaults for
    a new Network object.

    """

    def __init__(self, **kwargs):
        """
        Creates a fresh object, or one with attributes set by
        the `kwargs` dictionary.

        """
        super().__init__(**kwargs)

    def feed_xml(self, tree, ns="{http://www.vmware.com/vcloud/v1.5}"):
        """
        Updates the object by feeding it XML
        from the VMware API.

        """
        log = logging.getLogger("maloja.model.Network")
        log.debug(ET.tostring(tree, encoding="unicode"))
        self.dns = [tree.attrib.get("dns1"), tree.attrib.get("dns2")]
        super().feed_xml(tree, ns=ns)

        scope = tree.find(
            "./*/*/{}IpScope".format(ns)
        )
        self.defaultGateway = next(iter(Gateway.servicecast(
            scope.find(ns + "Gateway").text
        )), None)
        self.netmask = next(iter(Gateway.servicecast(
            scope.find(ns + "Netmask").text
        )), None)


        elem = None
        config = tree.find(
            "./*/{}GatewayDhcpService".format(ns)
        )
        if config is not None:
            elem = config.find(ns + "Pool")
        if elem is not None:
            self.dhcp = Network.DHCP(pool=[
                next(iter(Gateway.servicecast(elem.find(ns + "LowIpAddress").text)), None),
                next(iter(Gateway.servicecast(elem.find(ns + "HighIpAddress").text)), None),
            ])
        return self

class Org(DataObject):
    """
    The Org class represents a VMware organisation.

    """

    _defaults = [
        ("name", None),
        ("href", None),
        ("type", None),
        ("fullName", None),
    ]
    """
    A list of (key, value) pairs which define the defaults for
    a new Org object.

    """

class Task(DataObject):
    """
    The Task class represents a task running against a VMware
    resource.

    """

    _defaults = [
        ("name", None),
        ("href", None),
        ("type", None),
        ("operationName", None),
        ("organization", None),
        ("startTime", None),
        ("status", None),
    ]
    """
    A list of (key, value) pairs which define the defaults for
    a new Task object.

    """

    def feed_xml(self, tree, ns="{http://www.vmware.com/vcloud/v1.5}"):
        """
        Updates the object by feeding it XML
        from the VMware API.

        """
        log = logging.getLogger("maloja.model.Task")
        super().feed_xml(tree, ns=ns)
        org = tree.find(ns + "Organization")
        self.organization = Org().feed_xml(org, ns=ns)
        owner = tree.find(ns + "Owner")
        typ = owner.attrib.get("type")
        self.owner = {
            "application/vnd.vmware.admin.edgeGateway+xml": Gateway,
            "application/vnd.vmware.vcloud.vApp+xml": VApp
        }.get(typ)().feed_xml(owner, ns=ns)
        return self

class Template(DataObject):
    """
    The Template class represents a VMware VAppTemplate.

    """

    _defaults = [
        ("name", None),
        ("href", None),
        ("type", None),
        ("dateCreated", None),
    ]
    """
    A list of (key, value) pairs which define the defaults for
    a new Template object.

    """

class VApp(DataObject):
    """
    The VApp class represents a VMware VApp.

    """

    _defaults = [
        ("name", None),
        ("href", None),
        ("type", None),
    ]
    """
    A list of (key, value) pairs which define the defaults for
    a new Vapp object.

    """

class Vdc(DataObject):
    """
    The Vdc class represents a VMware Vdc.

    """

    _defaults = [
        ("name", None),
        ("href", None),
        ("type", None),
        ("description", None),
    ]
    """
    A list of (key, value) pairs which define the defaults for
    a new Vdc object.

    """

class Vm(DataObject):
    """
    The Vm class represents a VMware Vm.

    """

    rasd = {
        0: namedtuple("Other", []),
        3: namedtuple("Processor", ["instanceID", "virtualQuantity"]),
        4: namedtuple("Memory", ["instanceID", "virtualQuantity"]),
        5: namedtuple("IDEController", ["address", "description", "instanceID"]),
        6: namedtuple(
            "SCSIController",
            ["address", "description", "elementName", "instanceID", "resourceSubType"]
        ),
        10: namedtuple(
            "EthernetAdapter",
            ["address", "connection", "elementName", "instanceID", "resourceSubType"]
        ),
        14: namedtuple("FloppyDrive", ["description", "instanceID"]),
        15: namedtuple("CDDrive", ["description", "instanceID"]),
        16: namedtuple("DVDDrive", ["description", "instanceID"]),
        17: namedtuple(
            "DiskDrive",
            ["addressOnParent", "description", "hostResource", "instanceID"]
        ),
        23: namedtuple("USBController", []),
    }

    HardDisk = namedtuple(
        "HardDisk", ["name", "capacity"]
    )

    NetworkCard = namedtuple(
        "NetworkCard", ["name", "mac", "device"]
    )

    NetworkConnection = namedtuple(
        "NetworkConnection", [
            "name", "ip", "isConnected", "macAddress",
            "ipAddressAllocationMode"
        ]
    )

    SCSIController = namedtuple(
        "SCSIController", ["name", "device"]
    )

    _defaults = [
        ("name", None),
        ("href", None),
        ("type", None),
        ("dateCreated", None),
        ("guestOs", None),
        ("hardwareVersion", set([])),
        ("cpu", None),
        ("memoryMB", None),
        ("networkcards", []),
        ("harddisks", []),
        ("scsi", []),
        ("cd", None),
        ("floppydisk", None),
        ("isBusy", None),
        ("isDeleted", None),
        ("isDeployed", None),
        ("isInMaintenanceMode", None),
        ("isPublished", None),
        ("status", None),
        ("storageProfileName", None),
        ("vmToolsVersion", None),
        ("networkconnections", []),
        ("guestcustomization", None)
    ]
    """
    A list of (key, value) pairs which define the defaults for
    a new Vm object.

    """

    def __init__(self, **kwargs):
        """
        Creates a fresh object, or one with attributes set by
        the `kwargs` dictionary.

        """
        for seq, typ in [
            ("harddisks", Vm.HardDisk),
            ("networkcards", Vm.NetworkCard),
            ("networkconnections", Vm.NetworkConnection),
            ("scsi", Vm.SCSIController),
        ]:
            if seq in kwargs:
                kwargs[seq] = [
                    typ(**{k: self.typecast(v) for k, v in i.items()})
                    for i in kwargs[seq]
                ]

        super().__init__(**kwargs)

    def feed_xml(self, tree, ns="{http://www.vmware.com/vcloud/v1.5}"):
        """
        Updates the object by feeding it XML
        from the VMware API.

        """

        if tree.tag in (ns + "VAppTemplate", ns + "Vm", ns + "VMRecord"):
            super().feed_xml(tree, ns=ns)
            try:
                self.hardwareVersion.add(int(tree.attrib.get("hardwareVersion")))
            except TypeError:
                #  No version supplied
                pass

        if tree.tag in (ns + "VAppTemplate", ns + "Vm"):
            hardware = find_xpath(
                "./*/{}Item".format("{http://schemas.dmtf.org/ovf/envelope/1}"), tree
            )
            rasdNs = (
                "{http://schemas.dmtf.org/wbem/wscim/1/cim-schema/"
                "2/CIM_ResourceAllocationSettingData}"
            )
            for item in hardware:
                key = int(getattr(item.find(rasdNs + "ResourceType"), "text", "0"))
                typ = Vm.rasd[key]
                fields = [(rasdNs + i).lower() for i in typ._fields]
                obj = typ(*(i for i in list(item) if i.tag.lower() in fields))
                if key == 3:
                    self.cpu = int(obj.virtualQuantity.text)
                elif key == 4:
                    self.memoryMB = int(obj.virtualQuantity.text)
                elif key == 6:
                    entry = Vm.SCSIController(
                        obj.elementName.text,
                        obj.resourceSubType.text
                    )
                    if entry not in self.scsi:
                        self.scsi.append(entry)
                elif key == 10:
                    entry = Vm.NetworkCard(
                        obj.elementName.text,
                        obj.address.text,
                        obj.resourceSubType.text
                    )
                    if entry not in self.networkcards:
                        self.networkcards.append(entry)
                elif key == 17:
                    entry = Vm.HardDisk(
                        obj.description.text,
                        int(obj.hostResource.attrib.get(ns + "capacity"))
                    )
                    if entry not in self.harddisks:
                        self.harddisks.append(entry)

            self.networkconnections = [
                Vm.NetworkConnection(
                    i.attrib["network"],
                    getattr(i.find(ns + "IpAddress"), "text", None),
                    i.find(ns + "IsConnected").text == "true",
                    i.find(ns + "MACAddress").text,
                    getattr(i.find(ns + "IpAddressAllocationMode"), "text", None))
                for i in tree.iter(ns + "NetworkConnection")]

            section = tree.find(ns + "GuestCustomizationSection")
            # TODO: Define customization storage

        return self

ruamel.yaml.RoundTripDumper.add_representer(ipaddress.IPv4Address, object_as_str)
ruamel.yaml.RoundTripDumper.add_representer(Catalog, dataobject_as_ordereddict)
ruamel.yaml.RoundTripDumper.add_representer(Gateway, dataobject_as_ordereddict)
ruamel.yaml.RoundTripDumper.add_representer(Gateway.FW, namedtuple_as_dict)
ruamel.yaml.RoundTripDumper.add_representer(Gateway.DNAT, namedtuple_as_dict)
ruamel.yaml.RoundTripDumper.add_representer(Gateway.SNAT, namedtuple_as_dict)
ruamel.yaml.RoundTripDumper.add_representer(Network, dataobject_as_ordereddict)
ruamel.yaml.RoundTripDumper.add_representer(Network.DHCP, namedtuple_as_dict)
ruamel.yaml.RoundTripDumper.add_representer(Org, dataobject_as_ordereddict)
ruamel.yaml.RoundTripDumper.add_representer(Project, dataobject_as_ordereddict)
ruamel.yaml.RoundTripDumper.add_representer(Template, dataobject_as_ordereddict)
ruamel.yaml.RoundTripDumper.add_representer(VApp, dataobject_as_ordereddict)
ruamel.yaml.RoundTripDumper.add_representer(Vdc, dataobject_as_ordereddict)
ruamel.yaml.RoundTripDumper.add_representer(Vm, dataobject_as_ordereddict)
ruamel.yaml.RoundTripDumper.add_representer(Vm.HardDisk, namedtuple_as_dict)
ruamel.yaml.RoundTripDumper.add_representer(Vm.NetworkCard, namedtuple_as_dict)
ruamel.yaml.RoundTripDumper.add_representer(Vm.NetworkConnection, namedtuple_as_dict)
ruamel.yaml.RoundTripDumper.add_representer(Vm.SCSIController, namedtuple_as_dict)
