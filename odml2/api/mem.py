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
from sortedcontainers import SortedDict
import odml2
from odml2.api import base


"""
Provides abstract base classes for back-end implementations.
"""

# NOTICE: Classes have a getter/setter pattern for attributes instead of
#         properties in order to distinguish more precisely between read-only
#         and read-write attributes.

# TODO add section links
# TODO sanitize and check input (dates, name identifiers, type identifiers, prefixes, URIs)


class MemDocument(base.BaseDocument):

    def __init__(self, is_writable=True):
        self.__is_writable = is_writable
        self.__uri = None
        self.__date = None
        self.__author = None
        self.__version = 1
        self.__root = None
        self.__namespaces = MemNameSpaceMap(self)
        self.__property_defs = MemPropertyDefMap(self)
        self.__type_defs = MemTypeDefMap(self)
        self.__sections = MemSectionMap(self)

    def is_attached(self):
        return False

    def is_writable(self):
        return self.__is_writable

    def _set_writable(self, writable):
        self.__is_writable = writable

    def get_uri(self,):
        return self.__uri

    def set_uri(self, uri):
        self.assert_writable()
        self.__uri = uri

    def get_date(self):
        return self.__date

    def set_date(self, date):
        self.assert_writable()
        self.__date = date

    def get_author(self):
        return self.__author

    def set_author(self, author):
        self.assert_writable()
        self.__author = author

    def get_version(self):
        return self.__version

    def set_version(self, version):
        self.assert_writable()
        self.__version = version

    # noinspection PyShadowingBuiltins
    def create_root(self, type, uuid, label, reference):
        self.sections.add(type, uuid, label, reference, None, None)

    def get_root(self):
        return self.__root

    def set_root(self, uuid):
        self.assert_writable()
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
        self.assert_writable()
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
    def load(self, io, uri=None):
        pass

    @abc.abstractmethod
    def save(self, io, uri=None):
        pass


class MemNameSpaceMap(base.BaseNameSpaceMap):

    def __init__(self, doc):
        self.__doc = doc
        self.__namespaces = SortedDict()

    def set(self, prefix, uri):
        self.__doc.assert_writable()
        self.__namespaces[prefix] = odml2.NameSpace(prefix, uri)

    def __setitem__(self, prefix, ns):
        self.__doc.assert_writable()
        if prefix != ns.prefix:
            raise KeyError("NameSpace prefix mismatch: %s != %s" % (prefix, ns.prefix))
        self.set(prefix, ns.uri)

    def __getitem__(self, prefix):
        return self.__namespaces[prefix]

    def __delitem__(self, prefix):
        self.__doc.assert_writable()
        del self.__namespaces[prefix]

    def __len__(self):
        return len(self.__namespaces)

    def __iter__(self):
        return iter(self.__namespaces)


class MemPropertyDefMap(base.BasePropertyDefMap):

    def __init__(self, doc):
        self.__doc = doc
        self.__property_defs = SortedDict()

    def set(self, name, definition=None, types=frozenset()):
        self.__doc.assert_writable()
        self.__property_defs[name] = odml2.PropertyDef(name, definition, types)

    def __setitem__(self, name, pd):
        self.__doc.assert_writable()
        if name != pd.name:
            raise KeyError("Property name mismatch: %s != %s" % (name, pd.name))
        self.set(name, pd.definition, pd.types)

    def __getitem__(self, name):
        return self.__property_defs[name]

    def __delitem__(self, name):
        self.__doc.assert_writable()
        del self.__property_defs[name]

    def __len__(self):
        return len(self.__property_defs)

    def __iter__(self):
        return iter(self.__property_defs)


class MemTypeDefMap(base.BaseTypeDefMap):

    def __init__(self, doc):
        self.__doc = doc
        self.__type_defs = SortedDict()

    def set(self, name, definition=None, properties=frozenset()):
        self.__doc.assert_writable()
        self.__type_defs[name] = odml2.TypeDef(name, definition, properties)

    def __setitem__(self, name, td):
        self.__doc.assert_writable()
        if name != td.name:
            raise KeyError("Name mismatch: %s != %s" % (name, td.name))
        self.set(name, td.definition, td.properties)

    def __getitem__(self, name):
        return self.__type_defs[name]

    def __delitem__(self, name):
        self.__doc.assert_writable()
        del self.__type_defs[name]

    def __len__(self):
        return len(self.__type_defs)

    def __iter__(self):
        return iter(self.__type_defs)


class MemSectionMap(base.BaseSectionMap):

    def __init__(self, doc):
        self.__doc = doc
        self.__sections = {}

    # noinspection PyShadowingBuiltins
    def add(self, type, uuid, label, reference, parent_uuid, parent_prop):
        self.__doc.assert_writable()
        if isinstance(uuid, UUID):
            uuid = str(uuid)
        if parent_uuid is None and parent_prop is None:
            # add a new root section
            self.clear()
            self.__sections[uuid] = MemSection(self.__doc, type, uuid, label, reference, is_linked=False)
            self.__doc.set_root(uuid)
        elif parent_uuid is not None and parent_prop is not None:
            # add a new sub section
            if uuid in self:
                raise ValueError("A section with the given uuid '%s' does already exist" % uuid)

            parent = self.get(parent_uuid)
            if parent is None:
                raise ValueError("Parent section with uuid '%s' does not exist" % parent_uuid)

            if parent_prop in parent.value_properties:
                del parent.value_properties[parent_prop]

            refs = (base.SectionRef(uuid, None, False), )
            if parent_prop in parent.section_properties:
                refs = parent.section_properties[parent_prop] + refs
            parent.section_properties.set(parent_prop, refs)
            self.__sections[uuid] = MemSection(self.__doc, type, uuid, label, reference, is_linked=False)
        else:
            raise RuntimeError("Parent uuid and prop must be either both None or both not None!")

    def add_link(self, uuid, prefix, parent_uuid, parent_prop):
        parent = self[parent_uuid]

        if parent_prop in parent.value_properties:
            del parent.value_properties[parent_prop]

        refs = (base.SectionRef(uuid, prefix, True), )
        if parent_prop in parent.section_properties:
            refs = parent.section_properties[parent_prop] + refs

        parent.section_properties.set(parent_prop, refs)

    def __setitem__(self, uuid, value):
        self.__doc.assert_writable()
        # TODO maybe implement later (but is not needed at the moment)
        raise NotImplementedError()

    def __getitem__(self, uuid):
        return self.__sections[uuid]

    def __delitem__(self, uuid):
        self.__doc.assert_writable()
        if uuid not in self:
            raise KeyError("A section with the given uuid '%s' does not exist" % uuid)

        def remove_with_subsections(section_id):
            for refs in self[section_id].section_properties.values():
                for ref in refs:
                    if not ref.is_link:
                        remove_with_subsections(ref.uuid)
            for sec in self.__sections.values():
                for p, refs in sec.section_properties.items():
                    sec.section_properties[p] = tuple(ref for ref in refs if ref.uuid != section_id)
            del self.__sections[section_id]

        remove_with_subsections(uuid)

        if len(self.__sections) == 0:
            self.__doc.set_root(None)

    def __len__(self):
        return len(self.__sections)

    def __iter__(self):
        return iter(self.__sections)


class MemSection(base.BaseSection):

    # noinspection PyShadowingBuiltins
    def __init__(self, doc, type, uuid, label, reference, is_linked):
        self.__doc = doc
        self.__type = type
        self.__uuid = uuid
        self.__label = label
        self.__reference = reference
        self.__is_linked = is_linked
        self.__sections_properties = MemSectionPropertyMap(doc)
        self.__value_properties = MemValuePropertyMap(doc)

    def is_linked(self):
        return self.__is_linked

    def get_uuid(self):
        return self.__uuid

    def get_type(self):
        return self.__type

    # noinspection PyShadowingBuiltins
    def set_type(self, type, check=False):
        self.__doc.assert_writable()
        self.__type = type

    def get_label(self):
        return self.__label

    def set_label(self, label):
        self.__doc.assert_writable()
        self.__label = label

    def get_reference(self):
        return self.__reference

    def set_reference(self, reference):
        self.__doc.assert_writable()
        self.__reference = reference

    @property
    def section_properties(self):
        return self.__sections_properties

    @property
    def value_properties(self):
        return self.__value_properties


class MemSectionPropertyMap(base.BaseSectionPropertyMap):

    def __init__(self, doc):
        self.__doc = doc
        self.__section_props = SortedDict()

    def set(self, prop, refs):
        self.__doc.assert_writable()
        self.__section_props[prop] = refs

    def __setitem__(self, prop, refs):
        self.__doc.assert_writable()
        self.__section_props[prop] = refs

    def __getitem__(self, prop):
        return self.__section_props[prop]

    def __delitem__(self, prop):
        self.__doc.assert_writable()
        del self.__section_props[prop]

    def __len__(self):
        return len(self.__section_props)

    def __iter__(self):
        return iter(self.__section_props)


class MemValuePropertyMap(base.BaseValuePropertyMap):

    def __init__(self, doc):
        self.__doc = doc
        self.__value_props = SortedDict()

    def set(self, prop, value):
        self.__doc.assert_writable()
        if not isinstance(value, odml2.Value):
            raise ValueError("Type odml2.Value expected, but was %s" % type(value))
        self.__value_props[prop] = value

    def __setitem__(self, prop, value):
        self.__doc.assert_writable()
        self.set(prop, value)

    def __getitem__(self, key):
        return self.__value_props[key]

    def __delitem__(self, prop):
        self.__doc.assert_writable()
        del self.__value_props[prop]

    def __len__(self):
        return len(self.__value_props)

    def __iter__(self):
        return iter(self.__value_props)
