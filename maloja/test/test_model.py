#!/usr/bin/env python
#   -*- encoding: UTF-8 -*-

from __future__ import print_function
from __future__ import unicode_literals

import unittest

import ruamel.yaml

class YAMLTests(unittest.TestCase):

    def test_simple(self):
        inp = """\
        # example
        name:
          # details
          family: Smith   # very common
          given: Alice    # one of the siblings
        """

        code = ruamel.yaml.load(inp, ruamel.yaml.RoundTripLoader)
        code['name']['given'] = 'Bob'

        print(ruamel.yaml.dump(code, Dumper=ruamel.yaml.RoundTripDumper), end='')
