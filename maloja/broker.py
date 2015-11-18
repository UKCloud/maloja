#!/usr/bin/env python
#   -*- encoding: UTF-8 -*-

from collections import namedtuple
import logging
try:
    from functools import singledispatch
except ImportError:
    from singledispatch import singledispatch
import warnings

from requests_futures.sessions import FuturesSession

Credentials = namedtuple("Credentials", ["url", "user", "password"])
Stop = namedtuple("Stop", [])
Survey = namedtuple("Survey", [])

@singledispatch
def handler(msg, path=None, queue=None, **kwargs):
    warnings.warn("No handler registered for {0}.".format(type(msg)))

@handler.register(Credentials)
def credentials_handler(msg, session, path, queue):
    log = logging.getLogger("maloja.broker.credentials_handler")
    log.info("Handling credentials.")
    url = "{url}:{port}/{endpoint}".format(
        url=msg.url,
        port=443,
        endpoint="api/sessions")

    headers = {
        "Accept": "application/*+xml;version=5.5",
    }
    session.headers.update(headers)
    #future = session.get(url, background_callback=bg_cb)
    future = session.get(url)
    return (future,)
    
@handler.register(Stop)
def stop_handler(msg, path, queue):
    log = logging.getLogger("maloja.broker.stop_handler")
    log.info("Handling a stop.")
    
@handler.register(Survey)
def stop_handler(msg, path, queue):
    log = logging.getLogger("maloja.broker.survey_handler")
    log.info("Handling a survey.")

def bg_cb(sess, resp):
    # parse the json storing the result on the response object
    resp.data = resp.json()

class Broker:

    tasks = {
        "operation_task": None,
    }

    def __init__(self, operations, results, *args, executor=None, loop=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.operations = operations
        self.results = results
        self.token = None
        self.session = FuturesSession(executor=executor)

    @property
    def routines(self):
        return []

    def operation_task(self):
        log = logging.getLogger("maloja.broker.operation_task")
        n = 0
        msg = object()
        while not isinstance(msg, Stop):
            try:
                packet = self.operations.get()
                n += 1
                log.debug(packet)
                id_, msg = packet
                if isinstance(msg, Credentials):
                    for op in handler(msg, self.session, None, None):
                        log.info(op.result(timeout=6))
                else:
                    futures = Broker.handler(msg, None, None)
            except Exception as e:
                log.error(str(getattr(e, "args", e) or e))
        else:
            return n

