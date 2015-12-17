#!/usr/bin/env python
#   -*- encoding: UTF-8 -*-

import unittest

import pkg_resources

from maloja.model import Vm
from maloja.planner import read_objects
from maloja.workflow.utils import group_by_type


class PlannerTests(unittest.TestCase):

    def test_first_object_supplies_defaults(self):
        design = pkg_resources.resource_string(
                "maloja.test", "use_case01.yaml"
            )
        objs = group_by_type(read_objects(design))
        self.assertEqual(2, len(objs[Vm]))
        self.assertEqual(objs[Vm][0].href, objs[Vm][1].href)
