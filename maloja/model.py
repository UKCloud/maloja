#!/usr/bin/env python
#   -*- encoding: UTF-8 -*-

from collections import namedtuple
from collections import OrderedDict
import functools
import logging
import itertools

import ruamel.yaml

import maloja.types

yaml_loads = functools.partial(ruamel.yaml.load, Loader=ruamel.yaml.RoundTripLoader)
yaml_dumps = functools.partial(ruamel.yaml.dump, Dumper=ruamel.yaml.RoundTripDumper)

Template = namedtuple("Template", ["name", "type", "href", "dateCreated"])

def dataobject_as_ordereddict(dumper, data, flow_style=False):
    assert isinstance(dumper, ruamel.yaml.RoundTripDumper)
    return dumper.represent_ordereddict(OrderedDict([(k, getattr(data, k)) for k, v in data._defaults]))


def namedtuple_as_dict(dumper, data, flow_style=False):
    assert isinstance(dumper, ruamel.yaml.RoundTripDumper)
    return dumper.represent_dict(vars(data))

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

class Org(DataObject):

    _defaults = [
        ("name", None),
        ("href", None),
        ("type", None),
        ("fullName", None),
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
        "NetworkConnection", ["name", "ip", "isConnected", "macAddress"]
    )

    _defaults = [
        ("name", None),
        ("href", None),
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
        ("ipAddressAllocationMode", None),
        ("guestcustomization", None)
    ]

    def __init__(self, **kwargs):
        seq, typ = ("networkconnections", Vm.NetworkConnection)
        if seq in kwargs:
            kwargs[seq] = [typ(**{k: self.typecast(v) for k, v in i.items()}) for i in kwargs[seq]]

        super().__init__(**kwargs)

    def feed_xml(self, tree, ns="{http://www.vmware.com/vcloud/v1.5}"):

        if tree.tag in (ns + "Vm", ns + "VMRecord"):
            super().feed_xml(tree, ns=ns)

        if tree.tag == ns + "Vm":
            self.networkconnections = [
                Vm.NetworkConnection(
                    i.attrib["network"],
                    i.find(ns + "IpAddress").text,
                    True if i.find(ns + "IsConnected").text == "true" else False,
                    i.find(ns + "MACAddress").text)
                for i in tree.iter(ns + "NetworkConnection")]
        return self

ruamel.yaml.RoundTripDumper.add_representer(Catalog, dataobject_as_ordereddict)
ruamel.yaml.RoundTripDumper.add_representer(Org, dataobject_as_ordereddict)
ruamel.yaml.RoundTripDumper.add_representer(VApp, dataobject_as_ordereddict)
ruamel.yaml.RoundTripDumper.add_representer(Vdc, dataobject_as_ordereddict)
ruamel.yaml.RoundTripDumper.add_representer(Vm, dataobject_as_ordereddict)
ruamel.yaml.RoundTripDumper.add_representer(Vm.NetworkConnection, namedtuple_as_dict)
