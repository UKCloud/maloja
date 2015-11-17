#!/usr/bin/env python
#   -*- encoding: UTF-8 -*-

try:
    import asyncio
except ImportError:
    asyncio = None
import concurrent.futures
import logging
from logging.handlers import WatchedFileHandler
import queue
import sys
import warnings

import maloja.cli
import maloja.console


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

    console = maloja.console.create_console(operations, results, loop=loop)
    results = [
        i.result()
        for i in concurrent.futures.as_completed(set(console.tasks.values()))
    ]
    if max(results) != min(results):
        warnings.warn("Some commands, operations or results were missed.")
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
