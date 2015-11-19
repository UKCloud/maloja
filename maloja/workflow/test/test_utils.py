#!/usr/bin/env python
#   -*- encoding: UTF-8 -*-

from __future__ import print_function
from __future__ import unicode_literals

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
import os.path
import shutil
import tempfile
import unittest

import ruamel.yaml

import maloja.workflow.utils


class RecordTests(unittest.TestCase):

    def setUp(self):
        self.drcty = tempfile.TemporaryDirectory()

    def tearDown(self):
        if os.path.isdir(self.drcty.name):
            self.drcty.cleanup()
        self.assertFalse(os.path.isdir(self.drcty.name))
        self.drcty = None

    def test_content_goes_to_named_file(self):
        record = "node.yaml"
        fP = os.path.join(self.drcty.name, record)
        self.assertFalse(os.path.isfile(fP))
        with maloja.workflow.utils.record(record, parent=self.drcty.name) as output:
            output.write(ruamel.yaml.dump("Test string"))

        self.assertTrue(os.path.isfile(fP))
        with open(fP, 'r') as check:
            self.assertEqual("Test string\n...", check.read().strip())

    def test_content_goes_to_file_object(self):
        fObj = StringIO()
        with maloja.workflow.utils.record(fObj, parent=self.drcty.name) as output:
            output.write(ruamel.yaml.dump("Test string"))

        self.assertEqual("Test string\n...", fObj.getvalue().strip())
