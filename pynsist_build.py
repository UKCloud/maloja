#!/usr/bin/env python
# encoding: UTF-8

import os.path
import pkg_resources

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

for path in get_working_pkgs(pkg_resources.working_set):
    print(path)
