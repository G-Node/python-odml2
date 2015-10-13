# coding=UTF-8

# Copyright (c) 2015, Adrian Stoewer (adrian.stoewer@rz.ifi.lmu.de)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the project.

__all__ = ("SB", )

import odml2


class SB(object):
    """
    A section builder
    """

    # noinspection PyShadowingBuiltins
    def __init__(self, type, uuid=None, label=None, reference=None, **properties):
        self.type = type
        self.uuid = uuid
        self.label = label
        self.reference = reference
        self.properties = properties

    def build(self, back_end, parent_uuid=None, prop=None):
        # TODO What about error handling (undo already built sections)?
        if parent_uuid is None:
            uuid = back_end.metadata.root_create(self.type, self.uuid, self.label, self.reference)
        else:
            if prop is None:
                raise ValueError("A property name is needed to append the section")
            uuid = back_end.metadata.property_add_section(parent_uuid, prop, self.type, self.uuid, self.label, self.reference)
        for p, element in self.properties.items():
            if isinstance(element, list):
                for sub in element:
                    if isinstance(sub, SB):
                        sub.build(back_end, uuid, p)
                    elif isinstance(sub, odml2.Section):
                        # TODO Handle sections
                        raise NotImplementedError()
                    else:
                        ValueError("Section builder expected but was %s" % type(sub))
            elif isinstance(element, SB):
                element.build(back_end, uuid, p)
            elif isinstance(element, odml2.Section):
                # TODO Handle sections
                raise NotImplementedError()
            else:
                value = odml2.value_from(element)
                back_end.metadata.property_set_value(uuid, p, value)
