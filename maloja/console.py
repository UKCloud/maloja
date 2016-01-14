#!/usr/bin/env python
#   -*- encoding: UTF-8 -*-

import cmd
from collections import OrderedDict
import getpass
import glob
import itertools
import logging
import os.path
import queue
import sys
import time
import warnings

import concurrent.futures

import ruamel.yaml

from maloja.broker import Broker
from maloja.broker import create_broker
from maloja.model import Catalog
from maloja.model import Org
from maloja.model import Template
from maloja.model import VApp
from maloja.model import Vdc
from maloja.model import Vm
from maloja.surveyor import Surveyor
from maloja.types import Token
from maloja.types import Credentials
from maloja.types import Stop
from maloja.types import Survey
from maloja.types import Workflow
from maloja.workflow.path import Path
from maloja.workflow.path import find_ypath
from maloja.workflow.path import split_to_path
from maloja.workflow.utils import plugin_interface

class Console(cmd.Cmd):

    tasks = {
        "input_task": None,
        "command_task": None,
        "results_task": None,
    }

    def __init__(self, operations, results, creds, ref, entry="", loop=None, **kwargs):
        super().__init__(**kwargs)
        self.operations = operations
        self.results = results
        self.creds = creds
        self.ref = ref
        self.entry = entry
        if loop is None:
            self.commands = queue.Queue()
        else:
            self.commands = asyncio.Queue(loop=loop)
        self.prompt = ""
        self.token = None
        self.stop = False
        self.seq = itertools.count(1)
        self.search = OrderedDict([])

    @property
    def routines(self):
        return []

    @staticmethod
    def get_command(prompt):
        line = sys.stdin.readline()
        if not len(line):
            line = "EOF"
        else:
            line = line.rstrip("\r\n")
        return line

    def input_task(self):
        log = logging.getLogger("maloja.console.input_task")
        n = 0
        line = ""
        while not self.stop:
            if self.token is None:
                password = getpass.getpass(prompt="Enter your API password: ")
                self.creds = self.creds._replace(password=password.strip())
                packet = (next(self.seq), self.creds)
                self.operations.put(packet)
                sys.stdout.write(self.prompt)
                sys.stdout.flush()
            line = self.get_command(self.prompt)
            n += 1
            self.commands.put(line)
        else:
            log.debug("Closing console input.")
            return n

    def command_task(self):
        log = logging.getLogger("maloja.console.command_task")
        n = 0
        line = ""
        self.preloop()
        while not self.stop:
            if self.creds.password is not None:
                sys.stdout.write(self.prompt)
                sys.stdout.flush()
            line = self.commands.get()
            n += 1
            try:
                line = self.precmd(line)
                msg = self.onecmd(line)
                if msg is not None:
                    packet = (next(self.seq), msg)
                    self.operations.put(packet)
                    log.debug(packet)
                self.stop = self.postcmd(msg, line)
                if self.stop:
                    break
            except Exception as e:
                print(e)
                raise
        else:
            log.debug("Closing command stream.")
            return n

    def results_task(self):
        log = logging.getLogger("maloja.console.results_task")
        n = 0
        while not self.stop:
            time.sleep(0)
            while True:
                try:
                    packet = self.results.get(block=True, timeout=2)
                    status, msg = packet
                except ValueError:
                    log.error(packet)
                except queue.Empty:
                    break
                n += 1
                if msg is None:
                    sys.stdout.write("\n[{0.id}] {0.level}:{0.job} complete.\n".format(status))
                elif isinstance(msg, Token):
                    self.token = msg
                    sys.stdout.write(
                        "\n[{0.id}] {0.level}:{0.job} Token received.\n".format(status)
                    )
                    self.prompt = "Type 'help' for commands > "
                elif isinstance(msg, str):
                    sys.stdout.write("\n[{0.id}] {1}\n".format(status, msg))
                else:
                    sys.stdout.write(
                        "\n[{0.id}] {1.__name__} received.\n".format(status, type(msg))
                    )
                sys.stdout.flush()
                sys.stdout.write(self.prompt)
                sys.stdout.flush()
        else:
            log.debug("Closing results stream.")
            sys.stdout.write("Press return.")
            sys.stdout.flush()
            return n

    def postcmd(self, msg, line):
        """Decides stop condition."""
        return line.lower().startswith("quit")

    def do_survey(self, arg):
        """
        'Survey' launches a survey over your cloud assets.

        """
        log = logging.getLogger("maloja.console.do_survey")
        line = arg.strip()

        msg = Survey(self.ref)
        packet = (next(self.seq), msg)
        self.operations.put(packet)

    def do_clear(self, arg):
        """
        Clears the search results.
        """
        self.search = OrderedDict([])
        print("Search results are now empty.")

    def do_plugin(self, arg):
        """
        'Plugin' lists plugins and their availability. Supply a number from
        that menu to invoke the plugin.

            > plugin
            (a list will be shown)

            > plugin 2

        """
        log = logging.getLogger("maloja.console.do_plugin")

        index = arg.strip()
        if not index.isdigit():
            index = None

        menu = list(dict(plugin_interface()).values())
        if index is not None:
            plugin = menu[int(index)]
            # TODO: Either:
            # * Invoke plugin directly (needs args passing), or
            # * Pass messages via broker

            msg = Workflow(plugin, self.search.values())
            packet = (next(self.seq), msg)
            self.operations.put(packet)
        else:
            print("Your plugins:")
            for n, plugin in enumerate(menu):
                paths = plugin.selector(*self.search.keys())
                if paths is plugin.workflow:
                    missing = None
                    tmplt = "{0:01}: {1.name} available."
                else:
                    missing = ", ".join(os.path.splitext(i.file)[0] for i in paths)
                    tmplt = "{0:01}: {1.name} missing {missing}"
                print(tmplt.format(n, plugin, missing=missing))
            sys.stdout.write("\n")

    def do_search(self, arg):
        """
        'Search' locates items by their attributes:

            > search org fullName=Dev
            > search vdc description=Skyscape
            > search template name=Windows
            > search vm ip=192.168.2.100

        """
        log = logging.getLogger("maloja.console.do_search")
        lookup = {i.__name__.lower(): i for i in (Catalog, Org, Template, VApp, Vdc, Vm)}
        try:
            bits = arg.strip().split()
            if bits[-1].isdigit():
                index = bits.pop(-1)
            else:
                index = None
        except IndexError:
            self.do_help("search")
            return

        try:
            name, spec = bits
        except ValueError:
            name, spec = bits[0], ""
        finally:
            if name not in lookup:
                print("Type {} not recognised.".format(name))
                return

        typ = lookup[name]

        try:
            key, value = [i.strip() for i in spec.split("=")]
            if key in ("name", "description", "fullName"):
                results = [
                    (path, obj)
                    for path, obj in find_ypath(self.ref, typ())
                    if value.lower() in getattr(obj, key, "").lower()
                ]
            else:
                results = list(find_ypath(self.ref, typ(), **{key: value}))
        except ValueError as e:
            key, value = "", ""
            results = list(find_ypath(self.ref, typ()))

        if len(results) > 1:
            if index is not None:
                path, obj = results[int(index)]
                self.search[obj] = path
            else:
                print("Your options:")
                print(
                    *[
                        "{0:01}: {1}".format(n, getattr(obj, "name", obj))
                        for n, (path, obj) in enumerate(results)
                    ],
                    sep="\n"
                )
                sys.stdout.write("\n")
        elif results:
            self.search[results[0][1]] = results[0][0]
        else:
            print("No matches for pattern {}".format(spec))

        print("Search results:\n")
        print(*[vars(obj) for obj in self.search], sep="\n")

    def do_quit(self, arg):
        """
        'Quit' ends the session.

        """
        return Stop()


def create_console(operations, results, options, path, loop=None):
    n = max(16, len(Broker.tasks) + len(Console.tasks) + len(path))
    broker = create_broker(operations, results, max_workers=n, loop=loop)

    creds = Credentials(options.url, options.user, None)
    console = Console(operations, results, creds, path, options.output, loop=loop)
    if loop is not None:
        # launch asyncio coroutines
        for coro in console.routines:
            loop.create_task(coro(executor, loop=loop))
    else:
        for task in console.tasks:
            func = getattr(console, task)
            console.tasks[task] = broker.session.executor.submit(func)

    return console
