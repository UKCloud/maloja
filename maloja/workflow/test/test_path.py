#!/usr/bin/env python
#   -*- encoding: UTF-8 -*-

import os.path
from io import StringIO
import tempfile
import unittest

from maloja.workflow.test.test_utils import NeedsTempDirectory

from maloja.workflow.path import Path

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

class SplitToPathTests(NeedsTempDirectory, unittest.TestCase):

    def test_org(self):
        expect = Path(
            self.drcty.name,
            "project", "org", None, None, None,
            "org.yaml"
        )
        data = os.path.join(*(i for i in expect if not i is None))
        rv = split_to_path(data, expect.root)
        self.assertEqual(expect[1:], rv[1:])
        self.assertTrue(os.path.samefile(expect[0], rv[0]))

    def test_vdc(self):
        expect = Path(
            self.drcty.name,
            "project", "org", "vdc", None, None,
            "vdc.yaml"
        )
        data = os.path.join(*(i for i in expect if not i is None))
        rv = split_to_path(data, expect.root)
        self.assertEqual(expect[1:], rv[1:])
        self.assertTrue(os.path.samefile(expect[0], rv[0]))

    def test_template(self):
        expect = Path(
            self.drcty.name,
            "project", "org", "vdc", "template", None,
            "template.yaml"
        )
        data = os.path.join(*(i for i in expect if not i is None))
        rv = split_to_path(data, expect.root)
        self.assertEqual(expect[1:], rv[1:])
        self.assertTrue(os.path.samefile(expect[0], rv[0]))

    def test_vapp(self):
        expect = Path(
            self.drcty.name,
            "project", "org", "vdc", "vapp", None,
            "vapp.yaml"
        )
        data = os.path.join(*(i for i in expect if not i is None))
        rv = split_to_path(data, expect.root)
        self.assertEqual(expect[1:], rv[1:])
        self.assertTrue(os.path.samefile(expect[0], rv[0]))

    def test_vm(self):
        expect = Path(
            self.drcty.name,
            "project", "org", "vdc", "template", "vm",
            "vm.yaml"
        )
        data = os.path.join(*(i for i in expect if not i is None))
        rv = split_to_path(data, expect.root)
        self.assertEqual(expect[1:], rv[1:])
        self.assertTrue(os.path.samefile(expect[0], rv[0]))

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
