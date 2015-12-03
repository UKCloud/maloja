#!/usr/bin/env python
#   -*- encoding: UTF-8 -*-

import unittest

from maloja.plugin.vapplicator import plugin
from maloja.workflow.utils import Path

class SelectorTester(unittest.TestCase):

    def test_one_vapp_required(self):
        path = Path("root", "proj", "org", "vdc", "vapp", None, "vapp.yml")
        self.assertIsInstance(plugin.selector(), list)
        self.assertIs(plugin.selector.workflow, plugin.selector(path))
