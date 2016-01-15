#!/usr/bin/env python
#   -*- encoding: UTF-8 -*-

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
        fields = [k for k, v in self._defaults]
        attribs = ((attr, tree.attrib.get(attr)) for attr in tree.attrib if attr in fields)
        tags = [ns + k[0].upper() + k[1:] for k, v in self._defaults]
        body = (
            (elem.tag.replace(ns, ""), elem.text)
            for elem in tree
            if elem.tag in tags
        )
        for k, v in itertools.chain(attribs, body):
            setattr(self, k[0].lower() + k[1:], self.typecast(v))
        return self

class Project(DataObject):
    pass

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

    def feed_xml(self, tree, ns="{http://www.vmware.com/vcloud/v1.5}"):
        """
        Updates the object by feeding it XML
        from the VMware API.

        """
        log = logging.getLogger("maloja.model.Network")
        log.debug(ET.tostring(tree, encoding="unicode"))
        self.dns = [tree.attrib.get("dns1"), tree.attrib.get("dns2")]
        super().feed_xml(tree, ns=ns)
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
        self.owner = {
            "application/vnd.vmware.vcloud.vApp+xml": VApp
        }.get(owner.attrib.get("type"))().feed_xml(owner, ns=ns)
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

    NetworkConnection = namedtuple(
        "NetworkConnection", [
            "name", "ip", "isConnected", "macAddress",
            "ipAddressAllocationMode"
        ]
    )

    _defaults = [
        ("name", None),
        ("href", None),
        ("type", None),
        ("dateCreated", None),
        ("guestOs", None),
        ("hardwareVersion", None),
        ("cpu", None),
        ("memoryMB", None),
        ("networkcards", []),
        ("harddisks", []),
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
        seq, typ = ("networkconnections", Vm.NetworkConnection)
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

        if tree.tag in (ns + "VAppTemplate", ns + "Vm"):
            self.networkconnections = [
                Vm.NetworkConnection(
                    i.attrib["network"],
                    getattr(i.find(ns + "IpAddress"), "text", None),
                    i.find(ns + "IsConnected").text == "true",
                    i.find(ns + "MACAddress").text,
                    getattr(i.find(ns + "IpAddressAllocationMode"), "text", None))
                for i in tree.iter(ns + "NetworkConnection")]
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
ruamel.yaml.RoundTripDumper.add_representer(Vm.NetworkConnection, namedtuple_as_dict)
