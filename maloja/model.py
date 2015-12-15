#!/usr/bin/env python
#   -*- encoding: UTF-8 -*-

from collections import namedtuple
from collections import OrderedDict
import functools
import logging
import ipaddress
import itertools
from ipaddress import ip_address
from xml.etree import ElementTree as ET

import ruamel.yaml

import maloja.types

yaml_loads = functools.partial(ruamel.yaml.load, Loader=ruamel.yaml.RoundTripLoader)
yaml_dumps = functools.partial(ruamel.yaml.dump, Dumper=ruamel.yaml.RoundTripDumper)


def dataobject_as_ordereddict(dumper, data, flow_style=False):
    assert isinstance(dumper, ruamel.yaml.RoundTripDumper)
    return dumper.represent_ordereddict(OrderedDict([(k, getattr(data, k)) for k, v in data._defaults]))


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
        data = self._defaults + list(kwargs.items())
        for k, v in data:
            setattr(self, k, v)

    def feed_xml(self, tree, *args, **kwargs):
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

class Catalog(DataObject):

    _defaults = [
        ("name", None),
        ("href", None),
        ("type", None),
        ("dateCreated", None),
    ]

class Gateway(DataObject):

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

    @staticmethod
    def servicecast(val):
        val = val.lower()
        if "any" in val:
            return None
        else:
            return list(ipaddress.ip_network(val).hosts()) or [ipaddress.ip_address(val)]

    def __init__(self, **kwargs):
        for seq, typ in [("fw", Gateway.FW), ("dnat", Gateway.DNAT), ("snat", Gateway.SNAT)]:
            if seq in kwargs:
                kwargs[seq] = [typ(**{k: self.typecast(v) for k, v in i.items()}) for i in kwargs[seq]]

        super().__init__(**kwargs)

    def feed_xml(self, tree, ns="{http://www.vmware.com/vcloud/v1.5}"):
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

    _defaults = [
        ("name", None),
        ("href", None),
        ("type", None),
        ("defaultGateway", None),
        ("netmask", None),
        ("dnsSuffix", None),
        ("dns", []),
    ]

    def feed_xml(self, tree, ns="{http://www.vmware.com/vcloud/v1.5}"):
        log = logging.getLogger("maloja.model.Network")
        self.dns = [tree.attrib.get("dns1"), tree.attrib.get("dns2")]
        super().feed_xml(tree, ns=ns)
        return self

class Org(DataObject):

    _defaults = [
        ("name", None),
        ("href", None),
        ("type", None),
        ("fullName", None),
    ]

class Template(DataObject):

    _defaults = [
        ("name", None),
        ("href", None),
        ("type", None),
        ("dateCreated", None),
    ]

class VApp(DataObject):

    _defaults = [
        ("name", None),
        ("href", None),
        ("type", None),
    ]

class Vdc(DataObject):

    _defaults = [
        ("name", None),
        ("href", None),
        ("type", None),
        ("description", None),
    ]

class Vm(DataObject):

    NetworkConnection = namedtuple(
        "NetworkConnection", ["name", "ip", "isConnected", "macAddress", "ipAddressAllocationMode"]
    )

    _defaults = [
        ("name", None),
        ("href", None),
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

    def __init__(self, **kwargs):
        seq, typ = ("networkconnections", Vm.NetworkConnection)
        if seq in kwargs:
            kwargs[seq] = [typ(**{k: self.typecast(v) for k, v in i.items()}) for i in kwargs[seq]]

        super().__init__(**kwargs)

    def feed_xml(self, tree, ns="{http://www.vmware.com/vcloud/v1.5}"):

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
ruamel.yaml.RoundTripDumper.add_representer(Org, dataobject_as_ordereddict)
ruamel.yaml.RoundTripDumper.add_representer(Template, dataobject_as_ordereddict)
ruamel.yaml.RoundTripDumper.add_representer(VApp, dataobject_as_ordereddict)
ruamel.yaml.RoundTripDumper.add_representer(Vdc, dataobject_as_ordereddict)
ruamel.yaml.RoundTripDumper.add_representer(Vm, dataobject_as_ordereddict)
ruamel.yaml.RoundTripDumper.add_representer(Vm.NetworkConnection, namedtuple_as_dict)
