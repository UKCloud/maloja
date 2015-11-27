#!/usr/bin/env python
#   -*- encoding: UTF-8 -*-

from collections import namedtuple
import functools
import logging

import ruamel.yaml

import maloja.types

Status = namedtuple("Status", ["id", "job", "level"])

yaml_loads = functools.partial(ruamel.yaml.load, Loader=ruamel.yaml.RoundTripLoader)
yaml_dumps = functools.partial(ruamel.yaml.dump, Dumper=ruamel.yaml.RoundTripDumper)
