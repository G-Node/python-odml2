# coding=UTF-8

# Copyright (c) 2015, Adrian Stoewer (adrian.stoewer@rz.ifi.lmu.de)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the project.


__all__ = ("YamlBackEnd", )

import io
import yaml

from odml2 import compat
from odml2.back_end import memory


class YamlBackEnd(memory.MemDocumentBackEnd):
    """
    Back end implementation for yaml files.
    """

    NAME = "yaml"
    FILE_EXT = ("yaml", "yml")

    def __init__(self):
        super(YamlBackEnd, self).__init__(memory.MemMetadataBackEnd(), memory.MemTerminologyBackEnd())

    def save(self, destination):
        data = self.to_dict()
        if hasattr(destination, "write"):
            yaml_str = yaml.dump(data, default_flow_style=False, allow_unicode=True)
            if compat.PY2:
                yaml_str = yaml_str.decode("utf-8")
            destination.write(yaml_str)
        else:
            with io.open(destination, "w", encoding="utf-8") as f:
                yaml.dump(data, f, default_flow_style=False, allow_unicode=True)

    def load(self, source):
        if hasattr(source, "read"):
            data = yaml.load(source)
        else:
            with io.open(source, "r", encoding="utf-8") as f:
                data = yaml.load(f)
        self.from_dict(data)
