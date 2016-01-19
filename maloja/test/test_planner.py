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

import unittest

import pkg_resources

from maloja.model import Vm
from maloja.planner import read_objects
from maloja.workflow.utils import group_by_type


class PlannerTests(unittest.TestCase):

    def test_first_object_supplies_defaults(self):
        design = pkg_resources.resource_string(
                "maloja.test", "use_case01.yaml"
            )
        objs = group_by_type(read_objects(design))
        self.assertEqual(2, len(objs[Vm]))
        self.assertEqual(objs[Vm][0].href, objs[Vm][1].href)
