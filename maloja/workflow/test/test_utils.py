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

from maloja.workflow.utils import Path
from maloja.workflow.utils import make_path
from maloja.workflow.utils import recent_project
from maloja.workflow.utils import record


class NeedsTempDirectory:

    def setUp(self):
        self.drcty = tempfile.TemporaryDirectory()

    def tearDown(self):
        if os.path.isdir(self.drcty.name):
            self.drcty.cleanup()
        self.assertFalse(os.path.isdir(self.drcty.name))
        self.drcty = None

class PathTests(NeedsTempDirectory, unittest.TestCase):

    def test_nodirectory_recent(self):
        try:
            FileNotFoundError
        except NameError:
            FileNotFoundError = OSError

        drcty = tempfile.TemporaryDirectory()
        path = Path(
            drcty.name,
            None, None, None, None, None, None
        )
        drcty.cleanup()
        self.assertFalse(os.path.isdir(drcty.name))
        self.assertRaises(FileNotFoundError, recent_project, path)

    def test_nodirectory_make_path(self):
        drcty = tempfile.TemporaryDirectory()
        path = Path(
            drcty.name,
            None, None, None, None, None, None
        )
        drcty.cleanup()
        self.assertFalse(os.path.isdir(drcty.name))
        path = make_path(path)
        self.assertTrue(os.path.isdir(drcty.name))
        self.assertEqual(drcty.name, path.root)

    def test_nodirectory_make_project(self):
        drcty = tempfile.TemporaryDirectory()
        path = Path(
            drcty.name,
            None, None, None, None, None,
            "project.yaml"
        )
        drcty.cleanup()
        self.assertFalse(os.path.isdir(drcty.name))
        path = make_path(path)
        self.assertTrue(os.path.isdir(drcty.name))
        self.assertEqual(drcty.name, path.root)

    def test_nodirectory_recent_project(self):
        drcty = tempfile.TemporaryDirectory()
        path = Path(
            drcty.name,
            None, None, None, None, None,
            "project.yaml"
        )
        drcty.cleanup()
        self.assertFalse(os.path.isdir(drcty.name))
        path = make_path(recent_project(make_path(path)))
        self.assertTrue(os.path.isdir(drcty.name))
        self.assertEqual(drcty.name, path.root)
        self.assertTrue(path.project)

    def test_noproject_recent_project(self):
        path = Path(
            self.drcty.name,
            None, None, None, None, None,
            "project.yaml"
        )
        path = make_path(recent_project(make_path(path)))
        self.assertTrue(os.path.isdir(self.drcty.name))
        self.assertEqual(self.drcty.name, path.root)
        self.assertTrue(path.project)

class RecordTests(NeedsTempDirectory, unittest.TestCase):

    def test_content_goes_to_named_file(self):
        fN = "node.yaml"
        fP = os.path.join(self.drcty.name, fN)
        self.assertFalse(os.path.isfile(fP))
        with record(fN, parent=self.drcty.name) as output:
            output.write(ruamel.yaml.dump("Test string"))

        self.assertTrue(os.path.isfile(fP))
        with open(fP, 'r') as check:
            self.assertEqual("Test string\n...", check.read().strip())

    def test_content_goes_to_file_object(self):
        fObj = StringIO()
        with record(fObj, parent=self.drcty.name) as output:
            output.write(ruamel.yaml.dump("Test string"))

        self.assertEqual("Test string\n...", fObj.getvalue().strip())
