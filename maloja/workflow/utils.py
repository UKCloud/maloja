#!/usr/bin/env python
#   -*- encoding: UTF-8 -*-

from collections import defaultdict
from collections import namedtuple
import contextlib
import itertools
import tempfile
import operator
import os.path
import warnings

import pkg_resources

Path = namedtuple(
    "Path",
    ["root", "project", "org", "dc", "app", "node", "file"]
)
"""
This structure contains the file path components necessary to
identify resource stored as YAML data in the Maloja survey tree.

"""

def find_xpath(xpath, tree, namespaces={}, **kwargs):
    """
    Find elements within an XML tree whose attributes match certain
    values.

    :param xpath: an xpath query string.
    :param tree: `xml.etree.ElementTree` object.
    :param namespaces: a dictionary of namespace prefixes.
    :param kwargs: specifies attribute values to filter by.

    :return: An iterator over valid elements.
    """
    elements = tree.iterfind(xpath, namespaces=namespaces)
    if not kwargs:
        return elements
    else:
        query = set(kwargs.items())
        return (i for i in elements if query.issubset(set(i.attrib.items())))


def group_by_type(items):
    """
    Group a sequence of items by the type of item.

    :return: A dictionary of lists. Keys in the dictionary are types.
    """
    return defaultdict(
        list,
        {k: list(v) for k, v in itertools.groupby(items, key=type)}
    )


def make_path(path: Path, prefix="proj_", suffix=""):
    os.makedirs(path.root, exist_ok=True)

    if path.project is None and path.file is not None:
        project = tempfile.mkdtemp(suffix=suffix, prefix=prefix, dir=path.root)
        open(os.path.join(project, path.file), "w").close()
        return path._replace(project=os.path.basename(project))
    else:
        return path


def recent_project(path: Path):
    warnings.warn("Use find_project instead", DeprecationWarning, stacklevel=2)
    projects = [
        i
        for i in os.listdir(path.root)
        if os.path.isfile(os.path.join(path.root, i, "project.yaml"))
    ]
    stats = [(os.path.getmtime(os.path.join(path.root, fP)), fP)
             for fP in projects]
    stats.sort(key=operator.itemgetter(0), reverse=True)
    return Path(
        path.root, next((i[1] for i in stats), None), None, None, None, None, path.file)


def split_to_path(data, root=None):
    lookup = {
        "project.yaml": -3,
        "org.yaml": -4,
        "vdc.yaml": -5,
        "catalog.yaml": -5,
        "vapp.yaml": -6,
        "template.yaml": -6,
        "vm.yaml": -7,
    }
    drive, tail = os.path.splitdrive(data)
    bits = tail.split(os.sep)
    index = lookup[bits[-1]]
    data = list(itertools.chain(
        bits[index: -1],
        itertools.repeat(None, 7 + index),
        itertools.repeat(bits[-1], 1)
    ))
    rv = Path(*data)
    if root is None:
        rv = rv._replace(root=drive + os.path.join(*bits[:index]))
    else:
        rv = rv._replace(root=root)
    return rv


def plugin_interface(key="maloja.plugin"):
    for i in pkg_resources.iter_entry_points(key):
        try:
            ep = i.resolve()
        except Exception as e:
            continue
        else:
            yield (i.name, ep)


@contextlib.contextmanager
def record(nameOrStream, parent=None, suffix=".yaml"):
    if isinstance(nameOrStream, str):
        fD, fN = tempfile.mkstemp(suffix=suffix, dir=parent)
        try:
            rv = open(fN, 'w')
            yield rv
        except Exception as e:
            raise e
        rv.close()
        os.close(fD)
        os.rename(fN, os.path.join(parent, nameOrStream))
    else:
        yield nameOrStream
