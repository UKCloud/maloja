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

from collections import defaultdict
from collections import namedtuple
import glob
import itertools
import logging
import operator
import os.path
import tempfile
import threading

from maloja import __version__
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
    log = logging.getLogger("maloja.path.cache")
    parent = os.path.join(*(i for i in path[:-1] if i is not None))
    os.makedirs(parent, exist_ok=True)
    fP = os.path.join(parent, path.file)
    if obj is not None:
        try:
            locks[fP].acquire()
            with open(fP, "w") as output:
                data = yaml_dumps(obj)
                output.write(data)
                output.flush()
        finally:
            locks[fP].release()
    return fP


def make_project(root, prefix="proj_", suffix=""):
    os.makedirs(root, exist_ok=True)
    drcty = tempfile.mkdtemp(suffix=suffix, prefix=prefix, dir=root)
    path = Path(root, os.path.basename(drcty), None, None, None, None, None, "project.yaml")
    proj = Project()
    cache(path, proj)
    return path, proj


def find_project(root, query=None, **kwargs):
    query = query or Project()
    path = Path(root, None, None, None, None, None, None, "project.yaml")

    hits = [(os.path.getmtime(os.path.join(*(i for i in p if i is not None))),
             p, obj) for p, obj in find_ypath(path, query, **kwargs)]
    hits.sort(key=operator.itemgetter(0), reverse=True)
    return next(iter(hits))[1:]


def find_ypath(path: Path, query, **kwargs):
    """
    Find objects within the Maloja cache tree whose attributes match certain
    values.

    :param path: search location in cache.
    :param query: an archetype of the object to look for.
    :param kwargs: specifies attribute values to filter by.
     If no keyword arguments are supplied, then attributes
     on the query object serve as criteria to be matched.

    :return: An iterator over matching (path, object) tuples.
    """
    log = logging.getLogger("maloja.path.find_ypath")
    wildcards = [i if i is not None else '*' for i in path[:-1]]
    locations = {
        Project: wildcards[:2] + ["project.yaml"],
        Org: wildcards[:3] + ["org.yaml"],
        Catalog: wildcards[:5] + ["catalog.yaml"],
        Gateway: wildcards[:4] + ["edge.yaml"],
        Vdc: wildcards[:4] + ["vdc.yaml"],
        Network: wildcards[:6] + ["net.yaml"],
        VApp: wildcards[:6] + ["vapp.yaml"],
        Template: wildcards[:6] + ["template.yaml"],
        Vm: wildcards[:7] + ["vm.yaml"],
    }
    typ = type(query)
    criteria = set(kwargs.items()) or set(query.elements)
    pattern = os.path.join(*locations[typ])
    for fP in glob.glob(pattern):
        obj = None
        try:
            locks[fP].acquire()
            with open(fP, 'r') as data:
                obj = typ(**yaml_loads(data.read()))
        finally:
            locks[fP].release()

        if obj is not None and criteria.issubset(set(obj.elements)):
            tail = fP[len(path.root):].split(os.sep)
            pack = 8 - len(locations[typ])
            hit = [path.root] + tail[1:-1] + [None] * pack + tail[-1:]
            yield (Path(*hit), obj)


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
    index = lookup[bits[-1]]  # The index of the project field
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
