#!/usr/bin/env python
#   -*- encoding: UTF-8 -*-

import concurrent.futures
import getpass
import itertools
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
from maloja.types import Stop
from maloja.workflow.utils import group_by_type


__doc__ = """
The builder module modifies cloud assets according to a design file.

"""

# Send a Design to the broker.
# Add Broker handler

class Builder:

    def __init__(self, objs, operations, results, path, executor=None, loop=None, **kwargs):
        log = logging.getLogger("maloja.builder.Builder")
        self.plans = group_by_type(objs)
        self.operations = operations
        self.results = results
        self.token = None
        self.seq = itertools.count(1)
        self.tasks = []

    def __call__(self, session, creds, callback=None, status=None, **kwargs):
        log = logging.getLogger("maloja.builder")
        if self.token is None:
            password = getpass.getpass(prompt="Enter your API password: ")
            creds = creds._replace(password=password.strip())
            packet = (next(self.seq), creds)
            self.operations.put(packet)
            sys.stdout.flush()

        packet = (next(self.seq), Stop())
        self.operations.put(packet)

def create_builder(objs, operations, results, options, path=tuple(), loop=None):
    creds = Credentials(options.url, options.user, None)
    executor = concurrent.futures.ThreadPoolExecutor(
        max(4, len(Broker.tasks) + 2 * len(path))  # TODO: Declare builder tasks
    )
    broker = Broker(operations, results, executor=executor, loop=loop)
    builder = Builder(objs, operations, results, path, options.input, loop=loop)
    for task in broker.tasks:
        func = getattr(broker, task)
        builder.tasks.append(executor.submit(func))

    builder.tasks.append(executor.submit(builder(broker.session, creds))) 
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
    builder = create_builder(objs, operations, results, args)
    results = [
        i.result()
        for i in concurrent.futures.as_completed(set(builder.tasks))
        if i.done()
    ]
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
