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


try:
    import asyncio
except ImportError:
    asyncio = None
import concurrent.futures
import getpass
import logging
from logging.handlers import WatchedFileHandler
import os
import os.path
import queue
import sys
import time
import warnings

import maloja.cli
import maloja.broker
import maloja.console
import maloja.surveyor
import maloja.planner
from maloja.types import Credentials
from maloja.types import Design
from maloja.types import Status
from maloja.types import Stop
from maloja.types import Survey
from maloja.types import Token
from maloja.workflow.path import Path
from maloja.workflow.path import make_project
from maloja.workflow.path import find_project

__doc__ = """
start %HOME%\\maloja-py3.5\\scripts\\python -m maloja.main
@options.private build --input=maloja\\test\\use_case01.yaml
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
    if not os.listdir(args.output):
        log.info("No projects detected.")
        path, proj = make_project(args.output)
        log.info("Created {0}.".format(path.project))

    path, proj = find_project(args.output)
    log.info("Using project {0}.".format(path.project))

    maloja.broker.handler.register(
        Survey, maloja.surveyor.Surveyor.survey_handler
    )

    if not args.command:
        console = maloja.console.create_console(operations, results, args, path, loop=loop)
        results = [
            i.result()
            for i in concurrent.futures.as_completed(set(console.tasks.values()))
            if i.done()
        ]
        return 0

    elif args.command == "plan":
        with open(args.input, "r") as data:
            return maloja.planner.report(data)

    # Other commands require a broker
    broker = maloja.broker.create_broker(operations, results, max_workers=64, loop=loop)

    reply = None
    while not isinstance(reply, Token):
        password = getpass.getpass(prompt="Enter your API password: ")
        creds = Credentials(args.url, args.user, password.strip())
        operations.put((0, creds))
        status, reply = results.get()

    if args.command == "survey":
        operations.put((1, Survey(path)))

    elif args.command == "build":
        objs = []
        with open(args.input, "r") as data:
            objs = list(maloja.planner.read_objects(data.read()))
            objs = maloja.planner.check_objects(objs)

        operations.put((1, Design(objs)))

    while not isinstance(reply, Stop):
        try:
            status, reply = results.get(block=True, timeout=30)
        except queue.Empty:
            break
        else:
            if isinstance(status, Status):
                level = os.path.splitext(getattr(status.path, "file", ""))[0]
                log.info("{0:^10} update {1.job:04}".format(level, status))
            if reply is not None:
                log.info(reply)
            time.sleep(0)

    operations.put((2, Stop()))
    time.sleep(1)

    done, not_done = tasks = concurrent.futures.wait(
        set(broker.tasks.values()), timeout=6,
        return_when=concurrent.futures.FIRST_EXCEPTION
    )
    for task in not_done:
        log.warning("Not completed: {0}".format(task))
        log.debug(task.cancel())
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
