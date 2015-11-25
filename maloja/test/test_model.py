#!/usr/bin/env python
#   -*- encoding: UTF-8 -*-

from __future__ import print_function
from __future__ import unicode_literals

import unittest

from maloja.surveyor import yaml_dumps
from maloja.surveyor import yaml_loads


class YAMLTests(unittest.TestCase):

    @unittest.skip("Pending model design.")
    def test_simple(self):
        inp = """\
        # example
        name:
          # details
          family: Smith   # very common
          given: Alice    # one of the siblings
        """

        code = yaml_loads(inp)
        code['name']['given'] = 'Bob'

        print(yaml_dumps(code), end='')
