#!/usr/bin/env python
#   -*- encoding: UTF-8 -*-

# Copyright Skyscape Cloud Services
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import concurrent.futures
import itertools
import logging
import sys
import time
import uuid
import warnings
import xml.etree.ElementTree as ET

from maloja.builder import Builder
from maloja.model import Gateway
from maloja.model import Network
from maloja.model import Task
from maloja.model import Template
from maloja.model import VApp
from maloja.model import Vdc
from maloja.model import Vm
from maloja.planner import check_objects
from maloja.planner import read_objects
from maloja.types import Credentials
from maloja.types import Stop
from maloja.workflow.utils import find_xpath
from maloja.workflow.utils import group_by_type


class Inspector:
    """
    The Inspector accepts a sequence of objects from the
    :ref:`data model <data model>` and uses them to check
    existing virtual infrastructure.

    """

    def __init__(self, objs, results, executor=None, loop=None, **kwargs):
        """
        :param objs: a sequence of Maloja objects
        :param results: a queue to which status reports will be pushed
        :param executor: a `concurrent.futures.Executor` object

        """
        log = logging.getLogger("maloja.inspector.Inspector")
        self.plans = group_by_type(objs)
        self.results = results
        self.executor = executor
        self.token = None
        self.tasks = {}
        self.seq = itertools.count(1)

    def __call__(self, session, token, callback=None, status=None, **kwargs):
        """
        An Inspector is a callable object which runs in its own thread.

        It gets started up like this::

            executor.submit(inspector, session, token, callback, status)

        :param session: a *requests.futures* session object.
        :param token: an authorization Token for the VMware API.
        :param callback: a function to be called when
            the inspector is done.
        :param status: the current status at the point the inspector
            is invoked.

        """
        log = logging.getLogger("maloja.inspector")
