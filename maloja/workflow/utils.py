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
