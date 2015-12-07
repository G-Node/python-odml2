# coding=UTF-8

# Copyright (c) 2015, Adrian Stoewer (adrian.stoewer@rz.ifi.lmu.de)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the project.

import abc

import odml2
from odml2 import compat

__all__ = ("DocumentBackEnd", "MetadataBackEnd", "TerminologyBeckEnd")


class DocumentBackEnd(compat.ABC):

    def __init__(self, metadata, terms):
        """
        :type metadata: MetadataBackEnd
        :type terms: TerminologyBeckEnd
        """
        self.__metadata = metadata
        self.__terms = terms

    @property
    def metadata(self):
        return self.__metadata

    @property
    def terms(self):
        return self.__terms

    @abc.abstractmethod
    def author_get(self):
        raise NotImplementedError()

    @abc.abstractmethod
    def author_set(self, author):
        raise NotImplementedError()

    @abc.abstractmethod
    def date_get(self):
        raise NotImplementedError()

    @abc.abstractmethod
    def date_set(self, date):
        raise NotImplementedError()

    @abc.abstractmethod
    def save(self, destination):
        raise NotImplementedError()

    @abc.abstractmethod
    def load(self, source):
        raise NotImplementedError()

    def to_dict(self):
        root = {"author": self.author_get(), "date": self.date_get(),
                "terms": {"default": []}}

        def convert_value(val):
            if val.unit is not None or val.uncertainty is not None:
                return str(val)
            else:
                return val.value

        def convert_section(uuid):
            sec = {"uuid": uuid, "type": self.metadata.section_get_type(uuid)}
            label = self.metadata.section_get_label(uuid)
            if label is not None:
                sec["label"] = label
            reference = self.metadata.section_get_reference(uuid)
            if reference is not None:
                sec["reference"] = reference
            properties = self.metadata.section_get_properties(uuid)
            for p in properties:
                if self.metadata.property_has_value(uuid, p):
                    sec[p] = convert_value(self.metadata.property_get_value(uuid, p))
                elif self.metadata.property_has_sections(uuid, p):
                    child_uuids = self.metadata.property_get_sections(uuid, p)
                    if len(child_uuids) == 1:
                        sec[p] = convert_section(child_uuids[0])
                    else:
                        sec[p] = [convert_section(child_uuid) for child_uuid in child_uuids]
            return sec

        root["metadata"] = convert_section(self.metadata.root_get())
        return root

    def from_dict(self, data):
        if "author" in data:
            self.author_set(data["author"])
        if "date" in data:
            self.date_set(data["date"])

        def read_section(parent_uuid, parent_prop, sec):
            if parent_uuid is None:
                self.metadata.root_create(sec["type"], sec["uuid"], sec.get("label"), sec.get("reference"))
            else:
                self.metadata.property_add_section(parent_uuid, parent_prop, sec["type"], sec["uuid"],
                                                   sec.get("label"), sec.get("reference"))
            properties = ((k, v) for k, v in sec.items() if k not in ("type", "uuid", "label", "reference"))
            for prop, element in properties:
                if isinstance(element, dict):
                    read_section(sec["uuid"], prop, element)
                elif isinstance(element, list):
                    for sub_elem in element:
                        read_section(sec["uuid"], prop, sub_elem)
                else:
                    self.metadata.property_set_value(sec["uuid"], prop, odml2.value_from(element))

        read_section(None, None, data["metadata"])


class MetadataBackEnd(compat.ABC):

    @abc.abstractmethod
    def root_exists(self):
        raise NotImplementedError()

    @abc.abstractmethod
    def root_get(self):
        raise NotImplementedError()

    @abc.abstractmethod
    def root_create(self, typ, uuid=None, label=None, reference=None):
        raise NotImplementedError()

    @abc.abstractmethod
    def section_exists(self, uuid):
        raise NotImplementedError()

    @abc.abstractmethod
    def section_get_type(self, uuid):
        raise NotImplementedError()

    @abc.abstractmethod
    def section_set_type(self, uuid, typ):
        raise NotImplementedError()

    @abc.abstractmethod
    def section_get_label(self, uuid):
        raise NotImplementedError()

    @abc.abstractmethod
    def section_set_label(self, uuid, label):
        raise NotImplementedError()

    @abc.abstractmethod
    def section_get_reference(self, uuid):
        raise NotImplementedError()

    @abc.abstractmethod
    def section_set_reference(self, uuid, reference):
        raise NotImplementedError()

    @abc.abstractmethod
    def section_remove(self, uuid):
        raise NotImplementedError()

    @abc.abstractmethod
    def section_get_properties(self, uuid):
        raise NotImplementedError()

    @abc.abstractmethod
    def property_has_sections(self, parent_uuid, prop):
        raise NotImplementedError()

    @abc.abstractmethod
    def property_get_sections(self, parent_uuid, prop):
        raise NotImplementedError()

    @abc.abstractmethod
    def property_add_section(self, parent_uuid, prop, typ, uuid=None, label=None, reference=None):
        raise NotImplementedError()

    @abc.abstractmethod
    def property_has_value(self, parent_uuid, prop):
        raise NotImplementedError()

    @abc.abstractmethod
    def property_get_value(self, parent_uuid, prop):
        raise NotImplementedError()

    @abc.abstractmethod
    def property_set_value(self, parent_uuid, prop, value):
        raise NotImplementedError()

    @abc.abstractmethod
    def property_remove_value(self, parent_uuid, prop):
        raise NotImplementedError()

    @abc.abstractmethod
    def property_remove(self, parent_uuid, prop):
        raise NotImplementedError()


class TerminologyBeckEnd(compat.ABC):

    @abc.abstractmethod
    def namespace_get_all(self):
        raise NotImplementedError()

    @abc.abstractmethod
    def namespace_create(self, prefix, location=None):
        raise NotImplementedError()

    @abc.abstractmethod
    def namespace_remove(self, prefix):
        raise NotImplementedError()

    @abc.abstractmethod
    def namespace_get_location(self, prefix):
        raise NotImplementedError()

    @abc.abstractmethod
    def namespace_get_types(self, prefix):
        raise NotImplementedError()

    @abc.abstractmethod
    def type_create(self, typ, definition=None, properties=None):
        raise NotImplementedError()

    @abc.abstractmethod
    def type_exists(self, typ):
        raise NotImplementedError()

    @abc.abstractmethod
    def type_remove(self, typ):
        raise NotImplementedError()

    @abc.abstractmethod
    def type_get_definition(self, typ):
        raise NotImplementedError()

    @abc.abstractmethod
    def type_set_definition(self, typ, definition):
        raise NotImplementedError()

    @abc.abstractmethod
    def type_add_property(self, typ, prop):
        raise NotImplementedError()

    @abc.abstractmethod
    def type_remove_property(self, typ, prop):
        raise NotImplementedError()
