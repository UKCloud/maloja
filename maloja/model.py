#!/usr/bin/env python
#   -*- encoding: UTF-8 -*-

from collections import namedtuple
from collections import OrderedDict
import functools
import logging
import itertools

import ruamel.yaml

import maloja.types

Status = namedtuple("Status", ["id", "job", "level"])

yaml_loads = functools.partial(ruamel.yaml.load, Loader=ruamel.yaml.RoundTripLoader)
yaml_dumps = functools.partial(ruamel.yaml.dump, Dumper=ruamel.yaml.RoundTripDumper)


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
        fields = [k for k, v in self._defaults]
        attribs = ((attr, tree.attrib.get(attr)) for attr in tree.attrib if attr in fields)
        body = ((elem.tag, elem.text) for elem in tree if elem.tag in fields)
        for k, v in itertools.chain(attribs, body):
            setattr(self, k, self.typecast(v))
        return self


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

ruamel.yaml.RoundTripDumper.add_representer(Vm, dataobject_as_ordereddict)
ruamel.yaml.RoundTripDumper.add_representer(Vm.NetworkConnection, namedtuple_as_dict)
