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

import argparse
import logging
from logging.handlers import WatchedFileHandler
import os
import os.path
import sys
import warnings

import pkg_resources
import nsist

print(nsist.main)

__doc__ = """
This build script creates a self-installing executable for Maloja on Windows.

"""

def get_working_pkgs(ws):
    log = logging.getLogger("packaging.get_working_pkgs")
    for dist in ws:
        if dist.project_name == "maloja":
            continue

        try:
            pkgs = dist.get_metadata_lines("top_level.txt")
        except FileNotFoundError:
            pkgs = None

        try:
            if pkgs is None:
                locn = pkg_resources.resource_filename(dist.key, "")
                yield locn
            else:
                for pkg in pkgs:
                    locn = pkg_resources.resource_filename(pkg, "")

                    if not locn:
                        # namespace package
                        locn = os.path.join(dist.location, pkg)
                        if os.path.isdir(locn):
                            yield locn
                        else:
                            log.warning("couldn't find namespace package '{0}'.".format(pkg))

                    if os.path.samefile(locn, dist.location):
                        # single module
                        locn = os.path.join(dist.location, pkg + ".py")
                        if os.path.isfile(locn):
                            yield locn
                        else:
                            log.warning("couldn't find module '{0}'.".format(pkg))

                    else:
                        yield locn

        except ImportError as e:
            log.warning("couldn't find '{0}'.".format(dist))

def parser(description=__doc__):
    parser = argparse.ArgumentParser(description)
    parser.add_argument(
        "-v", "--verbose", required=False,
        action="store_const", dest="log_level",
        const=logging.DEBUG, default=logging.INFO,
        help="Increase the verbosity of output")
    parser.add_argument(
        "--log", default=None, dest="log_path",
        help="Set a file path for log output")
    return parser

def main(args):

    log = logging.getLogger("packaging")
    log.setLevel(args.log_level)

    formatter = logging.Formatter(
        "%(asctime)s %(levelname)-7s %(name)s|%(message)s")
    ch = logging.StreamHandler()

    if args.log_path is None:
        ch.setLevel(args.log_level)
    else:
        fh = WatchedFileHandler(args.log_path)
        fh.setLevel(args.log_level)
        fh.setFormatter(formatter)
        log.addHandler(fh)
        ch.setLevel(logging.WARNING)

    ch.setFormatter(formatter)
    log.addHandler(ch)

    for path in get_working_pkgs(pkg_resources.working_set):
        log.info(path)
    return 0

def run():
    p = parser()
    args = p.parse_args()
    rv = main(args)

    if rv == 2:
        sys.stderr.write("\n Incorrect options.\n\n")
        p.print_help()

    sys.exit(rv)

if __name__ == "__main__":
    run()
