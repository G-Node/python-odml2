# coding=UTF-8

# Copyright (c) 2015, Adrian Stoewer (adrian.stoewer@rz.ifi.lmu.de)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the project.

import abc
import collections
from odml2 import compat, value_from

"""
Provides abstract base classes for back-end implementations.
"""

# NOTICE: Classes have a getter/setter pattern for attributes instead of
#         properties in order to distinguish more precisely between read-only
#         and read-write attributes.

# TODO evaluate use of abc
# TODO evaluate use of type hints in docstrings


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
    def set_uri(self, uri):
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
    def set_version(self, version):
        pass

    # noinspection PyShadowingBuiltins
    @abc.abstractmethod
    def create_root(self, type, uuid, label, reference):
        pass

    @abc.abstractmethod
    def get_root(self):
        pass

    @property
    def namespaces(self):
        """
        Access to document namespaces.
        :rtype: BaseNameSpaceDict
        """
        raise NotImplementedError()

    @property
    def property_defs(self):
        """
        Access to document property definitions.
        :rtype: BasePropertyDefDict
        """
        raise NotImplementedError

    @property
    def type_defs(self):
        """
        Access to document type definitions.
        :rtype: BaseTypeDefDict
        """
        raise NotImplementedError()

    @property
    def sections(self):
        """
        Access to ALL document sections.
        :rtype: BaseSectionDict
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def clear(self):
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

    def to_dict(self):
        root = {"author": self.get_author(), "date": self.get_date(), "document_version": self.get_version(),
                "format_version": (2, 0)}

        def convert_value(val):
            if val.unit is not None or val.uncertainty is not None:
                return str(val)
            else:
                return val.value

        def convert_ns():
            ns_dict = {}
            for ns in self.namespaces.values():
                ns_dict[ns.get_prefix()] = ns.get_uri()
            return ns_dict

        def convert_definitions():
            defs_dict = {}
            for pd in self.property_defs.values():
                pd_dict = {"types": pd.get_types()}
                definition = pd.get_definition()
                if definition is not None:
                    pd_dict["definition"] = definition
                defs_dict[pd.get_name()] = pd_dict
            for td in self.type_defs.values():
                td_dict = {"properties": td.get_properties()}
                definition = td.get_definition()
                if definition is not None:
                    td_dict["definition"] = definition
                defs_dict[td.get_type()] = td_dict
            return defs_dict

        def convert_ref(ref):
            if ref.is_link:
                link = ref.uuid
                if ref.namespace is not None:
                    link = ref.namespace + ":" + link
                return link
            else:
                return convert_section(ref.uuid)

        def convert_section(uuid):
            sec = self.sections[uuid]
            sec_dict = {"uuid": uuid, "type": sec.get_type()}
            label = sec.get_label()
            if label is not None:
                sec_dict["label"] = label
            reference = sec.get_reference()
            if reference is not None:
                sec_dict["reference"] = reference
            for prop in sec.value_properties:
                value = sec.value_properties[prop]
                sec_dict[prop] = convert_value(value)
            for prop in sec.section_properties:
                refs = sec.section_properties[prop]
                if len(refs) == 1:
                    sec_dict[prop] = convert_ref(refs[0])
                else:
                    sec_dict[prop] = [convert_ref(ref) for ref in refs]
            return sec_dict

        root["namespaces"] = convert_ns()
        root["definitions"] = convert_definitions()
        root["metadata"] = convert_section(self.get_root())
        return root

    def from_dict(self, data):
        if data["format_version"] != (2, 0):
            raise RuntimeError("Format version must be 2.0")

        self.clear()

        if "author" in data:
            self.set_author(data["author"])
        if "date" in data:
            self.set_date(data["date"])
        if "document_version" in data:
            self.set_version(data["document_version"])

        if "namespaces" in data and data["namespaces"] is not None:
            for prefix, uri in enumerate(data["namespaces"]):
                self.namespaces.add(prefix, uri)
        if "definitions" in data and data["definitions"] is not None:
            for name, def_data in enumerate(data["definitions"]):
                if "types" in def_data:
                    self.property_defs.add(name, def_data.get("definition"), def_data["types"])
                elif "properties" in def_data:
                    self.type_defs.add(name, def_data.get("definition"), def_data["properties"])

        def read_section(parent_uuid, parent_prop, sec_data):
            if parent_uuid is None:
                self.create_root(sec_data["type"], sec_data["uuid"], sec_data.get("label"), sec_data.get("reference"))
            else:
                self.sections.add(sec_data["type"], sec_data["uuid"], sec_data.get("label"), sec_data.get("reference"),
                                  parent_uuid, parent_prop)
            properties = ((k, v) for k, v in sec_data.items() if k not in ("type", "uuid", "label", "reference"))
            for prop, element in properties:
                if isinstance(element, dict):
                    read_section(sec_data["uuid"], prop, element)
                elif isinstance(element, list):
                    for sub_elem in element:
                        read_section(sec_data["uuid"], prop, sub_elem)
                else:
                    section = self.sections[sec_data["uuid"]]
                    section.value_properties.set(prop, value_from(element))

        read_section(None, None, data["metadata"])


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

    @abc.abstractmethod
    def remove(self, key):
        pass

    @abc.abstractmethod
    def clear(self):
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

    def __delitem__(self, key):
        self.remove(key)

    def __contains__(self, item):
        return item in self.keys() or item in self.values()

    def __iter__(self):
        return self.keys()

    def __len__(self):
        return len([self.keys()])

collections.Iterable.register(_DictLike)


class BaseNameSpaceDict(_DictLike):
    """
    Dict like accessor for namespaces of an odML2 document.
    """

    @abc.abstractmethod
    def add(self, prefix, uri):
        pass

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
    def add(self, name, types=tuple()):
        pass

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

    # noinspection PyShadowingBuiltins
    @abc.abstractmethod
    def add(self, type, definition=None, properties=tuple()):
        pass

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

    # noinspection PyShadowingBuiltins
    @abc.abstractmethod
    def add(self, type, uuid, label, reference, parent_uuid, parent_prop):
        pass

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
    def is_linked(self):
        pass

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
    def set_reference(self, reference):
        pass

    @property
    def section_properties(self):
        """
        :rtype: BaseSectionPropertyDict
        """
        raise NotImplementedError()

    @property
    def value_properties(self):
        """
        :rtype: BasePropertyDefDict
        """
        raise NotImplementedError()


class BaseSectionPropertyDict(_DictLike):
    """
    Dict like accessor for section properties.
    """

    @abc.abstractmethod
    def set(self, prop, refs):
        """
        Set the section ids for a section property.
        :param prop: The property name.
        :type prop: str
        :param refs: Tuple of references to sections.
        :type refs: tuple[Ref]
        """
        pass

    @abc.abstractmethod
    def get(self, key):
        """
        :param key: The namespaces name.
        :return: tuple[Ref]
        """
        pass

    @abc.abstractmethod
    def keys(self):
        """
        Iterable containing all namespaces of a document.
        :rtype: collections.Iterable[str]
        """
        pass

    class Ref(object):
        """
        Holds information about a section used in a section property.
        """

        def __init__(self, uuid, namespace, is_link):
            self.__uuid = uuid
            self.__namespace = namespace
            self.__is_link = is_link

        @property
        def uuid(self):
            return self.__uuid

        @property
        def namespace(self):
            return self.__namespace

        @property
        def is_link(self):
            return self.__is_link


class BaseValuePropertyDict(_DictLike):
    """
    Dict like accessor for section properties.
    """

    @abc.abstractmethod
    def set(self, prop, value):
        """
        Set the value for a property.
        :param prop: The name of the property.
        :type prop: str
        :param value: The value to set.
        :type value: odml2.Value
        """
        pass

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

    def __setitem__(self, key, value):
        self.set(key, value)


class BaseNameSpace(compat.ABC):
    """
    Low level access to the name-spaces of an odML2 document.
    """

    @abc.abstractmethod
    def get_prefix(self):
        pass

    @abc.abstractmethod
    def get_uri(self):
        pass

    @abc.abstractmethod
    def set_uri(self, uri):
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
    def set_definition(self, definition):
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
    def set_definition(self, definition):
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
