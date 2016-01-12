#!/usr/bin/env python
#   -*- encoding: UTF-8 -*-

from collections import defaultdict
from collections import namedtuple
import glob
import itertools
import os.path
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
identify resource stored as YAML data in the Maloja survey tree.

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

def find_ypath(path: Path, obj):
    """
    Find elements within the cache tree whose attributes match certain
    values.

    :param path: search location in cache.
    :param obj: object to look for.
     Any attributes on the object evaluating as True will serve as criteria to be matched.

    :return: An iterator over matching (path, object) tuples.
    """
    wildcards = [i if i is not None else '*' for i in path[:-1]]
    locations = {
        Org: (wildcards[:3] + ["org.yaml"],),
        Catalog: (wildcards[:5] + ["catalog.yaml"],),
        Vdc: (wildcards[:4] + ["vdc.yaml"],),
        VApp: (wildcards[:5] + ["vapp.yaml"],),
        Template: (wildcards[:5] + ["template.yaml"],),
        Vm: (wildcards[:6] + ["vm.yaml"], wildcards[:7] + ["vm.yaml"]),
    }
    typ = type(obj)
    patterns = [os.path.join(*i) for i in locations[typ]]
    for pattern in patterns:
        for fP in glob.glob(pattern):
            with open(fP, 'r') as data:
                obj = typ(**yaml_loads(data.read()))
                yield (fP, obj)

# TODO: Surveyor.patterns go here
# TODO: Factories for empty Paths
# TODO: Integrate with model classes
# TODO: Needs a search API cf find_xpath

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
                data = dict([
                    (k, getattr(item, k))
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
