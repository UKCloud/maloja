#!/usr/bin/env python
#   -*- encoding: UTF-8 -*-

try:
    import asyncio
except ImportError:
    asyncio = None
import concurrent.futures
import getpass
import logging
from logging.handlers import WatchedFileHandler
import os
import queue
import sys
import warnings

import maloja.cli
import maloja.broker
import maloja.console
import maloja.planner
from maloja.types import Credentials
from maloja.types import Design
from maloja.types import Stop
from maloja.types import Token
from maloja.workflow.utils import Path
from maloja.workflow.utils import make_path
from maloja.workflow.utils import recent_project

__doc__ = """
start %HOME%\\maloja-py3.5\\scripts\\python -m maloja.main @options.private build --input=maloja\\test\\use_case01.yaml
"""

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

    asyncio = None  # TODO: Tox testing
    try:
        loop = asyncio.SelectorEventLoop()
        asyncio.set_event_loop(loop)
        operations = asyncio.Queue(loop=loop)
        results = asyncio.Queue(loop=loop)
    except AttributeError:
        loop = None
        operations = queue.Queue()
        results = queue.Queue()

    os.makedirs(args.output, exist_ok=True)
    path = Path(args.output, None, None, None, None, None, "project.yaml")
    try:
        path = make_path(recent_project(path))
    except Exception as e:
        log.error(e)

    if args.command == "build":
        objs = []
        broker = maloja.broker.create_broker(operations, results, max_workers=12, loop=loop)

        with open(args.input, "r") as data:
            objs = list(maloja.planner.read_objects(data.read()))
            objs = maloja.planner.check_objects(objs)

        reply = None
        while not isinstance(reply, Token):
            password = getpass.getpass(prompt="Enter your API password: ")
            creds = Credentials(args.url, args.user, password.strip())
            operations.put((0, creds))
            status, reply = results.get()

        operations.put((1, Design(objs)))

        while not isinstance(reply, Stop):
            status, reply = results.get()
            log.info(status)
            log.info(reply)
        else:
            operations.put((2, reply))

        results = [
            i.result()
            for i in concurrent.futures.as_completed(set(broker.tasks.values()))
            if i.done()
        ]

    else:
        console = maloja.console.create_console(operations, results, args, path, loop=loop)
        results = [
            i.result()
            for i in concurrent.futures.as_completed(set(console.tasks.values()))
            if i.done()
        ]

    return 0


def run():
    p, subs = maloja.cli.parsers()
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
