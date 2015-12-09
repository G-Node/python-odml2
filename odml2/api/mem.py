# coding=UTF-8

# Copyright (c) 2015, Adrian Stoewer (adrian.stoewer@rz.ifi.lmu.de)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the project.

from odml2.api import base

"""
Provides abstract base classes for back-end implementations.
"""

# NOTICE: Classes have a getter/setter pattern for attributes instead of
#         properties in order to distinguish more precisely between read-only
#         and read-write attributes.


class MemDocument(base.BaseDocument):

    def is_attached(self):
        pass

    def is_writable(self):
        pass

    def get_uri(self,):
        pass

    def get_date(self):
        pass

    def set_date(self, date):
        pass

    def get_author(self):
        pass

    def set_author(self, author):
        pass

    def get_version(self):
        pass

    def set_version(self):
        pass

    # noinspection PyShadowingBuiltins
    def create_root(self, type, uuid, label, reference):
        pass

    def get_root(self):
        pass

    @property
    def namespaces(self):
        pass

    @property
    def property_defs(self):
        pass

    @property
    def type_defs(self):
        pass

    @property
    def sections(self):
        pass

    @classmethod
    def load(cls, path):
        pass

    def close(self):
        pass

    def save(self, path):
        pass


class MemNameSpaceDict(base.BaseNameSpaceDict):

    def get(self, key):
        pass

    def keys(self):
        pass


class MemPropertyDefDict(base.BasePropertyDefDict):

    def get(self, key):
        pass

    def keys(self):
        pass


class MemTypeDefDict(base.BaseTypeDefDict):

    def get(self, key):
        pass

    def keys(self):
        pass


class MemSectionDict(base.BaseSectionDict):

    def get(self, key):
        pass

    def keys(self):
        pass


class MemSection(base.BaseSection):

    def get_uuid(self):
        pass

    def get_type(self):
        pass

    # noinspection PyShadowingBuiltins
    def set_type(self, type, check=False):
        pass

    def get_label(self):
        pass

    def set_label(self, label):
        pass

    def get_reference(self):
        pass

    def set_reference(self):
        pass

    @property
    def section_properties(self):
        pass

    @property
    def value_properties(self):
        pass


class MemSectionPropertyDict(base.BaseSectionPropertyDict):

    def get(self, key):
        pass

    def keys(self):
        pass


class MemValuePropertyDict(base.BaseValuePropertyDict):

    def get(self, key):
        pass

    def keys(self):
        pass


class MemNameSpace(base.BaseNameSpace):

    def get_name(self):
        pass

    def get_uri(self):
        pass

    def set_uri(self):
        pass


class MemPropertyDefinition(base.BasePropertyDefinition):

    def get_name(self):
        pass

    def get_definition(self):
        pass

    def set_definition(self):
        pass

    def get_types(self):
        pass

    # noinspection PyShadowingBuiltins
    def add_type(self, type):
        pass

    # noinspection PyShadowingBuiltins
    def remove_type(self, type):
        pass


class MemTypeDefinition(base.BaseTypeDefinition):

    def get_name(self):
        pass

    def get_definition(self):
        pass

    def set_definition(self):
        pass

    def get_properties(self):
        pass

    def add_property(self, prop):
        pass

    def remove_property(self, prop):
        pass
