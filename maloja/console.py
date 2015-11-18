#!/usr/bin/env python
#   -*- encoding: UTF-8 -*-

import cmd
import getpass
import logging
import queue
import sys
import uuid
import warnings

import concurrent.futures
from requests_futures.sessions import FuturesSession

from maloja.broker import Broker
from maloja.broker import Credentials
from maloja.broker import Stop
from maloja.broker import Survey

URL = 'http://localhost'
NUM = 3

class Console(cmd.Cmd):

    def __init__(self, operations, results, creds, *args, loop=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.operations = operations
        self.results = results
        self.creds = creds
        if loop is None:
            self.commands = queue.Queue()
        else:
            self.commands = asyncio.Queue(loop=loop)
        self.prompt = "Type 'help' for commands > "
        self.tasks = {
            "input_task": None,
            "command_task": None,
        }

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
        while not line.lower().startswith("quit"):
            if self.creds.password is None:
                password = getpass.getpass(prompt="Enter your API password: ")
                self.creds = self.creds._replace(password=password.strip())
                packet = (uuid.uuid4(), self.creds)
                self.operations.put(packet)
                log.debug(packet)
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
        while not line.lower().startswith("quit"):
            if self.creds.password is not None:
                sys.stdout.write(self.prompt)
                sys.stdout.flush()
            line = self.commands.get()
            n += 1
            try:
                line = self.precmd(line)
                msg = self.onecmd(line)
                if msg is not None:
                    packet = (uuid.uuid4(), msg)
                    self.operations.put(packet)
                    log.debug(packet)
                    #reply = yield from self.replies.get()
                stop = self.postcmd(msg, line)
                if stop:
                    break
            except Exception as e:
                print(e)
        else:
            log.debug("Closing command stream.")
            return n

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

        msg = Survey()
        packet = (uuid.uuid4(), msg)
        self.operations.put(packet)
        log.debug(packet)
        if not line:
            print("Your appliances:")
            print(*["{0:01}: {1}".format(i.id, i.name) for i in survey],
                    sep="\n")
            sys.stdout.write("\n")
        elif line.isdigit():
            app = survey[int(line)]
            msg = app
            return msg

    def do_quit(self, arg):
        """
        'Quit' ends the session.

        """
        return Stop()

class Surveyor:
    pass

def create_console(operations, results, options, loop=None):
    creds = Credentials(options.url, options.user, None)
    console = Console(operations, results, creds, loop=loop)
    executor = concurrent.futures.ThreadPoolExecutor(
        max(4, len(Broker.tasks) + len(console.tasks) + 2)
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

#session = FuturesSession()
#futures = {}

#logging.info('start')
#for n in range(NUM):
#    wibble = "%04d" % n
#    payload = { 
#        'name':'test',
#        'genNum':wibble,
#        'Button1':'Push+Now'
#    }
#    future = session.get( URL, data=payload )
#    futures[future] = payload

#logging.info('requests done, waiting for responses')

#for future in concurrent.futures.as_completed(futures, timeout=5):
#    res = future.result()
#    logging.info(
#        "wibble=%s, %s, %s bytes",
#        futures[future]['genNum'],
#        res,
#        len(res.text),
#    )

#logging.info('done!')
