# Copyright (c) 2014, Adrian Stoewer (adrian.stoewer@rz.ifi.lmu.de)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.

from __future__ import unicode_literals, absolute_import, division, print_function, generators

from datetime import datetime as dt
from odml.base import WithSections, WithStrictMode
from odml.info import DEFAULT_REPOSITORY
from odml.types import Type, is_valid_type, is_valid_value, guess_odml_type


class Document(WithSections):

    def __init__(self, author=None, date=None, time=None, repository=DEFAULT_REPOSITORY, odml_version=2.0,
                 document_version=1.0, sections=None):

        super(Document, self).__init__(sections)

        self.__author = author
        if date is None and time is None:
            now = dt.now()
            self.__date = now.date()
            self.__time = now.time()
        else:
            self.__date = date
            self.__time = time
        self.__repository = repository
        self.__odml_version = odml_version
        self.__document_version = document_version

    def is_section(self):
        return False

    @property
    def author(self):
        return self.__author

    @author.setter
    def author(self, author):
        self.__author = author

    @property
    def date(self):
        return self.__date

    @date.setter
    def date(self, date):
        self.__date = date

    @property
    def time(self):
        return self.__time

    @time.setter
    def time(self, time):
        self.__time = time

    @property
    def repository(self):
        return self.__repository

    @repository.setter
    def repository(self, repository):
        self.__repository = repository

    @property
    def odml_version(self):
        return self.__odml_version

    @odml_version.setter
    def odml_version(self, odml_version):
        self.__odml_version = odml_version

    @property
    def document_version(self):
        return self.__document_version

    @document_version.setter
    def document_version(self, document_version):
        self.__document_version = document_version


class Section(WithSections):

    def __init__(self, name, typ, definition=None, link=None, repository=None, mapping=None,
                 sections=None, properties=None):

        super(Section, self).__init__(sections)

        self.__name = name
        self.__type = typ
        self.__definition = definition
        self.__link = link
        self.__repository = repository
        self.__mapping = mapping

        if properties is None:
            self.__properties = []
        else:
            self.__properties = properties

    def is_section(self):
        return True

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, name):
        assert(name is not None)
        self.__name = name

    @property
    def type(self):
        return self.__type

    @type.setter
    def type(self, typ):
        assert(typ is not None)
        self.__type = typ

    @property
    def definition(self):
        return self.__definition

    @definition.setter
    def definition(self, definition):
        self.__definition = definition

    @property
    def link(self):
        return self.__link

    @link.setter
    def link(self, link):
        self.__link = link

    @property
    def repository(self):
        return self.__repository

    @repository.setter
    def repository(self, repository):
        self.__repository = repository

    @property
    def mapping(self):
        return self.__mapping

    @mapping.setter
    def mapping(self, mapping):
        self.__mapping = mapping

    #
    # Access to the section properties
    #

    def append(self, prop):
        self.__properties.append(prop)

    def __len__(self):
        return len(self.__properties)

    def __iter__(self):
        for p in self.__properties:
            yield p

    def __getitem__(self, name):
        return self.__properties[name]

    def __setitem__(self, name, prop):
        self.__properties[name] = prop


class Property(object):

    def __init__(self, name, values=None, unit=None, definition=None, mapping=None):

        if values:
            self.__values = values
        else:
            self.__values = []

        self.__name = name
        self.__unit = unit
        self.__definition = definition
        self.__mapping = mapping

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, name):
        assert(name is not None)
        self.__name = name

    @property
    def unit(self):
        return self.__unit

    @unit.setter
    def unit(self, unit):
        self.__unit = unit

    @property
    def definition(self):
        return self.__definition

    @definition.setter
    def definition(self, definition):
        self.__definition = definition

    @property
    def mapping(self):
        return self.__mapping

    @mapping.setter
    def mapping(self, mapping):
        self.__mapping = mapping

    #
    # Access to the property values
    #

    def set(self, value):
        self.__values = value

    def get(self):
        if len(self.__values) > 0:
            return self.__values[0]
        else:
            return None

    def append(self, value):
        self.__values.append(value)

    def __len__(self):
        return len(self.__values)

    def __iter__(self):
        for p in self.__values:
            yield p

    def __getitem__(self, name):
        return self.__values[name]

    def __setitem__(self, name, prop):
        self.__values[name] = prop


class Value(WithStrictMode):

    def __init__(self, value, dtype=None, uncertainty=None, order=None, checksum=None, filename=None,
                 strict_mode=False):
        super(Value, self).__init__(strict_mode)

        if dtype is None:
            self.__dtype = guess_odml_type(value)
        else:
            self.__dtype = dtype

        self.__assert_matching_dtype(value=value)
        self.__value = value

        self.__uncertainty = float(uncertainty) if uncertainty is not None else None
        self.__order = int(order) if order is not None else None

        self.__assert_base64_type(checksum)
        self.__checksum = checksum

        self.__assert_base64_type(filename)
        self.__filename = filename

    def get(self):
        return self.__value

    def set(self, value):
        self.__assert_matching_dtype(value=value)
        self.__value = value

    @property
    def dtype(self):
        return self.__dtype

    @dtype.setter
    def dtype(self, dtype):
        self.__assert_matching_dtype(dtype=dtype)
        self.__dtype = dtype

    @property
    def order(self):
        return self.__order

    @order.setter
    def order(self, order):
        self.__order = float(order) if order is not None else None

    @property
    def uncertainty(self):
        return self.__uncertainty

    @uncertainty.setter
    def uncertainty(self, uncertainty):
        self.__uncertainty = float(uncertainty) if uncertainty is not None else None

    @property
    def checksum(self):
        return self.__checksum

    @checksum.setter
    def checksum(self, checksum):
        self.__assert_base64_type(checksum)
        self.__checksum = checksum

    @property
    def filename(self):
        return self.__filename

    @filename.setter
    def filename(self, filename):
        self.__assert_base64_type(filename)
        self.__filename = filename

    def __assert_base64_type(self, value):
        if self.strict_mode and value is not None and self.dtype != Type.base64:
            msg = "This value is only valid if type is Type.base64, but type was %s"
            raise ValueError(msg % self.dtype)

    def __assert_matching_dtype(self, value=None, dtype=None):
        if self.strict_mode:

            if value is None:
                value = self.get()
            if dtype is None:
                dtype = self.dtype

            if dtype is not None:
                if not is_valid_type(dtype):
                    msg = "The given dtype is not valid: %s"
                    raise ValueError(msg % str(dtype))
                if value is not None and not is_valid_value(value, dtype):
                    msg = "The value '%s' does not match the dtype %s"
                    raise ValueError(msg % (str(value), str(dtype)))