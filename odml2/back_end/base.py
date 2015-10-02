# coding=UTF-8

# Copyright (c) 2015, Adrian Stoewer (adrian.stoewer@rz.ifi.lmu.de)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the project.

"""
Contains classes and base classes needed for all back-end implementations.
"""

__all__ = ("BackEnd", )

import abc
from odml2 import compat


class BackEnd(compat.ABC):
    """
    A base class for a back-end that represents data of an odML document and provides access to it.
    """

    @abc.abstractproperty
    def autosave(self):
        raise NotImplemented()

    @abc.abstractmethod
    def author_get(self):
        raise NotImplemented()

    @abc.abstractmethod
    def author_set(self, author):
        raise NotImplemented()

    @abc.abstractmethod
    def date_get(self):
        raise NotImplemented()

    @abc.abstractmethod
    def date_set(self, date):
        raise NotImplemented()

    @abc.abstractmethod
    def root_exists(self):
        raise NotImplemented()

    @abc.abstractmethod
    def root_get(self):
        raise NotImplemented()

    @abc.abstractmethod
    def root_create(self, typ, uuid=None, label=None, reference=None):
        raise NotImplemented()

    @abc.abstractmethod
    def section_exists(self, uuid):
        raise NotImplemented()

    @abc.abstractmethod
    def section_get_type(self, uuid):
        raise NotImplemented()

    @abc.abstractmethod
    def section_set_type(self, uuid, typ):
        raise NotImplemented()

    @abc.abstractmethod
    def section_get_label(self, uuid):
        raise NotImplemented()

    @abc.abstractmethod
    def section_set_label(self, uuid, label):
        raise NotImplemented()

    @abc.abstractmethod
    def section_get_reference(self, uuid):
        raise NotImplemented()

    @abc.abstractmethod
    def section_set_reference(self, uuid, reference):
        raise NotImplemented()

    @abc.abstractmethod
    def section_remove(self, uuid):
        raise NotImplemented()

    @abc.abstractmethod
    def section_get_properties(self, uuid):
        raise NotImplemented()

    @abc.abstractmethod
    def property_has_sections(self, parent_uuid, prop):
        raise NotImplemented()

    @abc.abstractmethod
    def property_get_sections(self, parent_uuid, prop):
        raise NotImplemented()

    @abc.abstractmethod
    def property_add_section(self, parent_uuid, prop, typ, uuid=None, label=None, reference=None):
        raise NotImplemented()

    @abc.abstractmethod
    def property_has_value(self, parent_uuid, prop):
        raise NotImplemented()

    @abc.abstractmethod
    def property_get_value(self, parent_uuid, prop):
        raise NotImplemented()

    @abc.abstractmethod
    def property_set_value(self, parent_uuid, prop, value):
        raise NotImplemented()

    @abc.abstractmethod
    def property_remove_value(self, parent_uuid, prop):
        raise NotImplemented()

    @abc.abstractmethod
    def property_remove(self, parent_uuid, prop):
        raise NotImplemented()

    @abc.abstractmethod
    def store(self, location):
        raise NotImplemented()

    @abc.abstractmethod
    def add_all(self, back_end):
        raise NotImplemented()
