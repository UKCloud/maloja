#!/usr/bin/env python
# encoding: UTF-8

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

from chameleon import PageTemplateFile
import pkg_resources

import maloja.planner

class ComposeVAppTests(unittest.TestCase):

    def setUp(self):
        self.macro = PageTemplateFile(pkg_resources.resource_filename(
            "maloja.workflow", "ComposeVAppParams.pt"))

    def test_render(self):
        data = {
            "appliance": {
                "name": "My Test VM",
                "description": "This VM is for testing",
                "vms": [
                        {
                            "name": "vm_001",
                            "href": "http://cloud.io/vms/1",
                            "networkconnections": [
                                {
                                    "href": "http://cloud.io/networks/3",
                                    "isConnected": True,
                                },
                                {
                                    "href": "http://cloud.io/networks/4",
                                    "isConnected": True,
                                },
                            ],
                            "guestcustomization": "#!/bin/sh\n",
                        },
                ],
            },
            "networks": [{
                "interface": "public ethernet",
                "name": "managed-external-network",
                "href": "http://cloud/api/networks/12345678",
            },
            {
                "interface": "data network",
                "name": "managed-data-network",
                "href": "http://cloud/api/networks/98765432",
            },
            ],
            "template": {
                "name": "Ubuntu",
                "href": "http://cloud/api/items/12345678"
            }
        }
        self.assertEqual(2457, len(self.macro(**data)))

class RecomposeVAppTests(unittest.TestCase):

    def setUp(self):
        fP = pkg_resources.resource_filename(
                "maloja.test", "issue_025-02.yaml"
            )
        with open(fP, "r") as data:
            self.design = list(maloja.planner.read_objects(data.read()))

    def test_macro(self):
        macro = PageTemplateFile(
            pkg_resources.resource_filename(
                "maloja.workflow", "RecomposeVAppParams.pt"
            )
        )
        networks = self.design[2:3]
        template = self.design[3]
        vms = self.design[4:]

        data = {
            "appliance": {
                "name": "Test VApp",
                "description": "Created by Maloja unit tests.",
                "vms": vms,
            },
            "networks": networks,
            "template": {
                "name": template.name,
                "href": template.href
            }
        }
        xml = macro(**data)
