# coding=UTF-8

# Copyright (c) 2015, Adrian Stoewer (adrian.stoewer@rz.ifi.lmu.de)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the project.

from uuid import uuid4

from odml2.checks import *

__all__ = ("SB", )


class SB(object):
    """
    A section builder
    """

    # noinspection PyShadowingBuiltins
    def __init__(self, type, uuid=None, label=None, reference=None, **properties):
        uuid = str(uuid) if uuid is not None else str(uuid4())
        assert_uuid(uuid)
        for p in properties:
            assert_name(p)
        self.type = type
        self.uuid = uuid
        self.label = label
        self.reference = reference
        self.properties = properties

    def build(self, document, parent_uuid=None, parent_prop=None):
        if parent_uuid is None:
            section = document.create_root(self.type, self.uuid, self.label, self.reference)
        else:
            if parent_prop is None:
                raise ValueError("A property name is needed in order to append a sub section")
            parent = document.find_section(parent_uuid)
            section = parent.create_subsection(parent_prop, self.type, self.uuid, self.label, self.reference)

        for p, thing in self.properties.items():
            section[p] = thing
