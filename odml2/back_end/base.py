# coding=UTF-8

# Copyright (c) 2015, Adrian Stoewer (adrian.stoewer@rz.ifi.lmu.de)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the project.

__all__ = ("BackEnd", )

import abc

import odml2
from odml2 import compat


class BackEnd(compat.ABC):
    """
    A base class for a back-end that represents data of an odML document and provides access to it.
    """

    @abc.abstractproperty
    def autosave(self):
        raise NotImplementedError()

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

    @abc.abstractmethod
    def save(self, destination):
        raise NotImplementedError()

    @abc.abstractmethod
    def load(self, source):
        raise NotImplementedError()

    @abc.abstractmethod
    def set_from(self, back_end):
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
            sec = {"uuid": uuid, "type": self.section_get_type(uuid)}
            label = self.section_get_label(uuid)
            if label is not None:
                sec["label"] = label
            reference = self.section_get_reference(uuid)
            if reference is not None:
                sec["reference"] = reference
            properties = self.section_get_properties(uuid)
            for p in properties:
                if self.property_has_value(uuid, p):
                    sec[p] = convert_value(self.property_get_value(uuid, p))
                elif self.property_has_sections(uuid, p):
                    child_uuids = self.property_get_sections(uuid, p)
                    if len(child_uuids) == 1:
                        sec[p] = convert_section(child_uuids[0])
                    else:
                        sec[p] = [convert_section(child_uuid) for child_uuid in child_uuids]
            return sec

        root["metadata"] = convert_section(self.root_get())
        return root

    def from_dict(self, data):
        if "author" in data:
            self.author_set(data["author"])
        if "date" in data:
            self.date_set(data["date"])

        def read_section(parent_uuid, parent_prop, sec):
            if parent_uuid is None:
                self.root_create(sec["type"], sec["uuid"], sec.get("label"), sec.get("reference"))
            else:
                self.property_add_section(parent_uuid, parent_prop, sec["type"], sec["uuid"],
                                              sec.get("label"), sec.get("reference"))
            properties = ((k, v) for k, v in sec.items() if k not in ("type", "uuid", "label", "reference"))
            for prop, element in properties:
                if isinstance(element, dict):
                    read_section(sec["uuid"], prop, element)
                elif isinstance(element, list):
                    for sub_elem in element:
                        read_section(sec["uuid"], prop, sub_elem)
                else:
                    self.property_set_value(sec["uuid"], prop, odml2.value_from(element))

        read_section(None, None, data["metadata"])
