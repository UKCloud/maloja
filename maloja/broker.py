#!/usr/bin/env python
#   -*- encoding: UTF-8 -*-

from collections import namedtuple
import logging

Credentials = namedtuple("Credentials", ["url", "user", "password"])
Stop = namedtuple("Stop", [])

class Broker:

    def __init__(self, operations, results, *args, loop=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.operations = operations
        self.results = results
        self.tasks = {
            "operation_task": None,
        }

    @property
    def routines(self):
        return []

    def operation_task(self):
        log = logging.getLogger("maloja.broker.operation_task")
        n = 0
        msg = object()
        while not isinstance(msg, Stop):
            packet = self.operations.get()
            n += 1
            log.debug(packet)
            id_, msg = packet
        else:
            return n

