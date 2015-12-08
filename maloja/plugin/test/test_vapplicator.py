#!/usr/bin/env python
#   -*- encoding: UTF-8 -*-

import unittest

from maloja.model import Template
from maloja.model import Vdc
from maloja.model import Vm
from maloja.plugin.vapplicator import plugin
from maloja.workflow.utils import Path

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
