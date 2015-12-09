# coding=UTF-8

# Copyright (c) 2015, Adrian Stoewer (adrian.stoewer@rz.ifi.lmu.de)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the project.

import abc
from odml2 import compat

"""
Provides abstract base classes for back-end implementations.
"""

# NOTICE: Classes have a getter/setter pattern for attributes instead of
#         properties in order to distinguish more precisely between read-only
#         and read-write attributes.


class BaseDocument(compat.ABC):
    """
    Low level access to an odML2 document
    """

    @abc.abstractmethod
    def is_attached(self):
        pass

    @abc.abstractmethod
    def is_writable(self):
        pass

    @abc.abstractmethod
    def get_uri(self,):
        pass

    @abc.abstractmethod
    def get_date(self):
        pass

    @abc.abstractmethod
    def set_date(self, date):
        pass

    @abc.abstractmethod
    def get_author(self):
        pass

    @abc.abstractmethod
    def set_author(self, author):
        pass

    @abc.abstractmethod
    def get_version(self):
        pass

    @abc.abstractmethod
    def set_version(self):
        pass

    # noinspection PyShadowingBuiltins
    @abc.abstractmethod
    def create_root(self, type, uuid, label, reference):
        pass

    @abc.abstractmethod
    def get_root(self):
        pass

    @abc.abstractproperty
    def namespaces(self):
        """
        Access to document namespaces.
        :rtype: BaseNameSpaceDict
        """
        pass

    @abc.abstractproperty
    def property_defs(self):
        """
        Access to document property definitions.
        :rtype: BasePropertyDefDict
        """
        pass

    @abc.abstractproperty
    def type_defs(self):
        """
        Access to document type definitions.
        :rtype: BaseTypeDefDict
        """
        pass

    @abc.abstractproperty
    def sections(self):
        """
        Access to ALL document sections.
        :rtype: BaseSectionDict
        """
        pass

    @abc.abstractmethod
    def load(self, path):
        pass

    @abc.abstractmethod
    def close(self):
        pass

    @abc.abstractmethod
    def save(self, path):
        pass


class _DictLike(compat.ABC):
    """
    Dictionary like access to related objects.
    """

    @abc.abstractmethod
    def get(self, key):
        """
        :param key: The key of the related object.
        :return: object
        """
        pass

    @abc.abstractmethod
    def keys(self):
        """
        Iterable containing all keys.
        :rtype: collections.Iterable[str]
        """
        pass

    def values(self):
        for key in self.keys():
            yield self[key]

    def items(self):
        for key in self.keys():
            yield (key, self[key])

    def __getitem__(self, key):
        item = self.get(key)
        if item is None:
            raise KeyError(key)
        return item

    def __contains__(self, item):
        return item in self.keys() or item in self.values()

    def __iter__(self):
        return self.keys()

    def __len__(self):
        return len(tuple(self))


class BaseNameSpaceDict(_DictLike):
    """
    Dict like accessor for namespaces of an odML2 document.
    """

    @abc.abstractmethod
    def get(self, key):
        """
        :param key: The namespaces name.
        :return: BaseNameSpace
        """
        pass

    @abc.abstractmethod
    def keys(self):
        """
        Iterable containing all namespaces of a document.
        :rtype: collections.Iterable[str]
        """
        pass


class BasePropertyDefDict(_DictLike):
    """
    Dict like accessor for property definitions of an odML2 document.
    """

    @abc.abstractmethod
    def get(self, key):
        """
        :param key: The namespaces name.
        :return: BasePropertyDefinition
        """
        pass

    @abc.abstractmethod
    def keys(self):
        """
        Iterable containing all namespaces of a document.
        :rtype: collections.Iterable[str]
        """
        pass


class BaseTypeDefDict(_DictLike):
    """
    Dict like accessor for type definitions of an odML2 document.
    """

    @abc.abstractmethod
    def get(self, key):
        """
        :param key: The namespaces name.
        :return: BaseTypeDefinition
        """
        pass

    @abc.abstractmethod
    def keys(self):
        """
        Iterable containing all namespaces of a document.
        :rtype: collections.Iterable[str]
        """
        pass


class BaseSectionDict(_DictLike):
    """
    Dict like accessor for namespaces of a odML2 document.
    """

    @abc.abstractmethod
    def get(self, key):
        """
        :param key: The namespaces name.
        :return: BaseSection
        """
        pass

    @abc.abstractmethod
    def keys(self):
        """
        Iterable containing all namespaces of a document.
        :rtype: collections.Iterable[str]
        """
        pass


class BaseSection(compat.ABC):
    """
    Low level access to a section within a document.
    """

    @abc.abstractmethod
    def get_uuid(self):
        pass

    @abc.abstractmethod
    def get_type(self):
        pass

    # noinspection PyShadowingBuiltins
    @abc.abstractmethod
    def set_type(self, type, check=False):
        pass

    @abc.abstractmethod
    def get_label(self):
        pass

    @abc.abstractmethod
    def set_label(self, label):
        pass

    @abc.abstractmethod
    def get_reference(self):
        pass

    @abc.abstractmethod
    def set_reference(self):
        pass

    @abc.abstractproperty
    def section_properties(self):
        pass

    @abc.abstractproperty
    def value_properties(self):
        pass


class BaseSectionPropertyDict(_DictLike):
    """
    Dict like accessor for section properties.
    """

    @abc.abstractmethod
    def get(self, key):
        """
        :param key: The namespaces name.
        :return: tuple[BaseSection]
        """
        pass

    @abc.abstractmethod
    def keys(self):
        """
        Iterable containing all namespaces of a document.
        :rtype: collections.Iterable[str]
        """
        pass


class BaseValuePropertyDict(_DictLike):
    """
    Dict like accessor for section properties.
    """

    @abc.abstractmethod
    def get(self, key):
        """
        :param key: The namespaces name.
        :return: tuple[odml2.Value]
        """
        pass

    @abc.abstractmethod
    def keys(self):
        """
        Iterable containing all namespaces of a document.
        :rtype: collections.Iterable[str]
        """
        pass


class BaseNameSpace(compat.ABC):
    """
    Low level access to the name-spaces of an odML2 document.
    """

    @abc.abstractmethod
    def get_name(self):
        pass

    @abc.abstractmethod
    def get_uri(self):
        pass

    @abc.abstractmethod
    def set_uri(self):
        pass


class BasePropertyDefinition(compat.ABC):
    """
    Low level access to a property definition of an odML2 document.
    """

    @abc.abstractmethod
    def get_name(self):
        pass

    @abc.abstractmethod
    def get_definition(self):
        pass

    @abc.abstractmethod
    def set_definition(self):
        pass

    @abc.abstractmethod
    def get_types(self):
        pass

    # noinspection PyShadowingBuiltins
    @abc.abstractmethod
    def add_type(self, type):
        pass

    # noinspection PyShadowingBuiltins
    @abc.abstractmethod
    def remove_type(self, type):
        pass


class BaseTypeDefinition(compat.ABC):
    """
    Low-level access to a type definition of an odML2 document.
    """

    @abc.abstractmethod
    def get_name(self):
        pass

    @abc.abstractmethod
    def get_definition(self):
        pass

    @abc.abstractmethod
    def set_definition(self):
        pass

    @abc.abstractmethod
    def get_properties(self):
        pass

    @abc.abstractmethod
    def add_property(self, prop):
        pass

    @abc.abstractmethod
    def remove_property(self, prop):
        pass
