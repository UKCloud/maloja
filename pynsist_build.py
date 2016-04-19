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
import ast
import logging
from logging.handlers import WatchedFileHandler
import os
import os.path
import shutil
import sys
import warnings

import pkg_resources
import nsist

CFG_FN = "pynsist.cfg"
PKG_DIR = "pynsist_pkgs"

__doc__ = """
This build script creates a self-installing executable for Maloja on Windows.

First install Maloja from source::

    pip install .[dev,docbuild,binbuild]

Second, build the HTML docs::

    sphinx-build maloja\doc maloja\doc\html

Finally, run this script::

    python pynsist_build.py

A self-installing executable will be created in the `build\\nsis` directory.

"""

try:
    from maloja import __version__ as VERSION
except ImportError:
    VERSION = str(
        ast.literal_eval(
            open(os.path.join(
                os.path.dirname(__file__),
                "maloja", "__init__.py"),
                'r').read().split("=")[-1].strip()
        )
    )

configTemplate = """
[Application]
name=Maloja
version={version}
entry_point=maloja.main:run
console=true
#icon=myapp.ico

[Python]
version=3.5.1

[Include]
packages = requests_futures
files = LICENSE
    maloja\doc\
""".lstrip()

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
                yield (dist.key, locn)
            else:
                for pkg in pkgs:
                    locn = pkg_resources.resource_filename(pkg, "")

                    if not locn:
                        # namespace package
                        locn = os.path.join(dist.location, pkg)
                        if os.path.isdir(locn):
                            yield (pkg, locn)
                        else:
                            log.warning("couldn't find namespace package '{0}'.".format(pkg))

                    if os.path.samefile(locn, dist.location):
                        # single module
                        locn = os.path.join(dist.location, pkg + ".py")
                        if os.path.isfile(locn):
                            yield ("", locn)
                        else:
                            log.warning("couldn't find module '{0}'.".format(pkg))

                    else:
                        yield (pkg, locn)

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
    parser.add_argument(
        "--no-tidy", required=False,
        action="store_const", dest="preserve",
        const=True, default=False,
        help="Preserve configuration, working directories and build products")
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

    here = os.path.dirname(os.path.abspath(__file__))
    pkgDir = os.path.join(here, PKG_DIR)
    shutil.rmtree(pkgDir, ignore_errors=True)
    os.makedirs(pkgDir, exist_ok=False)

    for dst, src in get_working_pkgs(pkg_resources.working_set):
        log.info("Copying {0}...".format(src))
        try:
            shutil.copytree(src, os.path.join(pkgDir, dst))
        except FileExistsError:
            log.debug("{0} exists.".format(dst))
        except NotADirectoryError:
            shutil.copy(src, pkgDir)

    configFp = os.path.join(here, CFG_FN)
    with open(configFp, "w") as cfg:
        cfg.write(configTemplate.format(version=VERSION))
    log.info("Created a config for version {0}.".format(VERSION))

    log.info("Invoking pynsist...\n\n")
    nsist.main([configFp])

    if not args.preserve:
        log.info("Tidying up...")
        os.remove(configFp)
        shutil.rmtree(pkgDir, ignore_errors=True)

    log.info("Done.")
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
