#!/usr/bin/env python
#   -*- encoding: UTF-8 -*-

from collections import namedtuple

Path = namedtuple(
    "Path",
    ["root", "project", "org", "dc", "app", "node", "file"]
)
"""
This structure contains the file path components necessary to
identify resource stored as YAML data in the Maloja survey tree.

"""

# TODO: Surveyor.patterns go here
# TODO: Factories for empty Paths
# TODO: Integrate with model classes
# TODO: Needs a search API cf find_xpath
