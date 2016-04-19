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

def get_working_pkgs(ws):
    for dist in ws:
        try:
            pkgs = dist.get_metadata_lines("top_level.txt")
        except FileNotFoundError:
            pkgs = None

        try:
            if pkgs is None:
                yield pkg_resources.resource_filename(dist.key, "")
            else:
                for pkg in pkgs:
                    locn = pkg_resources.resource_filename(pkg, "")
                    # namespace packages test false
                    yield locn or os.path.join(dist.location, pkg)
        except ImportError as e:
            print(e)
            if pkgs is None:
                locn = os.path.join(dist.location, dist.key)
                if os.path.isdir(locn):
                    yield locn
                else:
                    locn += ".py"
                    if os.path.isfile(locn):
                        yield locn
                    else:
                        print("******", pkg)

def parser(description=__doc__):
    return argparse.ArgumentParser(
        description,
        fromfile_prefix_chars="@"
    )

def main(args):
    for path in get_working_pkgs(pkg_resources.working_set):
        print(path)
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
