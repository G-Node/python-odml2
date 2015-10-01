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

__all__ = ("BackEnd", "SecData", "ValData")

from abc import abstractmethod
from uuid import uuid4
import odml2.compat as compat


class BackEnd(compat.ABC):
    """
    A base class for a back-end that represents data of an odML document and provides access to it.
    """

    @abstractmethod
    def has_root(self):
        raise NotImplemented()

    @abstractmethod
    def root_get(self):
        raise NotImplemented()

    @abstractmethod
    def root_reset(self, section):
        raise NotImplemented()

    @abstractmethod
    def section_exists(self, uuid):
        raise NotImplemented()

    @abstractmethod
    def section_get(self, uuid):
        raise NotImplemented()

    @abstractmethod
    def section_update(self, section):
        raise NotImplemented()

    @abstractmethod
    def section_remove(self, uuid):
        raise NotImplemented()

    @abstractmethod
    def section_get_properties(self, uuid):
        raise NotImplemented()

    @abstractmethod
    def property_has_sections(self, uuid, prop):
        raise NotImplemented()

    @abstractmethod
    def property_has_value(self, uuid, prop):
        raise NotImplemented()

    @abstractmethod
    def property_get_sections(self, uuid, prop):
        raise NotImplemented()

    @abstractmethod
    def property_add_section(self, uuid, prop, section):
        raise NotImplemented()

    @abstractmethod
    def property_remove_section(self, uuid, prop, child_uuid):
        raise NotImplemented()

    @abstractmethod
    def property_get_value(self, uuid, prop):
        raise NotImplemented()

    @abstractmethod
    def property_set_value(self, uuid, prop, value):
        raise NotImplemented()

    @abstractmethod
    def property_remove_value(self, uuid, prop):
        raise NotImplemented()

    @abstractmethod
    def store(self, file_name):
        raise NotImplemented()


class SecData(object):
    """
    Simple section representation used by Context
    """

    def __init__(self, typ, uuid=None, label=None, reference=None):
        self.__type = typ
        self.__uuid = str(uuid4()) if uuid is None else uuid
        self.__label = label
        self.__reference = reference

    @property
    def type(self):
        return self.__type

    @property
    def uuid(self):
        return self.__uuid

    @property
    def label(self):
        return self.__label

    @property
    def reference(self):
        return self.__reference

    def using(self, typ=None, uuid=None, label=None, reference=None):
        return SecData(
            typ if typ is not None else self.type,
            uuid if uuid is not None else self.uuid,
            label if label is not None else self.label,
            reference if reference is not None else self.reference,
        )

    @classmethod
    def create_from(cls, other):
        return SecData(other.type, other.uuid, other.label, other.reference)


class ValData(object):
    """
    Simple value representation use by Context
    """

    def __init__(self, value, unit=None, uncertainty=None):
        self.__value = value
        self.__unit = unit
        self.__uncertainty = uncertainty

    @property
    def value(self):
        return self.__value

    @property
    def unit(self):
        return self.__unit

    @property
    def uncertainty(self):
        return self.__uncertainty

    def using(self, value=None, unit=None, uncertainty=None):
        return ValData(
            value if value is not None else self.value,
            unit if unit is not None else self.unit,
            uncertainty if uncertainty is not None else self.uncertainty
        )
