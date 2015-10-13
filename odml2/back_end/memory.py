# coding=UTF-8

# Copyright (c) 2015, Adrian Stoewer (adrian.stoewer@rz.ifi.lmu.de)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the project.

__all__ = ("MemDocumentBackEnd", "MemMetadataBackEnd", "MemTerminologyBeckEnd")

import abc
import itertools
from uuid import uuid4

from odml2.back_end import base


class MemDocumentBackEnd(base.DocumentBackEnd):

    def __init__(self, metadata, terms):
        super(MemDocumentBackEnd, self).__init__(metadata, terms)
        self.__author = None
        self.__date = None
        self.__root = None

    def author_get(self):
        return self.__author

    def author_set(self, author):
        self.__author = author

    def date_get(self):
        return self.__date

    def date_set(self, date):
        self.__date = date

    @abc.abstractmethod
    def save(self, destination):
        raise NotImplementedError()

    @abc.abstractmethod
    def load(self, source):
        raise NotImplementedError()


class MemMetadataBackEnd(base.MetadataBackEnd):

    def __init__(self):
        self.__content = {}  # all sections (by uuid)
        self.__root = None   # the uuid of the root section

    def root_exists(self):
        return self.__root is not None

    def root_get(self):
        if not self.root_exists():
            raise RuntimeError("The back-end has no root!")
        return self.__root

    def root_create(self, typ, uuid=None, label=None, reference=None):
        if uuid is None:
            uuid = str(uuid4())
        sd = SecData(typ, uuid, label, reference)
        self.__content.clear()
        self.__content[uuid] = sd
        self.__root = uuid
        return uuid

    def section_exists(self, uuid):
        return uuid in self.__content

    def section_get_type(self, uuid):
        sd = self.__section_get(uuid)
        return sd.type

    def section_set_type(self, uuid, typ):
        sd = self.__section_get(uuid)
        sd.type = typ

    def section_get_label(self, uuid):
        sd = self.__section_get(uuid)
        return sd.label

    def section_set_label(self, uuid, label):
        sd = self.__section_get(uuid)
        sd.label = label

    def section_get_reference(self, uuid):
        sd = self.__section_get(uuid)
        return sd.reference

    def section_set_reference(self, uuid, reference):
        sd = self.__section_get(uuid)
        sd.reference = reference

    def section_remove(self, uuid):
        sd = self.__section_get(uuid)
        sd_parent, prop = self.__section_get_parent(uuid)
        if sd_parent is not None:
            sd_parent.section_props[prop].remove(uuid)
        self.__section_remove_with_children(sd)
        if len(self.__content) == 0:
            self.__root = None

    def section_get_properties(self, uuid):
        sd = self.__section_get(uuid)
        return sorted(itertools.chain(sd.section_props, sd.value_props))

    def property_has_sections(self, uuid, prop):
        sd = self.__section_get(uuid)
        return prop in sd.section_props

    def property_get_sections(self, parent_uuid, prop):
        sd = self.__section_get(parent_uuid)
        if prop not in sd.section_props:
            raise RuntimeError("Unable to get sections for property '%s' on section with uuid '%s'" %
                               (prop, parent_uuid))
        return sd.section_props[prop]

    def property_add_section(self, parent_uuid, prop, typ, uuid=None, label=None, reference=None):
        # TODO check for forbidden/reserved property names
        sd = self.__section_get(parent_uuid)
        if prop in sd.value_props:
            del sd.value_props[prop]
        if uuid is None:
            uuid = str(uuid4())
        if prop in sd.section_props:
            sd.section_props[prop].append(uuid)
        else:
            sd.section_props[prop] = [uuid]
        self.__content[uuid] = SecData(typ, uuid, label, reference)
        return uuid

    def property_has_value(self, parent_uuid, prop):
        sd = self.__section_get(parent_uuid)
        return prop in sd.value_props

    def property_get_value(self, parent_uuid, prop):
        sd = self.__section_get(parent_uuid)
        if prop not in sd.value_props:
            raise RuntimeError("Unable to get value for property '%s' on section with uuid '%s'" %
                               (prop, parent_uuid))
        return sd.value_props[prop]

    def property_set_value(self, parent_uuid, prop, value):
        # TODO check for forbidden/reserved property names
        sd = self.__section_get(parent_uuid)
        if prop in sd.section_props:
            for child_uuid in sd.section_props[prop]:
                sd_child = self.__content.get(child_uuid)
                if sd_child is not None:
                    self.__section_remove_with_children(sd_child)
            del sd.section_props[prop]
        sd.value_props[prop] = value

    def property_remove_value(self, parent_uuid, prop):
        sd = self.__section_get(parent_uuid)
        if prop not in sd.value_props:
            raise RuntimeError("Unable to remove value for property '%s' on section with uuid '%s'" %
                               (prop, parent_uuid))
        del sd.value_props[prop]

    def property_remove(self, parent_uuid, prop):
        sd = self.__section_get(parent_uuid)
        if prop in sd.section_props:
            for child_uuid in sd.section_props[prop]:
                sd_child = self.__content.get(child_uuid)
                if sd_child is not None:
                    self.__section_remove_with_children(sd_child)
            del sd.section_props[prop]
        elif prop in sd.value_props:
            del sd.value_props[prop]
        else:
            raise RuntimeError("Unable to remove property '%s' on section with uuid '%s'" %
                               (prop, parent_uuid))

    #
    # internal methods
    #

    def __section_get(self, uuid):
        if not self.section_exists(uuid):
            raise RuntimeError("The back-end contains no section with the uuid %s" % uuid)
        return self.__content[uuid]

    def __section_get_parent(self, uuid):
        for parent_uuid, sd_parent in self.__content.items():
            for (prop, child_uuids) in sd_parent.section_props.items():
                if uuid in child_uuids:
                    return sd_parent, prop
        return None, None

    def __section_remove_with_children(self, sec_data):
        del self.__content[sec_data.uuid]
        for children_uuids in sec_data.section_props.values():
            for child_uuid in children_uuids:
                sd_child = self.__content.get(child_uuid)
                if sd_child is not None:
                    self.__section_remove_with_children(sd_child)


class MemTerminologyBackEnd(base.TerminologyBeckEnd):

    def __init__(self):
        self.__namespaces = {"default": NameSpaceData("default")}

    def namespace_get_all(self):
        return list(self.__namespaces.keys())

    def namespace_create(self, prefix, location=None):
        if prefix in self.__namespaces:
            raise RuntimeError("The back-end contains already a namespace with the prefix '%s'" % prefix)
        if location is not None:
            # TODO support loading of name-space from other locations
            raise NotImplementedError()
        self.__namespaces[prefix] = NameSpaceData(prefix)

    def namespace_remove(self, prefix):
        ns = self.__namespace_get(prefix)
        del self.__namespaces[ns.prefix]

    def namespace_get_location(self, prefix):
        ns = self.__namespace_get(prefix)
        return ns.location

    def namespace_get_types(self, prefix):
        ns = self.__namespace_get(prefix)
        return list(ns.types.keys())

    def type_create(self, typ, definition=None, properties=None):
        prefix, typ = split_type(typ)
        ns = self.__namespace_get(prefix)
        if typ in ns.types:
            raise RuntimeError("The type already exists: %s:%s" % (prefix, typ))
        ns[typ] = TypeData(typ, definition, properties)

    def type_exists(self, typ):
        prefix, typ = split_type(typ)
        return prefix in self.__namespaces and typ in self.__namespaces[prefix].types

    def type_remove(self, typ):
        prefix, typ = split_type(typ)
        ns = self.__namespace_get(prefix)
        if typ not in ns.types:
            raise RuntimeError("The type does not exist: %s:%s" % (prefix, typ))
        del ns[typ]

    def type_get_definition(self, typ):
        type_data = self.__type_get(typ)
        return type_data.definition

    def type_set_definition(self, typ, definition):
        type_data = self.__type_get(typ)
        type_data.definition = definition

    def type_add_property(self, typ, prop):
        raise NotImplementedError()

    def type_remove_property(self, typ, prop):
        raise NotImplementedError()

    def __namespace_get(self, prefix):
        if prefix is None:
            prefix = "default"
        if prefix not in self.__namespaces:
            raise RuntimeError("The back-end contains no namespace with the prefix '%s'" % prefix)
        return self.__namespaces[prefix]

    def __type_get(self, typ):
        prefix, typ = split_type(typ)
        ns = self.__namespace_get(prefix)
        if typ in ns.types:
            raise RuntimeError("The type already exists: %s:%s" % (prefix, typ))
        return ns[typ]

class SecData(object):
    """
    Simple section data object used by the back-and
    """

    def __init__(self, typ, uuid, label=None, reference=None, value_props=None, section_props=None):
        self.type = typ
        self.uuid = uuid
        self.label = label
        self.reference = reference
        self.value_props = value_props if value_props is not None else {}
        self.section_props = section_props if section_props is not None else {}


class NameSpaceData(object):
    """
    Simple container for namespace date managed by the back-end
    """

    def __init__(self, prefix, location=None, types=None):
        self.__prefix = prefix
        self.__location = location
        self.types = types if types is not None else {}

    @property
    def prefix(self):
        return self.__prefix

    @property
    def location(self):
        return self.__location


class TypeData(object):
    """
    Simple container for type definition data managed by the back-end
    """

    # noinspection PyShadowingBuiltins
    def __init__(self, type, definition, properties):
        self.__type = type
        self.definition = definition
        self.properties = properties

    @property
    def type(self):
        return self.__type


def split_type(typ):
    count = typ.count(":")
    if count == 0:
        return "default", typ
    elif count == 1:
        return typ.split(":")
    else:
        raise RuntimeError("Not a valid type: %s" % type)
