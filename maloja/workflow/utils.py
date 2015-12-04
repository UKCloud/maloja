#!/usr/bin/env python
#   -*- encoding: UTF-8 -*-

from collections import namedtuple
import contextlib
import itertools
import tempfile
import operator
import os.path

import pkg_resources

Path = namedtuple("Path", ["root", "project", "org", "dc", "app", "node", "file"])
 
def make_path(path:Path, prefix="proj_", suffix=""):
    os.makedirs(path.root, exist_ok=True)

    if path.project is None and path.file is not None:
        project = tempfile.mkdtemp(suffix=suffix, prefix=prefix, dir=path.root)
        open(os.path.join(project, path.file), "w").close()
        return path._replace(project=os.path.basename(project))
    else:
        return path


def recent_project(path:Path):
    projects = [i for i in os.listdir(path.root)
             if os.path.isfile(os.path.join(path.root, i, "project.yaml"))]
    stats = [(os.path.getmtime(os.path.join(path.root, fP)), fP)
             for fP in projects]
    stats.sort(key=operator.itemgetter(0), reverse=True)
    return Path(
        path.root, next((i[1] for i in stats), None), None, None, None, None, path.file)


def split_to_path(data):
    lookup = {
        "org.yaml": -4,
        "vdc.yaml": -5,
        "vapp.yaml": -6,
        "template.yaml": -6,
        "vm.yaml": -7,
    }
    drive, tail = os.path.splitdrive(data)
    bits = tail.split(os.sep)
    index = lookup[bits[-1]] 
    data = list(itertools.chain(
        bits[index: -1],
        itertools.repeat(None, 7 + index),
        itertools.repeat(bits[-1], 1)
    ))
    return Path(*data)._replace(root=drive + os.path.join(*bits[:index]))
    

def plugin_interface(key="maloja.plugin"):
    for i in pkg_resources.iter_entry_points(key):
        try:
            ep = i.resolve()
        except Exception as e:
            continue
        else:
            yield (i.name, ep)


@contextlib.contextmanager
def record(nameOrStream, parent=None, suffix=".yaml"):
    if isinstance(nameOrStream, str):
        fD, fN = tempfile.mkstemp(suffix=suffix, dir=parent)
        try:
            rv = open(fN, 'w')
            yield rv
        except Exception as e:
            raise e
        rv.close()
        os.close(fD)
        os.rename(fN, os.path.join(parent, nameOrStream))
    else:
        yield nameOrStream
