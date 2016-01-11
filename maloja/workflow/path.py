#!/usr/bin/env python
#   -*- encoding: UTF-8 -*-

from collections import namedtuple

Path = namedtuple(
    "Path",
    ["root", "project", "org", "service", "category", "container", "node", "file"]
)
"""
This structure contains the file path components necessary to
identify resource stored as YAML data in the Maloja survey tree.

"""

"""
    patterns = {
        "org": (Org, "*/org.yaml"),
        "catalog": (Catalog, "*/*/catalog.yaml"),
        "vdc": (Vdc, "*/*/vdc.yaml"),
        "vapp": (VApp, "*/*/*/vapp.yaml"),
        "template": (Template, "*/*/*/template.yaml"),
        "vm": (Vm, "*/*/*/*/vm.yaml"),
    }
"""

# TODO: Surveyor.patterns go here
# TODO: Factories for empty Paths
# TODO: Integrate with model classes
# TODO: Needs a search API cf find_xpath

def filter_records(*args, root="", key="", value=""):
    """
    Reads files from the argument list, turns them into objects and yields
    those which match key, value criteria.

    Matching of attributes flattens the object hierarchy. Attributes at the top
    level of the object take precedence over those with the same name further
    down in its children.

    Return values are 2-tuples of object and path.

    """
    for fP in args:
        path = split_to_path(fP, root)
        name = os.path.splitext(path.file)[0]
        try:
            typ, pattern = Surveyor.patterns[name]
        except KeyError:
            continue

        with open(fP, 'r') as data:
            obj = typ(**yaml_loads(data.read()))
            if obj is None:
                continue
            if not key:
                yield (obj, path)
                continue
            else:
                data = dict([
                    (k, getattr(item, k))
                    for seq in [
                        i for i in vars(obj).values() if isinstance(i, list)
                    ]
                    for item in seq
                    for k in getattr(item, "_fields", [])],
                    **vars(obj)
                )
                match = data.get(key.strip(), "")
                if value.strip() in str(match):
                    yield (obj, path)


