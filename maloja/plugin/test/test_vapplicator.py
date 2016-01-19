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

from maloja.model import Template
from maloja.model import Vdc
from maloja.model import Vm
from maloja.plugin.vapplicator import plugin
from maloja.workflow.path import Path

class SelectorTester(unittest.TestCase):

    def test_one_template_required(self):
        obj = Template()
        rv = plugin.selector(obj)
        self.assertIsInstance(rv, list)
        self.assertEqual(2, len(rv))
        self.assertEqual("vdc.yaml", rv[0].file)
        self.assertEqual("vm.yaml", rv[1].file)

    def test_one_vdc_required(self):
        obj = Vdc()
        rv = plugin.selector(obj)
        self.assertIsInstance(rv, list)
        self.assertEqual(2, len(rv))
        self.assertEqual("vm.yaml", rv[0].file)
        self.assertEqual("template.yaml", rv[1].file)

    def test_one_vm_required(self):
        obj = Vm()
        rv = plugin.selector(obj)
        self.assertIsInstance(rv, list)
        self.assertEqual(2, len(rv))
        self.assertEqual("vdc.yaml", rv[0].file)
        self.assertEqual("template.yaml", rv[1].file)

    def test_match(self):
        objs = [Template(), Vdc(), Vm()]
        self.assertIs(plugin.workflow, plugin.selector(*objs))
