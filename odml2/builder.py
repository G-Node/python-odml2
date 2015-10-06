# coding=UTF-8

# Copyright (c) 2015, Adrian Stoewer (adrian.stoewer@rz.ifi.lmu.de)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the project.

__all__ = ("SB", )

from odml2 import value_from


class SB(object):
    """
    A section builder
    """

    def __init__(self, typ, uuid=None, label=None, reference=None, **properties):
        self.type = typ
        self.uuid = uuid
        self.label = label
        self.reference = reference
        self.properties = properties

    def build(self, back_end, parent_uuid=None, prop=None):
        # TODO What about error handling (undo already built sections)?
        # TODO Handle sections?
        if parent_uuid is None:
            uuid = back_end.root_create(self.type, self.uuid, self.label, self.reference)
        else:
            if prop is None:
                raise ValueError("A property name is needed to append the section")
            uuid = back_end.property_add_section(parent_uuid, prop, self.type, self.uuid, self.label, self.reference)
        for p, element in self.properties.items():
            if isinstance(element, list):
                for sub in element:
                    if isinstance(sub, SB):
                        sub.build(back_end, uuid, p)
                    else:
                        ValueError("Section builder expected but was %s" % type(sub))
            if isinstance(element, SB):
                element.build(back_end, uuid, p)
            else:
                value = value_from(element)
                back_end.property_add_value(uuid, p, value)
