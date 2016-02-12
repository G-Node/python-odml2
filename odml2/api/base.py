# coding=UTF-8

# Copyright (c) 2015, Adrian Stoewer (adrian.stoewer@rz.ifi.lmu.de)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the project.

import six
import abc
import datetime
from collections import OrderedDict, MutableMapping

import odml2

"""
Provides abstract base classes for back-end implementations.
"""

# NOTICE: Classes have a getter/setter pattern for attributes instead of
#         properties in order to distinguish more precisely between read-only
#         and read-write attributes.


@six.add_metaclass(abc.ABCMeta)
class BaseDocument(object):
    """
    Low level access to data of an odML2 document.
    """

    @abc.abstractmethod
    def is_attached(self):
        """
        Returns whether the back-end is attached or not. Attached back-ends
        persist changes immediately.

        :return: True if attached, False otherwise.
        :rtype: bool
        """
        pass

    @abc.abstractmethod
    def is_writable(self):
        """
        Returns whether the back-end is writable or not.

        :return: True if data can be written to the back-end, False otherwise.
        """
        pass

    def assert_writable(self):
        if not self.is_writable():
            raise RuntimeError("The document is not writable!")

    @abc.abstractmethod
    def get_uri(self):
        """
        The location where the data for this document is stored. Can be None for newly created,
        non saved documents.

        :return: The uri to the document data.
        :rtype: str
        """
        pass

    @abc.abstractmethod
    def set_uri(self, uri):
        pass

    @abc.abstractmethod
    def get_date(self):
        """
        :return: The creation date of the document.
        :rtype: datetime.datetime
        """

    @abc.abstractmethod
    def set_date(self, date):
        pass

    @abc.abstractmethod
    def get_author(self):
        """
        The author of the document. Is None unless the author was specified.

        :return: The name of the documents author.
        :rtype: str
        """

    @abc.abstractmethod
    def set_author(self, author):
        pass

    @abc.abstractmethod
    def get_version(self):
        """
        :return: The document version (default is 1).
        :rtype: int
        """

    @abc.abstractmethod
    def set_version(self, version):
        pass

    # noinspection PyShadowingBuiltins
    @abc.abstractmethod
    def create_root(self, type, uuid, label, reference):
        """
        Create a new root section. If the document is not empty, all sections will be replaced.

        :param type:        The type of the section.
        :param uuid:        The uuid of the section (optional), if the uuid is None a random uuid will be chosen.
        :param label:       The label of the section (optional)
        :param reference:   The reference of the section (optional)
        """
        pass

    @abc.abstractmethod
    def get_root(self):
        """
        :return: The uuid of the root section or None if the document is empty.
        :rtype: str
        """
        pass

    @property
    def namespaces(self):
        """
        Access to document namespaces.
        :rtype: BaseNameSpaceMap
        """
        raise NotImplementedError()

    @property
    def property_defs(self):
        """
        Access to document property definitions.
        :rtype: BasePropertyDefMap
        """
        raise NotImplementedError

    @property
    def type_defs(self):
        """
        Access to document type definitions.
        :rtype: BaseTypeDefMap
        """
        raise NotImplementedError()

    @property
    def sections(self):
        """
        Access to ALL document sections.
        :rtype: BaseSectionMap
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def clear(self):
        """
        Remove all sections from the document.
        """
        pass

    @abc.abstractmethod
    def load(self, io, uri=None):
        """
        Fill the document with data from a certain location.

        :param io:  An I/O (StingIO,FileIO) to read the data from.
        :param uri: The uri of the document.
        """
        pass

    @abc.abstractmethod
    def save(self, io, uri=None):
        """
        Save the documents data to a certain location.

        :param io: The I/O to write the data to.
        :param uri: The uri of the document.
        """
        pass

    def to_dict(self):
        root = OrderedDict(author=self.get_author(), date=self.get_date(),
                           document_version=self.get_version(), format_version=2)

        def convert_value(val):
            if val.unit is not None or val.uncertainty is not None:
                return str(val)
            else:
                return val.value

        def convert_ns():
            ns_dict = OrderedDict()
            for ns in self.namespaces.values():
                ns_dict[ns.prefix] = ns.uri
            return ns_dict if len(ns_dict) > 0 else None

        def convert_definitions():
            defs_dict = OrderedDict()
            for pd in self.property_defs.values():
                pd_dict = OrderedDict(types=pd.types)
                definition = pd.definition
                if definition is not None:
                    pd_dict["definition"] = definition
                defs_dict[pd.name] = pd_dict
            for td in self.type_defs.values():
                td_dict = OrderedDict(properties=td.properties)
                definition = td.definition
                if definition is not None:
                    td_dict["definition"] = definition
                defs_dict[td.name] = td_dict
            return defs_dict if len(defs_dict) > 0 else None

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
            sec_dict = OrderedDict(uuid=uuid, type=sec.get_type())
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
        if self.get_root() is not None:
            root["metadata"] = convert_section(self.get_root())
        else:
            root["metadata"] = None
        return root

    def from_dict(self, data):
        if data["format_version"] != 2:
            raise RuntimeError("Format version must be 2")

        self.clear()

        if "author" in data:
            self.set_author(data["author"])
        if "date" in data:
            self.set_date(data["date"])
        if "document_version" in data:
            self.set_version(data["document_version"])

        if "namespaces" in data and data["namespaces"] is not None:
            for prefix, uri in data["namespaces"].items():
                self.namespaces.set(prefix, uri)
        if "definitions" in data and data["definitions"] is not None:
            for name, def_data in data["definitions"].items():
                if "types" in def_data:
                    self.property_defs.set(name, def_data.get("definition"), def_data["types"])
                elif "properties" in def_data:
                    self.type_defs.set(name, def_data.get("definition"), def_data["properties"])

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
                    section.value_properties.set(prop, odml2.Value.from_obj(element))

        if "metadata" in data and data["metadata"] is not None:
            read_section(None, None, data["metadata"])


class BaseNameSpaceMap(MutableMapping):
    """
    Dict like accessor for namespaces of an odML2 document.
    """

    @abc.abstractmethod
    def set(self, prefix, uri):
        pass


class BasePropertyDefMap(MutableMapping):
    """
    Dict like accessor for property definitions of an odML2 document.
    """

    @abc.abstractmethod
    def set(self, name, types=tuple()):
        pass


class BaseTypeDefMap(MutableMapping):
    """
    Dict like accessor for type definitions of an odML2 document.
    """

    # noinspection PyShadowingBuiltins
    @abc.abstractmethod
    def set(self, type, definition=None, properties=tuple()):
        pass


class BaseSectionMap(MutableMapping):
    """
    Dict like accessor for namespaces of a odML2 document.
    """

    # noinspection PyShadowingBuiltins
    @abc.abstractmethod
    def add(self, type, uuid, label, reference, parent_uuid, parent_prop):
        pass

    @abc.abstractmethod
    def add_link(self, uuid, prefix, parent_uuid, parent_prop):
        pass


@six.add_metaclass(abc.ABCMeta)
class BaseSection(object):
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
        :rtype: BaseSectionPropertyMap
        """
        raise NotImplementedError()

    @property
    def value_properties(self):
        """
        :rtype: BasePropertyDefMap
        """
        raise NotImplementedError()


class BaseSectionPropertyMap(MutableMapping):
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
        :type refs: tuple[SectionRef]
        """
        pass


class SectionRef(object):
    """
    Holds information about a reference to a section used in a section property.
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


class BaseValuePropertyMap(MutableMapping):
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
