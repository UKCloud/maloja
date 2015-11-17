#!/usr/bin/env python
#   -*- encoding: UTF-8 -*-

try:
    import asyncio
except ImportError:
    asyncio = None
import cmd
import logging
import queue
import sys
import warnings

import concurrent.futures
from requests_futures.sessions import FuturesSession

URL = 'http://localhost'
NUM = 3

logging.basicConfig(
    stream=sys.stderr, level=logging.INFO,
    format='%(name)s %(relativeCreated)s %(message)s',
    )

class Broker:
    pass

class Console(cmd.Cmd):

    def __init__(self, operations, results, *args, loop=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.operations = operations
        self.results = results
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
        line = ""
        while not line.lower().startswith("quit"):
            log.info("Eh?")
            line = self.get_command(self.prompt)
            self.commands.put(line)
            log.info("OK!")
 
    def command_task(self):
        log = logging.getLogger("maloja.console.command_task")
        line = ""
        self.preloop()
        while not line.lower().startswith("quit"):
            sys.stdout.write(self.prompt)
            sys.stdout.flush()
            line = self.commands.get()
            try:
                line = self.precmd(line)
                msg = self.onecmd(line)
                if msg is not None:
                    self.operations.put(msg)
                    #reply = yield from self.replies.get()
                stop = self.postcmd(msg, line)
                if stop:
                    # TODO: Send 'stop' msg to broker
                    break
            except Exception as e:
                print(e)

class Surveyor:
    pass

def create_console(operations, results, loop=None):
    console = Console(operations, results, loop=loop)
    executor = concurrent.futures.ThreadPoolExecutor(
        max(4, len(console.tasks) + 1)
    )
    if loop is not None:
        # launch asyncio coroutines
        for coro in console.routines:
            loop.create_task(coro(executor, loop=loop))
    else:
        # launch looping threads
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

def main(args):

    asyncio = None
    try:
        loop = asyncio.SelectorEventLoop()
        asyncio.set_event_loop(loop)
        operations = asyncio.Queue(loop=loop)
        results = asyncio.Queue(loop=loop)
    except AttributeError:
        loop = None
        operations = queue.Queue()
        results = queue.Queue()

    console = create_console(operations, results, loop=loop)
    for future in concurrent.futures.as_completed(set(console.tasks.values())):
        print(future.result())

if __name__ == "__main__":
    rv = main(None)
    sys.exit(rv)
