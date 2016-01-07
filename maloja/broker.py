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
def handler(msg, session, token, results=None, status=None, **kwargs):
    """
    The Broker provides this handler to dispatch messages it
    receives to functions which know how to execute them.

    This design allows new modules to be implemented and to register
    functions for receipt of specific message types.

    Every handler function receives these positional arguments:

    :param msg: the message object.
    :param session: a *requests.futures* session object.
    :param token: an authorization Token for the VMware API.
    :param results: a queue object so your handler can send back
        status messages.
    :param status: the current status at the point your handler
        is invoked.
    """
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


# TODO: Move to builder module
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


# TODO: Move to surveyor module
@handler.register(Survey)
def survey_handler(msg, session, token, callback=None, results=None, status=None, **kwargs):
    log = logging.getLogger("maloja.broker.survey_handler")
    if msg.path.project and not any(msg.path[2:-1]):
        endpoints = [
            (
                "api/org",
                functools.partial(
                    Surveyor.on_org_list,
                    msg.path,
                    results=results,
                    status=status
                )
            )
        ]
    else:
        endpoints = [
            ("api/catalogs/query", None)
        ]
    rv = []
    for endpoint, callback in endpoints:
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
    """
    The Broker manages all Maloja's interactions with the VMware API.
    It is responsible for taking messages from an *operations* queue
    and initiating an action for each one.

    The Broker caches your API authorization token. It also maintains
    a *requests* session with the API.

    The best way to create a Broker object is with the
    :py:func:`maloja.broker.create_broker` function.

    """

    tasks = {
        "operation_task": None,
    }
    """
    A Broker is an active object. The tasks it runs in the background
    of your program are stored in this dictionary.

    To wait for a Broker to finish takes code like this::

        tasks = concurrent.futures.wait(set(broker.tasks.values()))
    """

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
    """
    :param operations: a queue object. Push operations to this queue.
    :param results: a queue object. Get results from this queue.
    :param max_workers: the number of threads to use in the executor
        pool. Leave this as `None` to get a sensible default value.
    :param loop: an asyncio loop object. *Not implemented*.
    :return: A new Broker object
    """
    executor = concurrent.futures.ThreadPoolExecutor(max_workers)
    broker = Broker(operations, results, executor=executor, loop=loop)
    for task in broker.tasks:
        func = getattr(broker, task)
        broker.tasks[task] = executor.submit(func)

    return broker
