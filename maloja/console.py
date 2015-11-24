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

URL = 'http://localhost'
NUM = 3

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
        self.selection = OrderedDict()

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
                    #reply = yield from self.replies.get()
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
            id_, msg = self.results.get(block=True, timeout=None)
            n += 1
            if isinstance(msg, Token):
                self.token = msg
                self.prompt = "Type 'help' for commands > "
            if isinstance(msg, str):
                sys.stdout.write("\n[{0}] {1}\n".format(id_, msg))
            else:
                sys.stdout.write("\n[{0}] {1.__name__} received.\n".format(id_, type(msg)))
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
        survey = []

        msg = Survey(self.project)
        packet = (next(self.seq), msg)
        self.operations.put(packet)
        log.debug(packet)
        if not line:
            #print("Your appliances:")
            print(*["{0:01}: {1}".format(i.id, i.name) for i in survey],
                    sep="\n")
            #sys.stdout.write("\n")
        elif line.isdigit():
            app = survey[int(line)]
            msg = app
            return msg

    def do_select(self, arg):
        log = logging.getLogger("maloja.console.do_survey")
        name, spec = arg.strip().split()
        try:
            locn, criteria = spec.split(":")
        except ValueError:
            locn = spec.strip()
            criteria = ""
        try:
            key, value = criteria.split("=")
        except ValueError:
            key = value = None
        hits = glob.glob(
            os.path.join(self.project.root, self.project.project, "*", locn, "*.yaml")
        )
        objs = []
        for hit in hits:
            with open(hit, 'r') as data:
                obj = ruamel.yaml.load(data.read())
                if not (key or value) or value.strip() in getattr(obj, key.strip()): 
                    objs.append(obj)

        if len(objs) > 1:
            print("Your options:")
            print(*["{0:01}: {1}".format(n, i.name) for n, i in enumerate(objs)],
                    sep="\n")
            sys.stdout.write("\n")
        elif objs:
            print(objs[0])
        else:
            print("No matches for pattern {}".format(spec))

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
