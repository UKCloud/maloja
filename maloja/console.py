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
from maloja.broker import Token
from maloja.broker import Credentials
from maloja.broker import Stop
from maloja.broker import Survey
from maloja.model import Catalog
from maloja.model import Org
from maloja.model import Template
from maloja.model import VApp
from maloja.model import Vdc
from maloja.model import Vm
from maloja.surveyor import yaml_loads


class Console(cmd.Cmd):

    def __init__(self, operations, results, creds, path, *args, loop=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.operations = operations
        self.results = results
        self.creds = creds
        self.project = path
        if loop is None:
            self.commands = queue.Queue()
        else:
            self.commands = asyncio.Queue(loop=loop)
        self.prompt = ""
        self.tasks = {
            "input_task": None,
            "command_task": None,
            "results_task": None,
        }
        self.token = None
        self.stop = False
        self.seq = itertools.count(1)
        self.search = set([])

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
                    sys.stdout.write("\n[{0.id}] {0.level}:{0.job} Token received.\n".format(status))
                    self.prompt = "Type 'help' for commands > "
                elif isinstance(msg, str):
                    sys.stdout.write("\n[{0.id}] {1}\n".format(status, msg))
                else:
                    sys.stdout.write("\n[{0.id}] {1.__name__} received.\n".format(status, type(msg)))
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
        'Survey' lists the VApps you can see. Add a number from
        that menu to survey a specific item, eg::
            
            > survey
            (a list will be shown)

            > survey 3
        """
        log = logging.getLogger("maloja.console.do_survey")
        line = arg.strip()

        msg = Survey(self.project)
        packet = (next(self.seq), msg)
        self.operations.put(packet)

    def do_clear(self, arg):
        """
        Clears the search results.
        """
        self.search = set([])
        print("Search results are now empty.")

    def do_search(self, arg):
        """
            > search org fullName=Dev
            > search vdc description=Skyscape
            > search template name=Windows
            > search vm ip=192.168.2.100

        """
        log = logging.getLogger("maloja.console.do_search")
        patterns = {
            "org": (Org, "*/org.yaml"),
            "catalog": (Catalog, "*/*/catalog.yaml"),
            "vdc": (Vdc, "*/*/vdc.yaml"),
            "vapp": (VApp, "*/*/*/vapp.yaml"),
            "template": (Template, "*/*/*/template.yaml"),
            "vm": (Vm, "*/*/*/*/vm.yaml"),
        }

        bits = arg.strip().split()
        if bits[-1].isdigit():
            index = bits.pop(-1)
        else:
            index = None

        try:
            name, spec = bits
        except ValueError:
            name, spec = bits[0], ""

        try:
            key, value = spec.split("=")
        except ValueError:
            key, value = "", ""

        typ, pattern = patterns[name]
        hits = glob.glob(
            os.path.join(self.project.root, self.project.project, pattern)
        )
        objs = []
        for hit in hits:
            with open(hit, 'r') as data:
                obj = typ(**yaml_loads(data.read()))
                if obj is None:
                    continue
                if not key: 
                    objs.append(obj)
                    continue
                else:
                    data = dict(
                        [(k, getattr(item, k))
                        for seq in [
                            i for i in vars(obj).values() if isinstance(i, list)
                        ]
                        for item in seq
                        for k in getattr(item, "_fields", [])],
                        **vars(obj))
                    match = data.get(key.strip(), "")
                    if value.strip() in str(match):
                        objs.append(obj)
                        continue

        if len(objs) > 1:
            if index is not None:
                self.search.add(objs[int(index)])
            else:
                print("Your options:")
                print(*["{0:01}: {1}".format(n, i.name) for n, i in enumerate(objs)],
                        sep="\n")
                sys.stdout.write("\n")
        elif objs:
            self.search.add(objs[0])
        else:
            print("No matches for pattern {}".format(spec))

        print("Search results:\n")
        print(*[vars(i) for i in self.search], sep="\n")

    def do_quit(self, arg):
        """
        'Quit' ends the session.

        """
        return Stop()


def create_console(operations, results, options, path, loop=None):
    creds = Credentials(options.url, options.user, None)
    console = Console(operations, results, creds, path, loop=loop)
    executor = concurrent.futures.ThreadPoolExecutor(
        max(4, len(Broker.tasks) + len(console.tasks) + 2 * len(path))
    )
    broker = Broker(operations, results, executor=executor, loop=loop)
    if loop is not None:
        # launch asyncio coroutines
        for coro in console.routines:
            loop.create_task(coro(executor, loop=loop))
    else:
        # launch looping threads
        for task in broker.tasks:
            func = getattr(broker, task)
            broker.tasks[task] = executor.submit(func)
            
        for task in console.tasks:
            func = getattr(console, task)
            console.tasks[task] = executor.submit(func)
            
    return console
