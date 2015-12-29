#!/usr/bin/env python
#   -*- encoding: UTF-8 -*-

from collections import namedtuple
import concurrent.futures
import logging
import functools
try:
    from functools import singledispatch
except ImportError:
    from singledispatch import singledispatch
import time
import warnings

import requests
from requests_futures.sessions import FuturesSession

from maloja.builder import Builder
from maloja.surveyor import Surveyor
from maloja.types import Credentials
from maloja.types import Design
from maloja.types import Plugin
from maloja.types import Status
from maloja.types import Stop
from maloja.types import Survey
from maloja.types import Token
from maloja.types import Workflow


@singledispatch
def handler(msg, path=None, queue=None, **kwargs):
    warnings.warn("No handler registered for {0}.".format(type(msg)))


@handler.register(Credentials)
def credentials_handler(msg, session, results=None, status=None, **kwargs):
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

    
@handler.register(Design)
def design_handler(
    msg, session, token,
    callback=None, results=None, status=None,
    **kwargs
):
    log = logging.getLogger("maloja.broker.design_handler")
    try:
        builder = Builder(msg.objects, results, session.executor)
    except Exception as e:
        log.error(str(getattr(e, "args", e) or e))
        return tuple()
    else:
        headers = {
            "Accept": "application/*+xml;version=5.5",
            token.key: token.value,
        }
        session.headers.update(headers)
        return (session.executor.submit(builder, session, token, callback, status),)


@handler.register(Stop)
def stop_handler(msg, session, token, **kwargs):
    log = logging.getLogger("maloja.broker.stop_handler")
    log.debug("Handling a stop.")
    return tuple()

 
@handler.register(Survey)
def survey_handler(msg, session, token, callback=None, results=None, status=None, **kwargs):
    log = logging.getLogger("maloja.broker.survey_handler")
    if msg.path.project and not any(msg.path[2:-1]):
        endpoints = [
            ("api/org", functools.partial(
                Surveyor.on_org_list, msg.path, results=results, status=status
                )
            )
        ]
    else:
        endpoints = [
            ("api/catalogs/query", None)
        ]
    rv = []
    for endpoint, callback in endpoints:
        #future = session.get(url, background_callback=bg_cb)
        log.debug("Scheduling  GET to {0}".format(endpoint))
        url = "{url}:{port}/{endpoint}".format(
            url=token.url,
            port=443,
            endpoint=endpoint)

        headers = {
            "Accept": "application/*+xml;version=5.5",
            token.key: token.value,
        }
        session.headers.update(headers)
        rv.append(session.get(url, background_callback=callback))
    return rv


@handler.register(Workflow)
def workflow_handler(
    msg, session, token,
    callback=None, results=None, status=None,
    **kwargs
):
    log = logging.getLogger("maloja.broker.workflow_handler")
    try:
        worker = msg.plugin.workflow(msg.paths, results, session.executor)
    except Exception as e:
        log.error(str(getattr(e, "args", e) or e))
        return tuple()
    else:
        headers = {
            "Accept": "application/*+xml;version=5.5",
            token.key: token.value,
        }
        session.headers.update(headers)
        return (session.executor.submit(worker, session, token, callback, status),)

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
                status = Status(id_, 1, 1)
                reply = None
                if isinstance(msg, Credentials):
                    ops = handler(msg, self.session)
                    tasks = concurrent.futures.wait(
                        ops, timeout=6,
                        return_when=concurrent.futures.FIRST_EXCEPTION
                    )
                    response = next(iter(tasks.done)).result(timeout=0)
                    if response.status_code == requests.codes.ok:
                        token = Token(time.time(), msg.url, "x-vcloud-authorization", None)
                        self.token = token._replace(value=response.headers.get(token.key))
                        reply = self.token
                    else:
                        reply = "Authentication failed."
                else:
                    log.debug(packet)
                    ops = handler(
                        msg, self.session, self.token,
                        results=self.results, status=status)
                    if ops:
                        tasks = concurrent.futures.wait(
                            ops, timeout=None,
                            return_when=concurrent.futures.FIRST_EXCEPTION
                        )
                        response = next(iter(tasks.done)).result(timeout=0)
            except Exception as e:
                log.error(str(getattr(e, "args", e) or e))
            finally:
                self.results.put((status, reply))
        else:
            return n

def create_broker(operations, results, max_workers=None, loop=None):
    executor = concurrent.futures.ThreadPoolExecutor(max_workers)
    broker = Broker(operations, results, executor=executor, loop=loop)
    for task in broker.tasks:
        func = getattr(broker, task)
        broker.tasks[task] = executor.submit(func)

    return broker
