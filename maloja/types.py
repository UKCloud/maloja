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

from collections import namedtuple

Credentials = namedtuple("Credentials", ["url", "user", "password"])
Design = namedtuple("Design", ["objects"])
Inspection = namedtuple("Inspection", ["name", "objects"])

Plugin = namedtuple(
    "Plugin",
    ["name", "description", "selector", "workflow"]
)
"""
This data structure describes a Maloja plugin. It is the type
expected by the `maloja.plugin` interface.

"""

Status = namedtuple("Status", ["id", "job", "path"])
Stop = namedtuple("Stop", [])
Survey = namedtuple("Survey", ["path"])
Token = namedtuple("Token", ["t", "url", "key", "value"])
Workflow = namedtuple("Workflow", ["plugin", "paths"])
