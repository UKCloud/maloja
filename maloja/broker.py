#!/usr/bin/env python
#   -*- encoding: UTF-8 -*-

from collections import namedtuple
import concurrent.futures
import logging
try:
    from functools import singledispatch
except ImportError:
    from singledispatch import singledispatch
import time
import warnings

import requests
from requests_futures.sessions import FuturesSession

Credentials = namedtuple("Credentials", ["url", "user", "password"])
Stop = namedtuple("Stop", [])
Survey = namedtuple("Survey", [])
Token = namedtuple("Token", ["t", "url", "key", "value"])

@singledispatch
def handler(msg, path=None, queue=None, **kwargs):
    warnings.warn("No handler registered for {0}.".format(type(msg)))

@handler.register(Credentials)
def credentials_handler(msg, session):
    log = logging.getLogger("maloja.broker.credentials_handler")
    log.debug("Handling credentials.")
    url = "{url}:{port}/{endpoint}".format(
        url=msg.url,
        port=443,
        endpoint="api/sessions")

    headers = {
        "Accept": "application/*+xml;version=5.5",
    }
    session.headers.update(headers)
    session.auth = (msg.user, msg.password)
    future = session.post(url)
    return (future,)
    
@handler.register(Stop)
def stop_handler(msg, session, token):
    log = logging.getLogger("maloja.broker.stop_handler")
    log.debug("Handling a stop.")
    return tuple()
    
@handler.register(Survey)
def survey_handler(msg, session, token, callback=None):
    log = logging.getLogger("maloja.broker.survey_handler")
    log.debug("Handling a survey.")
    #future = session.get(url, background_callback=bg_cb)
    url = "{url}:{port}/{endpoint}".format(
        url=token.url,
        port=443,
        endpoint="api/catalogs/query")

    headers = {
        "Accept": "application/*+xml;version=5.5",
        token.key: token.value,
    }
    session.headers.update(headers)
    future = session.get(url)
    return (future,)

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
                id_, msg = packet
                reply = None
                if isinstance(msg, Credentials):
                    ops = handler(msg, self.session)
                    results = concurrent.futures.wait(
                        ops, timeout=6,
                        return_when=concurrent.futures.FIRST_EXCEPTION
                    )
                    response = next(iter(results.done)).result(timeout=0)
                    # TODO: Handle failure modes and results.not_done
                    #if response.status_code == requests.codes.ok:
                    log.info(response.status_code)
                    token = Token(time.time(), msg.url, "x-vcloud-authorization", None)
                    self.token = token._replace(value=response.headers.get(token.key))
                    reply = self.token
                else:
                    log.debug(packet)
                    ops = handler(msg, self.session, self.token)
                    results = concurrent.futures.wait(
                        ops, timeout=6,
                        return_when=concurrent.futures.FIRST_EXCEPTION
                    )
                    response = next(iter(results.done)).result(timeout=0)
                    reply = response.text
                    # TODO: Handle failure modes and results.not_done
            except Exception as e:
                log.error(str(getattr(e, "args", e) or e))
            finally:
                self.results.put((id_, reply))
        else:
            return n

    def on_complete(self, session, response):
        # Example of a callback
        # parse the json storing the result on the response object
        response.data = response.json()

