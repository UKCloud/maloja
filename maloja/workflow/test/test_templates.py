#!/usr/bin/env python
# encoding: UTF-8

import unittest

from chameleon import PageTemplateFile
import pkg_resources

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
