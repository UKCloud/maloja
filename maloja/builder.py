#!/usr/bin/env python
#   -*- encoding: UTF-8 -*-

import concurrent.futures
import logging
from logging.handlers import WatchedFileHandler
import itertools
import os
import queue
import sys
import warnings

from maloja.broker import Broker
import maloja.cli
from maloja.model import Gateway
from maloja.model import Network
from maloja.model import Vm
from maloja.planner import check_objects
from maloja.planner import read_objects
from maloja.types import Credentials
from maloja.workflow.utils import group_by_type


__doc__ = """
The builder module modifies cloud assets according to a design file.

"""

class Builder:

    def __init__(self, objs, operations, results, creds, path, executor=None, loop=None, **kwargs):
        log = logging.getLogger("maloja.builder.Builder")
        self.plans = group_by_type(objs)
        self.operations = operations
        self.results = results

    def __call__(self, session, token, callback=None, status=None, **kwargs):
        log = logging.getLogger("maloja.builder")
        log.debug("Called")

def create_builder(objs, operations, results, options, path=tuple(), loop=None):
    creds = Credentials(options.url, options.user, None)
    executor = concurrent.futures.ThreadPoolExecutor(
        max(4, len(Broker.tasks) + 2 * len(path))
    )
    broker = Broker(operations, results, executor=executor, loop=loop)
    builder = Builder(objs, operations, results, creds, path, options.input, loop=loop)
    for task in broker.tasks:
        func = getattr(broker, task)
        broker.tasks[task] = executor.submit(func)
        
    return builder

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
    operations = queue.Queue()
    results = queue.Queue()
    b = create_builder(objs, operations, results, args)
    log.debug(b)
    return 0


def run():
    p = maloja.cli.parser(description=__doc__)
    p = maloja.cli.add_common_options(p)
    p = maloja.cli.add_api_options(p)
    p = maloja.cli.add_builder_options(p)
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
