# coding=UTF-8

# Copyright (c) 2015, Adrian Stoewer (adrian.stoewer@rz.ifi.lmu.de)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the project.

from uuid import uuid4
import odml2

__all__ = ("SB", )


class SB(object):
    """
    A section builder
    """

    # noinspection PyShadowingBuiltins
    def __init__(self, type, uuid=None, label=None, reference=None, **properties):
        self.type = type
        self.uuid = str(uuid) if uuid is not None else str(uuid4())
        self.label = label
        self.reference = reference
        self.properties = properties

    def build(self, back_end, parent_uuid=None, prop=None):
        # TODO What about error handling (undo already built sections)?
        if parent_uuid is None:
            back_end.create_root(self.type, self.uuid, self.label, self.reference)
        else:
            if prop is None:
                raise ValueError("A property name is needed to append the section")
            back_end.sections.add(self.type, self.uuid, self.label, self.reference, parent_uuid, prop)

        for p, element in self.properties.items():
            if isinstance(element, list):
                for sub in element:
                    if isinstance(sub, SB):
                        sub.build(back_end, self.uuid, p)
                    elif isinstance(sub, odml2.Section):
                        # TODO Handle sections
                        raise NotImplementedError()
                    else:
                        ValueError("Section builder expected but was %s" % type(sub))
            elif isinstance(element, SB):
                element.build(back_end, self.uuid, p)
            elif isinstance(element, odml2.Section):
                # TODO Handle sections
                raise NotImplementedError()
            else:
                value = odml2.value_from(element)
                back_end.sections[self.uuid].value_properties.set(p, value)
