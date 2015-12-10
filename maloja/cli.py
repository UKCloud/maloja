#!/usr/bin/env python
#   -*- encoding: UTF-8 -*-

import argparse
import logging
import os.path
import sys

__doc__ = """
CLI Interface to Maloja toolkit.
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
        "--input", required=False, default="",
        help="path to input directory")
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
        "infile", nargs="?", type=argparse.FileType("r"),
        default=sys.stdin,
        help="Send a design to the planner"
    )
    parser.add_argument(
        "--output", default=DFLT_LOCN,
        help="path to output directory [{}]".format(DFLT_LOCN))
    return parser

def parser(description=__doc__):
    return argparse.ArgumentParser(
        description,
        fromfile_prefix_chars="@"
    )

def parsers(description=__doc__):
    parser =  parser(description)
    parser = add_common_options(parser)
    parser = add_api_options(parser)
    parser = add_builder_options(parser)
    parser = add_cache_options(parser)
    subparsers = parser.add_subparsers(
        dest="command",
        help="Commands:",
    )
    return (parser, subparsers)
