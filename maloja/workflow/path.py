#!/usr/bin/env python
#   -*- encoding: UTF-8 -*-

from collections import defaultdict
from collections import namedtuple
import glob
import itertools
import os.path
import tempfile
import threading

from maloja.model import Catalog
from maloja.model import Gateway
from maloja.model import Network
from maloja.model import Template
from maloja.model import Org
from maloja.model import Project
from maloja.model import VApp
from maloja.model import Vdc
from maloja.model import Vm
from maloja.model import yaml_dumps
from maloja.model import yaml_loads

locks = defaultdict(threading.Lock)

Path = namedtuple(
    "Path",
    ["root", "project", "org", "service", "category", "container", "node", "file"]
)
"""
This structure contains the file path components necessary to
identify a resource stored as YAML data in the Maloja survey tree.

"""


def cache(path, obj=None):
    parent = os.path.join(*(i for i in path[:-1] if i is not None))
    os.makedirs(parent, exist_ok=True)
    fP = os.path.join(parent, path.file)
    if obj is not None:
        try:
            locks[path].acquire()
            with open(fP, "w") as output:
                data = yaml_dumps(obj)
                output.write(data)
                output.flush()
        finally:
            locks[path].release()
    return fP


def project(root, prefix="proj_", suffix=""):
    os.makedirs(root, exist_ok=True)
    drcty = tempfile.mkdtemp(suffix=suffix, prefix=prefix, dir=root)
    path = Path(root, os.path.basename(drcty), None, None, None, None, None, "project.yaml")
    proj = Project()
    return cache(path, proj)


def find_ypath(path: Path, query, **kwargs):
    """
    Find elements within the cache tree whose attributes match certain
    values.

    :param path: search location in cache.
    :param query: an archetype of the object to look for.
    :param kwargs: specifies attribute values to filter by.
     If no keyword arguments are supplied, then attributes
     on the query object serve as criteria to be matched.

    :return: An iterator over matching (path, object) tuples.
    """
    wildcards = [i if i is not None else '*' for i in path[:-1]]
    locations = {
        Org: wildcards[:3] + ["org.yaml"],
        Catalog: wildcards[:5] + ["catalog.yaml"],
        Gateway: wildcards[:4] + ["edge.yaml"],
        Vdc: wildcards[:4] + ["vdc.yaml"],
        Network: wildcards[:6] + ["net.yaml"],
        VApp: wildcards[:6] + ["vapp.yaml"],
        Template: wildcards[:5] + ["template.yaml"],
        Vm: wildcards[:7] + ["vm.yaml"],
    }
    typ = type(query)
    criteria = set(kwargs.items()) or set(query.elements)
    pattern = os.path.join(*locations[typ])
    for fP in glob.glob(pattern):
        with open(fP, 'r') as data:
            obj = typ(**yaml_loads(data.read()))
            if criteria.issubset(set(obj.elements)):
                hit = Path(*fP.split(os.sep)[-len(path):])
                yield (hit._replace(root=path.root), obj)


def split_to_path(data, root=None):
    drive, tail = os.path.splitdrive(data)
    bits = tail.split(os.sep)
    lookup = {
        "project.yaml": -3,
        "org.yaml": -4,
        "edge.yaml": -5,
        "vdc.yaml": -5,
        "catalog.yaml": -6,
        "net.yaml": -7,
        "vapp.yaml": -7,
        "template.yaml": -7,
        "vm.yaml": -8,
    }
    index = lookup[bits[-1]] #  The index of the project field
    data = list(itertools.chain(
        bits[index: -1],
        itertools.repeat(None, 8 + index),
        itertools.repeat(bits[-1], 1)
    ))
    rv = Path(*data)
    if root is None:
        rv = rv._replace(root=drive + os.path.join(*bits[:index]))
    else:
        rv = rv._replace(root=root)
    return rv
