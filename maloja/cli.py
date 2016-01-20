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

import argparse
import logging
import os.path
import sys

__doc__ = """
CLI Interface to the Maloja toolkit.

Operation via CLI requires a set of common options.
Each subcommand may have extra options, like this::

    maloja <common options> SUBCOMMAND <subcommand options>

"""

DFLT_LOCN = os.path.expanduser(os.path.join("~", ".maloja"))

def add_api_options(parser):
    parser.add_argument(
        "--url", required=True,
        help="URL to API endpoint")
    parser.add_argument(
        "--user", required=True,
        help="Registered user for API access")
    return parser

def add_builder_options(parser):
    parser.add_argument(
        "--input", required=True,
        help="path to design file")
    return parser

def add_cache_options(parser):
    parser.add_argument(
        "--output", default=DFLT_LOCN,
        help="path to output directory [{}]".format(DFLT_LOCN))
    return parser

def add_common_options(parser):
    parser.add_argument(
        "--version", action="store_true", default=False,
        help="Print the current version number")
    parser.add_argument(
        "-v", "--verbose", required=False,
        action="store_const", dest="log_level",
        const=logging.DEBUG, default=logging.INFO,
        help="Increase the verbosity of output")
    parser.add_argument(
        "--log", default=None, dest="log_path",
        help="Set a file path for log output")
    return parser

def add_planner_options(parser):
    parser.add_argument(
        "design", nargs="?", type=argparse.FileType("r"),
        default=sys.stdin,
        help="Send a design to the planner"
    )
    return parser

def parser(description=__doc__):
    return argparse.ArgumentParser(
        description,
        fromfile_prefix_chars="@"
    )

def parsers(description=__doc__):
    rv = parser(description)
    rv = add_common_options(rv)
    rv = add_api_options(rv)
    rv = add_cache_options(rv)
    subparsers = rv.add_subparsers(
        dest="command",
        help="Commands:",
    )
    p = subparsers.add_parser(
        "survey",
        help="Maloja 'survey' command.",
        description="Invokes the surveyor module to map your virtual infrastructure."
    )

    p = subparsers.add_parser(
        "plan",
        help="Maloja 'plan' command.",
        description="Invokes the planner module to check a design file."
    )
    p = add_builder_options(p)

    p = subparsers.add_parser(
        "build",
        help="Maloja 'build' command.",
        description="Invokes the builder module to create virtual infrastructure."
    )
    p = add_builder_options(p)
    return (rv, subparsers)

def cli():
    return parsers()[0]
