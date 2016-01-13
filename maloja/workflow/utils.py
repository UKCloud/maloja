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
