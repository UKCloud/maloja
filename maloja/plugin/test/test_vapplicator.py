#!/usr/bin/env python
#   -*- encoding: UTF-8 -*-

import unittest

from maloja.model import Template
from maloja.model import Vm
from maloja.plugin.vapplicator import plugin
from maloja.workflow.utils import Path

class SelectorTester(unittest.TestCase):

    def test_one_template_required(self):
        obj = Template()
        rv = plugin.selector(obj)
        self.assertIsInstance(rv, list)
        self.assertEqual(1, len(rv))
        self.assertEqual("vm.yaml", rv[0].file)

    def test_one_vm_required(self):
        obj = Vm()
        rv = plugin.selector(obj)
        self.assertIsInstance(rv, list)
        self.assertEqual(1, len(rv))
        self.assertEqual("template.yaml", rv[0].file)

    def test_match(self):
        objs = [Template(), Vm()]
        self.assertIs(plugin.workflow, plugin.selector(*objs))
