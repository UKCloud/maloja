#!/usr/bin/env python
#   -*- encoding: UTF-8 -*-

import os
import os.path
from io import StringIO
import tempfile
import unittest

from maloja.model import Catalog
from maloja.model import Gateway
from maloja.model import Network
from maloja.model import Template
from maloja.model import Org
from maloja.model import Project
from maloja.model import VApp
from maloja.model import Vdc
from maloja.model import Vm
from maloja.model import yaml_loads

from maloja.workflow.path import Path
from maloja.workflow.path import cache
from maloja.workflow.path import find_ypath
from maloja.workflow.path import split_to_path
from maloja.workflow.test.test_utils import NeedsTempDirectory


class PathTests(NeedsTempDirectory, unittest.TestCase):

    @property
    def fixture(self):
        root = self.drcty.name
        return [
            (Project(), Path(
                root, "testproj", None, None, None, None, None, "project.yaml")),
            (Org(name="0-123-4-567890"), Path(
                root, "testproj", "0-123-4-567890", None, None, None, None, "org.yaml")),
            (Catalog(name="Skyscape"),
             Path(root, "testproj", "0-123-4-567890", "catalogs",
                  "Skyscape", None, None, "catalog.yaml")),
            (Template(name="CentOS_FTP"),
             Path(root, "testproj", "0-123-4-567890", "catalogs",
                 "Skyscape", "CentOS_FTP", None, "template.yaml")),
            (Vm(name="server"),
             Path(root, "testproj", "0-123-4-567890", "catalogs",
                 "Skyscape", "CentOS_FTP", "server", "vm.yaml")),
            (Template(name="RedHat_MySQL"),
             Path(root, "testproj", "0-123-4-567890", "catalogs",
                 "Skyscape", "RedHat_MySQL", None, "template.yaml")),
            (Vm(name="master"),
             Path(root, "testproj", "0-123-4-567890", "catalogs",
                 "Skyscape", "RedHat_MySQL", "master", "vm.yaml")),
            (Vm(name="slave"),
             Path(root, "testproj", "0-123-4-567890", "catalogs",
                 "Skyscape", "RedHat_MySQL", "slave", "vm.yaml")),
            (Gateway(name="0-123-4-567890-edge"),
             Path(root, "testproj", "0-123-4-567890", "PROD",
                 None, None, None, "edge.yaml")),
            (Vdc(name="PROD"),
             Path(root, "testproj", "0-123-4-567890", "PROD",
                 None, None, None, "vdc.yaml")),
            (Network(name="USER_NET"),
             Path(root, "testproj", "0-123-4-567890", "PROD",
                 "networks", "USER_NET", None, "net.yaml")),
            (VApp(name="CentOS_FTP"),
             Path(root, "testproj", "0-123-4-567890", "PROD",
                 "Skyscape", "CentOS_FTP", None, "vapp.yaml")),
            (Vm(name="server"),
             Path(root, "testproj", "0-123-4-567890", "PROD",
                 "Skyscape", "CentOS_FTP", "server", "vm.yaml")),
        ]

    def test_cache_path(self):
        for obj, path in self.fixture:
            with self.subTest(path=path):
                rv = cache(path, obj)
                self.assertEqual(path, split_to_path(rv, root=self.drcty.name))
                self.assertTrue(os.path.isfile(rv))

    def test_object_cache(self):
        self.maxDiff = 1200
        for obj, path in self.fixture:
            with self.subTest(path=path):
                fP = cache(path, obj)
                with open(fP, 'r') as data:
                    text = data.read()
                    rv = type(obj)(**yaml_loads(text))
                    self.assertEqual(vars(obj), vars(rv))

    def test_ypath_by_type(self):
        proj = self.fixture[0][1]
        for obj, path in self.fixture:
            cache(path, obj)

        results = list(find_ypath(proj, Vm()))
        self.assertEqual(4, len(results))
        self.assertTrue(all(len(i) == 2 for i in results), results)
        self.assertTrue(all(isinstance(i[0], Path) for i in results), results)
        self.assertTrue(all(isinstance(i[1], Vm) for i in results), results)
        self.assertIn(self.fixture[-1][1], [i[0] for i in results], results)

    def test_ypath_with_attributes(self):
        proj = self.fixture[0][1]
        for obj, path in self.fixture:
            cache(path, obj)

        results = list(find_ypath(proj, Vm(name="server")))
        self.assertEqual(2, len(results))
        self.assertTrue(all(len(i) == 2 for i in results), results)
        self.assertTrue(all(isinstance(i[0], Path) for i in results), results)
        self.assertTrue(all(isinstance(i[1], Vm) for i in results), results)
        self.assertIn(self.fixture[-1][1], [i[0] for i in results], results)

    def test_ypath_with_keywords(self):
        proj = self.fixture[0][1]
        for obj, path in self.fixture:
            cache(path, obj)

        results = list(find_ypath(proj, Vm(), name="server"))
        self.assertEqual(2, len(results))
        self.assertTrue(all(len(i) == 2 for i in results), results)
        self.assertTrue(all(isinstance(i[0], Path) for i in results), results)
        self.assertTrue(all(isinstance(i[1], Vm) for i in results), results)
        self.assertIn(self.fixture[-1][1], [i[0] for i in results], results)

@unittest.skip("Heavy development")
class ProjectTests(NeedsTempDirectory, unittest.TestCase):

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

@unittest.skip("Heavy development")
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

@unittest.skip("Heavy development")
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
