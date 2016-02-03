# coding=UTF-8

# Copyright (c) 2015, Adrian Stoewer (adrian.stoewer@rz.ifi.lmu.de)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the project.

import abc
from uuid import UUID
import odml2
from odml2.api import base


"""
Provides abstract base classes for back-end implementations.
"""

# NOTICE: Classes have a getter/setter pattern for attributes instead of
#         properties in order to distinguish more precisely between read-only
#         and read-write attributes.

# TODO add section links
# TODO raise errors when trying to change a read only document
# TODO sanitize and check input (dates, name identifiers, type identifiers, prefixes, URIs)


class MemDocument(base.BaseDocument):

    def __init__(self, is_writable=True):
        self.__is_writable = is_writable
        self.__uri = None
        self.__date = None
        self.__author = None
        self.__version = 1
        self.__root = None
        self.__namespaces = MemNameSpaceDict(self)
        self.__property_defs = MemPropertyDefDict(self)
        self.__type_defs = MemTypeDefDict(self)
        self.__sections = MemSectionDict(self)

    def is_attached(self):
        return False

    def is_writable(self):
        return self.__is_writable

    def get_uri(self,):
        return self.__uri

    def set_uri(self, uri):
        self.__uri = uri

    def get_date(self):
        return self.__date

    def set_date(self, date):
        self.__date = date

    def get_author(self):
        return self.__author

    def set_author(self, author):
        self.__author = author

    def get_version(self):
        return self.__version

    def set_version(self, version):
        self.__version = version

    # noinspection PyShadowingBuiltins
    def create_root(self, type, uuid, label, reference):
        self.sections.add(type, uuid, label, reference, None, None)

    def get_root(self):
        return self.__root

    def set_root(self, uuid):
        self.__root = uuid

    @property
    def namespaces(self):
        return self.__namespaces

    @property
    def property_defs(self):
        return self.__property_defs

    @property
    def type_defs(self):
        return self.__type_defs

    @property
    def sections(self):
        return self.__sections

    def clear(self):
        self.__uri = None
        self.__date = None
        self.__author = None
        self.__version = None
        self.__root = None
        self.__namespaces.clear()
        self.__property_defs.clear()
        self.__type_defs.clear()
        self.__sections.clear()

    @abc.abstractmethod
    def load(self, path):
        pass

    @abc.abstractmethod
    def close(self):
        pass

    @abc.abstractmethod
    def save(self, path):
        pass


class MemNameSpaceDict(base.BaseNameSpaceDict):

    def __init__(self, doc):
        self.__doc = doc
        self.__namespaces = {}

    def add(self, prefix, uri):
        self.__namespaces[prefix] = MemNameSpace(prefix, uri)

    def remove(self, key):
        del self.__namespaces[key]

    def clear(self):
        self.__namespaces.clear()

    def get(self, key):
        return self.__namespaces.get(key)

    def keys(self):
        for key in self.__namespaces:
            yield key


class MemPropertyDefDict(base.BasePropertyDefDict):

    def __init__(self, doc):
        self.__doc = doc
        self.__property_defs = {}

    def add(self, name, definition=None, types=tuple()):
        self.__property_defs[name] = MemPropertyDefinition(name, definition, types)

    def remove(self, key):
        del self.__property_defs[key]

    def clear(self):
        self.__property_defs.clear()

    def get(self, key):
        return self.__property_defs.get(key)

    def keys(self):
        for key in self.__property_defs:
            yield key


class MemTypeDefDict(base.BaseTypeDefDict):

    def __init__(self, doc):
        self.__doc = doc
        self.__type_defs = {}

    # noinspection PyShadowingBuiltins
    def add(self, type, definition=None, properties=tuple()):
        self.__type_defs[type] = MemTypeDefinition(type, definition, properties)

    def remove(self, key):
        del self.__type_defs[key]

    def clear(self):
        self.__type_defs.clear()

    def get(self, key):
        return self.__type_defs.get(key)

    def keys(self):
        for key in self.__type_defs:
            yield key


class MemSectionDict(base.BaseSectionDict):

    def __init__(self, doc):
        self.__doc = doc
        self.__sections = {}

    # noinspection PyShadowingBuiltins
    def add(self, type, uuid, label, reference, parent_uuid, parent_prop):
        if isinstance(uuid, UUID):
            uuid = str(uuid)
        if parent_uuid is None and parent_prop is None:
            # add a new root section
            self.clear()
            self.__sections[uuid] = MemSection(self.__doc, type, uuid, label, reference, is_linked=False)
            self.__doc.set_root(uuid)
        elif parent_uuid is not None and parent_prop is not None:
            # add a new sub section
            # TODO handle parents with namespace
            if uuid in self:
                raise ValueError("A section with the given uuid '%s' does already exist" % uuid)

            parent = self.get(parent_uuid)
            if parent is None:
                raise ValueError("Parent section with uuid '%s' does not exist" % parent_uuid)

            refs = (base.SectionRef(uuid, None, False), )
            if parent_prop in parent.section_properties:
                refs = parent.section_properties[parent_prop] + refs
            parent.section_properties.set(parent_prop, refs)
            self.__sections[uuid] = MemSection(self.__doc, type, uuid, label, reference, is_linked=False)
        else:
            raise RuntimeError("Parent uuid and prop must be either both None or both not None!")

    def remove(self, key):
        if key not in self:
            raise KeyError("A section with the given uuid '%s' does not exist" % key)

        def remove_with_subsections(key):
            sec = self[key]
            for refs in sec.section_properties.values():
                for ref in refs:
                    if not ref.is_link:
                        remove_with_subsections(ref.uuid)
            del self.__sections[key]

        remove_with_subsections(key)

        if len(self.__sections) == 0:
            self.__doc.set_root(None)

    def clear(self):
        self.__sections.clear()

    def get(self, key):
        return self.__sections.get(key)

    def keys(self):
        for key in self.__sections:
            yield key


# noinspection PyShadowingBuiltins
class MemSection(base.BaseSection):

    def __init__(self, doc, type, uuid, label, reference, is_linked):
        self.__doc = doc
        self.__type = type
        self.__uuid = uuid
        self.__label = label
        self.__reference = reference
        self.__is_linked = is_linked
        self.__sections_properties = MemSectionPropertyDict(doc)
        self.__value_properties = MemValuePropertyDict(doc)

    def is_linked(self):
        return self.__is_linked

    def get_uuid(self):
        return self.__uuid

    def get_type(self):
        return self.__type

    def set_type(self, type, check=False):
        self.__type = type

    def get_label(self):
        return self.__label

    def set_label(self, label):
        self.__label = label

    def get_reference(self):
        return self.__reference

    def set_reference(self, reference):
        self.__reference = reference

    @property
    def section_properties(self):
        return self.__sections_properties

    @property
    def value_properties(self):
        return self.__value_properties


class MemSectionPropertyDict(base.BaseSectionPropertyDict):

    def __init__(self, doc):
        self.__doc = doc
        self.__section_props = {}

    def set(self, prop, refs):
        self.__section_props[prop] = refs

    def remove(self, key):
        del self.__section_props[key]

    def clear(self):
        self.__section_props.clear()

    def get(self, key):
        return self.__section_props.get(key)

    def keys(self):
        for key in self.__section_props:
            yield key


class MemValuePropertyDict(base.BaseValuePropertyDict):

    def __init__(self, doc):
        self.__doc = doc
        self.__value_props = {}

    def set(self, prop, value):
        if not isinstance(value, odml2.Value):
            raise ValueError("Type odml2.Value expected, but was %s" % type(value))
        self.__value_props[prop] = value

    def remove(self, key):
        del self.__value_props[key]

    def clear(self):
        self.__value_props.clear()

    def get(self, key):
        return self.__value_props.get(key)

    def keys(self):
        for key in self.__value_props:
            yield key


class MemNameSpace(base.BaseNameSpace):

    def __init__(self, prefix, uri):
        self.__prefix = prefix
        self.__uri = uri

    def get_prefix(self):
        return self.__prefix

    def get_uri(self):
        return self.__uri

    def set_uri(self, uri):
        self.__uri = uri


class MemPropertyDefinition(base.BasePropertyDefinition):

    def __init__(self, name, definition, types):
        self.__name = name
        self.__definition = definition
        self.__types = types

    def get_name(self):
        return self.__name

    def get_definition(self):
        return self.__definition

    def set_definition(self, definition):
        self.__definition = definition

    def get_types(self):
        return self.__types

    def set_types(self, types):
        self.__types = types

    # noinspection PyShadowingBuiltins
    def add_type(self, type):
        self.__types = self.__types + (type, )

    # noinspection PyShadowingBuiltins
    def remove_type(self, type):
        self.__types = tuple(t for t in self.__types if t != type)


class MemTypeDefinition(base.BaseTypeDefinition):

    def __init__(self, name, definition, properties):
        self.__name = name
        self.__definition = definition
        self.__properties = properties

    def get_name(self):
        return self.__name

    def get_definition(self):
        return self.__definition

    def set_definition(self, definition):
        self.__definition = definition

    def get_properties(self):
        return self.__properties

    def set_properties(self, props):
        self.__properties = props

    def add_property(self, prop):
        self.__properties = self.__properties + (prop, )

    def remove_property(self, prop):
        self.__properties = tuple(p for p in self.__properties if p != prop)
