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

import collections.abc
import logging
from logging.handlers import WatchedFileHandler
import itertools
import os
import sys
import warnings

import maloja.cli
from maloja.model import Gateway
from maloja.model import Network
from maloja.model import Template
from maloja.model import Vdc
from maloja.model import Vm
from maloja.model import yaml_loads


__doc__ = """
The planner module allows offline inspection of a design file.

A design file conforms to YAML syntax. It is made up of items
from a survey (also YAML) assembled in a hierarchical structure.

"""

types = {
    "application/vnd.vmware.admin.edgeGateway+xml": Gateway,
    "application/vnd.vmware.vcloud.orgVdcNetwork+xml": Network,
    "application/vnd.vmware.vcloud.vAppTemplate+xml": Template,
    "application/vnd.vmware.vcloud.vdc+xml": Vdc,
    "application/vnd.vmware.vcloud.vm+xml": Vm,
}


def read_objects(text):
    log = logging.getLogger("maloja.planner")
    contents = yaml_loads(text)
    if contents is None:
        log.warning("No objects found.")
        return
    elif isinstance(contents, collections.abc.Mapping):
        contents = [contents]

    for n, data in enumerate(contents):
        try:
            typ = types[data.get("type", None)]
        except KeyError:
            log.warning("Type unrecognised at item {}".format(n + 1))
            continue

        attribs = {k: data.get(k, None) for k, v in typ._defaults}
        try:
            obj = typ(**attribs)
        except TypeError as e:
            log.warning("Type mismatch at item {}".format(n + 1))
            log.warning(e)
            continue

        log.info(obj)
        yield obj


def check_objects(seq):
    log = logging.getLogger("maloja.planner")
    missing = set(types.values()) - {type(obj) for obj in seq}
    for typ in missing:
        log.warning("Missing an object of type {0.__name__}".format(typ))
    log.info("Approved {0} objects of {0}".format(len(seq)))
    return seq


def report(fObj):
    objs = list(read_objects(fObj.read()))
    objs = check_objects(objs)
    print(*[vars(i) for i in objs], sep="\n")
    return 0


def main(args):

    log = logging.getLogger("maloja")
    log.setLevel(args.log_level)

    formatter = logging.Formatter(
        "%(asctime)s %(levelname)-7s %(name)s|%(message)s")
    ch = logging.StreamHandler()

    if args.log_path is None:
        ch.setLevel(args.log_level)
    else:
        fh = WatchedFileHandler(args.log_path)
        fh.setLevel(args.log_level)
        fh.setFormatter(formatter)
        log.addHandler(fh)
        ch.setLevel(logging.WARNING)

    ch.setFormatter(formatter)
    log.addHandler(ch)

    return report(args.design)


def run():
    p = maloja.cli.parser(description=__doc__)
    p = maloja.cli.add_common_options(p)
    p = maloja.cli.add_planner_options(p)
    args = p.parse_args()
    rv = 0
    if args.version:
        sys.stdout.write(maloja.__version__ + "\n")
    else:
        rv = main(args)

    if rv == 2:
        sys.stderr.write("\n Missing command.\n\n")
        p.print_help()

    sys.exit(rv)

if __name__ == "__main__":
    run()
