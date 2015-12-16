#!/usr/bin/env python
#   -*- encoding: UTF-8 -*-

import logging
from logging.handlers import WatchedFileHandler
import itertools
import os
from pprint import pprint
import sys
import warnings

import maloja.cli
from maloja.model import Gateway
from maloja.model import Network
from maloja.model import yaml_loads


__doc__ = """
This is to prototype YAML design. Will becom e the planner module.
"""

types = {
"application/vnd.vmware.admin.edgeGateway+xml": Gateway,
"application/vnd.vmware.vcloud.orgVdcNetwork+xml": Network,
}

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

    for data in yaml_loads(args.design.read()):
        typ = types[data.get("type", None)]
        obj = typ(**data)
        pprint(obj)

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
