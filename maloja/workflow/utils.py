#!/usr/bin/env python
#   -*- encoding: UTF-8 -*-

from collections import namedtuple
import contextlib
import tempfile
import operator
import os.path


Path = namedtuple("Path", ["root", "project", "org", "dc", "app", "node", "file"])
 
def make_path(path:Path, prefix="proj_", suffix=""):
    os.makedirs(path.root, exist_ok=True)

    if path.project is None and path.file is not None:
            project = tempfile.mkdtemp(suffix=suffix, prefix=prefix, dir=path.root)
            return path._replace(project=os.path.basename(project))
    else:
        return path

def recent_project(path:Path):
    projects = [i for i in os.listdir(path.root)
             if os.path.isdir(os.path.join(path.root, i))]
    stats = [(os.path.getmtime(os.path.join(path.root, fP)), fP)
             for fP in projects]
    stats.sort(key=operator.itemgetter(0), reverse=True)
    return Path(
        path.root, next((i[1] for i in stats), None), path.file)

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
