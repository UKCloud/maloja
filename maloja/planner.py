#!/usr/bin/env python
#   -*- encoding: UTF-8 -*-

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

"""

types = {
"application/vnd.vmware.admin.edgeGateway+xml": Gateway,
"application/vnd.vmware.vcloud.orgVdcNetwork+xml": Network,
"application/vnd.vmware.vcloud.vAppTemplate+xml": Template,
"application/vnd.vmware.vcloud.vdc+xml": Vdc,
"application/vnd.vmware.vcloud.vm+xml": Vm,
}


def read_objects(text):
    # FIXME: First object of each type provides defaults
    log = logging.getLogger("maloja.planner")
    for n, data in enumerate(yaml_loads(text)):
        try:
            typ = types[data.get("type", None)]
        except KeyError:
            log.warning("Type unrecognised at item {}".format(n + 1))
            continue

        try:
            obj = typ(**data)
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

    objs = list(read_objects(args.design.read()))
    objs = check_objects(objs)
    print(*[vars(i) for i in objs], sep="\n")
    return 0


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
