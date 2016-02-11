# coding=UTF-8

# Copyright (c) 2015, Adrian Stoewer (adrian.stoewer@rz.ifi.lmu.de)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the project.

"""
Provides a back-and implementation for yaml using the memory back-end base classes.
"""

import six
import yaml
from collections import OrderedDict

from odml2.api import mem


class YamlDocument(mem.MemDocument):

    NAME = "yaml"
    FEXT = (".yml", ".yaml")
    MIME = ("text/yaml", "text/x-yaml", "application/yaml", "application/x-yaml")

    def __init__(self, is_writable=True):
        super(YamlDocument, self).__init__(is_writable)

    def load(self, io, uri=None):
        writable = self.is_writable()
        try:
            data = yaml.load(io)
            self._set_writable(True)
            self.from_dict(data)
            self.set_uri(uri)
        finally:
            self._set_writable(writable)

    def save(self, io, uri=None):
        writable = self.is_writable()
        try:
            self._set_writable(True)
            data = self.to_dict()
            yaml_str = yaml.dump(data, default_flow_style=False, allow_unicode=True)
            if six.PY2:
                yaml_str = yaml_str.decode("utf-8")
            io.write(yaml_str)
            self.set_uri(uri)
        finally:
            self._set_writable(writable)


def __ordered_dict_representer(dumper, od):
    nodes = [(dumper.represent_data(k), dumper.represent_data(v)) for k, v in od.items()]
    return yaml.nodes.MappingNode(u'tag:yaml.org,2002:map', nodes)


def __frozenset_representer(dumper, fs):
    nodes = [dumper.represent_data(v) for v in fs]
    return yaml.nodes.SequenceNode(u'tag:yaml.org,2002:seq', nodes)

yaml.add_representer(OrderedDict, __ordered_dict_representer)
yaml.add_representer(frozenset, __frozenset_representer)
