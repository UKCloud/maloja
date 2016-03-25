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

import os
import os.path
from io import StringIO
import tempfile
import time
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
from maloja.workflow.path import find_project
from maloja.workflow.path import find_ypath
from maloja.workflow.path import make_project
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
                 "vapps", "CentOS_FTP", None, "vapp.yaml")),
            (Vm(name="server"),
             Path(root, "testproj", "0-123-4-567890", "PROD",
                 "vapps", "CentOS_FTP", "server", "vm.yaml")),
        ]

    def test_cache_path(self):
        self.maxDiff = 1200
        for obj, path in self.fixture:
            with self.subTest(path=path):
                rv = cache(path, obj)
                check = split_to_path(rv, root=self.drcty.name)
                self.assertEqual(path, check, check)
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

        results = list(find_ypath(proj, Gateway(name="0-123-4-567890-edge")))
        self.assertTrue(results)

        results = list(find_ypath(proj, Network(name="USER_NET")))
        self.assertTrue(results)

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

class ProjectTests(NeedsTempDirectory, unittest.TestCase):

    def test_nodirectory_find_project(self):
        drcty = tempfile.TemporaryDirectory()
        drcty.cleanup()
        self.assertFalse(os.path.isdir(drcty.name))
        self.assertRaises(StopIteration, find_project, drcty.name)

    def test_nodirectory_make_project(self):
        drcty = tempfile.TemporaryDirectory()
        drcty.cleanup()
        self.assertFalse(os.path.isdir(drcty.name))
        path, proj = make_project(drcty.name)
        self.assertTrue(os.path.isdir(drcty.name))
        self.assertEqual(drcty.name, path.root)

    def test_nodirectory_project_found(self):
        drcty = tempfile.TemporaryDirectory()
        drcty.cleanup()
        self.assertFalse(os.path.isdir(drcty.name))
        locn, proj = make_project(drcty.name)
        path, rv = find_project(drcty.name)
        self.assertEqual(locn.root, path.root)
        self.assertEqual(locn.project, path.project)

    def test_project_has_version(self):
        path, proj = make_project(self.drcty.name)
        self.assertTrue(hasattr(proj, "version"))

    def test_find_most_recently_modified_project(self):
        assets = [make_project(self.drcty.name)]
        time.sleep(1)
        assets.append(make_project(self.drcty.name))

        path, proj = find_project(self.drcty.name)
        self.assertEqual(assets[1][0], path)

        # Modify first project
        time.sleep(1)
        fP = os.path.join(*(i for i in assets[0][0] if i is not None))
        with open(fP, "r") as data:
            text = data.read()
            with open(fP, "w") as output:
                output.write(text)
                output.flush()

        path, proj = find_project(self.drcty.name)
        self.assertEqual(assets[0][0], path)

class SplitToPathTests(NeedsTempDirectory, unittest.TestCase):

    def test_org(self):
        expect = Path(
            self.drcty.name,
            "project", "org", None, None, None, None,
            "org.yaml"
        )
        data = os.path.join(*(i for i in expect if not i is None))
        rv = split_to_path(data, expect.root)
        self.assertEqual(expect[1:], rv[1:])
        self.assertTrue(os.path.samefile(expect[0], rv[0]))

    def test_vdc(self):
        expect = Path(
            self.drcty.name,
            "project", "org", "vdc", None, None, None,
            "vdc.yaml"
        )
        data = os.path.join(*(i for i in expect if not i is None))
        rv = split_to_path(data, expect.root)
        self.assertEqual(expect[1:], rv[1:])
        self.assertTrue(os.path.samefile(expect[0], rv[0]))

    def test_template(self):
        expect = Path(
            self.drcty.name,
            "project", "org", "catalogs", "catalog", "template", None,
            "template.yaml"
        )
        data = os.path.join(*(i for i in expect if not i is None))
        rv = split_to_path(data, expect.root)
        self.assertEqual(expect[1:], rv[1:])
        self.assertTrue(os.path.samefile(expect[0], rv[0]))

    def test_vapp(self):
        expect = Path(
            self.drcty.name,
            "project", "org", "vdc", "vapps", "vapp", None,
            "vapp.yaml"
        )
        data = os.path.join(*(i for i in expect if not i is None))
        rv = split_to_path(data, expect.root)
        self.assertEqual(expect[1:], rv[1:])
        self.assertTrue(os.path.samefile(expect[0], rv[0]))

    def test_vm(self):
        expect = Path(
            self.drcty.name,
            "project", "org", "catalogs", "catalog", "template", "vm",
            "vm.yaml"
        )
        data = os.path.join(*(i for i in expect if not i is None))
        rv = split_to_path(data, expect.root)
        self.assertEqual(expect[1:], rv[1:])
        self.assertTrue(os.path.samefile(expect[0], rv[0]))
