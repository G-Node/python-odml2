# coding=UTF-8

# Copyright (c) 2015, Adrian Stoewer (adrian.stoewer@rz.ifi.lmu.de)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the project.

import io
import os
import six
import enum
import requests

# noinspection PyUnresolvedReferences
from six.moves import StringIO
# noinspection PyUnresolvedReferences
from six.moves.urllib.parse import urlparse

import datetime as dt
from future.utils import python_2_unicode_compatible

import odml2
from odml2.api import yml, base

__all__ = ("BACK_ENDS", "Document", "TerminologyMode")

BACK_ENDS = (yml.YamlDocument, )


class TerminologyMode(enum.Enum):
    Ignore = 0,
    Create = 1,
    Loose = 2,
    Strict = 3


@python_2_unicode_compatible
class Document(object):

    def __init__(self, back_end="yaml"):
        if isinstance(back_end, six.string_types):
            found = False
            for be in BACK_ENDS:
                if be.NAME == back_end:
                    found = True
                    self.__back_end = be()
                    break
            if not found:
                raise ValueError("No back-end found for '%s'" % back_end)
        elif isinstance(back_end, base.BaseDocument):
            self.__back_end = back_end
        else:
            raise ValueError("Not a valid back-end %s" % type(back_end))

        self.__namespaces = odml2.NameSpaceMap(self.__back_end)
        self.__property_defs = odml2.PropertyDefMap(self.__back_end)
        self.__type_defs = odml2.TypeDefMap(self.__back_end)

    @property
    def is_attached(self):
        return self.back_end.is_attached()

    @property
    def is_writable(self):
        return self.back_end.is_writable()

    @property
    def location(self):
        return self.back_end.get_uri()

    @property
    def author(self):
        return self.back_end.get_author()

    @author.setter
    def author(self, author):
        if not isinstance(author, six.string_types):
            raise ValueError("Author must be a string")
        self.back_end.set_author(author)

    @property
    def date(self):
        return self.back_end.get_date()

    @date.setter
    def date(self, date):
        if not isinstance(date, dt.date):
            raise ValueError("Date must be a date or datetime")
        self.back_end.set_date(date)

    @property
    def version(self):
        return self.back_end.get_version()

    @version.setter
    def version(self, version):
        if not isinstance(version, int):
            raise ValueError("The document version must be an integer")
        self.back_end.set_version(version)

    @property
    def root(self):
        uuid = self.back_end.get_root()
        if uuid is None:
            return None
        return odml2.Section(uuid, self)

    @root.setter
    def root(self, thing):
        if isinstance(thing, odml2.SB):
            thing.build(self)
        elif isinstance(thing, odml2.Section):
            thing.copy_section(self)
        else:
            raise ValueError("Only Section and SB can be used as root")

    # noinspection PyShadowingBuiltins
    def create_root(self, type, uuid, label=None, reference=None):
        # TODO handle type
        self.back_end.create_root(type, uuid, label, reference)
        return odml2.Section(uuid, self)

    def find_section(self, uuid):
        if uuid not in self.back_end.sections:
            raise KeyError("Section with uuid '%s' does not exist" % uuid)
        return odml2.Section(uuid, self)

    def iter_sections(self):
        for uuid in self.back_end.sections:
            yield odml2.Section(uuid, self)

    @property
    def namespaces(self):
        return self.__namespaces

    @property
    def type_definitions(self):
        return self.__type_defs

    @property
    def property_definitions(self):
        return self.__property_defs

    @property
    def back_end(self):
        return self.__back_end

    def save(self, destination=None):
        if not hasattr(destination, "write"):
            parsed = urlparse(destination)
            if parsed.scheme == "file" or parsed.scheme == "":
                with io.open(destination, "w", encoding="utf-8") as f:
                    self.back_end.save(f, destination)
            else:
                raise RuntimeError("Unable to save to destination: %s" % destination)
        else:
            uri = destination.name if hasattr(destination, "name") else None
            self.back_end.save(destination, uri)

    def load(self, source, is_writable=True):
        if not hasattr(source, "read"):
            parsed = urlparse(source)
            if parsed.scheme == "file" or parsed.scheme == "":
                _, extension = os.path.splitext(source)
                back_end = self.__find_back_end(extension)(is_writable)
                with io.open(source, "r", encoding="utf-8") as f:
                    back_end.load(f, source)
                self.__set_back_end(back_end)
            elif parsed.scheme == "http":
                result = requests.get(source)
                mime_type = result.headers["content-type"].split(";")[0]
                back_end = self.__find_back_end(mime_type)(is_writable)
                back_end.load(StringIO(result.text), source)
                self.__set_back_end(back_end)
            else:
                raise RuntimeError("Unable to load from source: %s" % source)
        else:
            self.back_end.load(source)

    # noinspection PyMethodMayBeStatic
    def __find_back_end(self, hint):
        for be in BACK_ENDS:
            if hint == be.NAME or hint in be.FEXT or hint in be.MIME:
                return be
        raise ValueError("No suitable back-end fund for: %s" % hint)

    def __set_back_end(self, be):
        self.__back_end = be
        self.__namespaces = odml2.NameSpaceMap(self.__back_end)
        self.__property_defs = odml2.PropertyDefMap(self.__back_end)
        self.__type_defs = odml2.TypeDefMap(self.__back_end)

    def __str__(self):
        return u"Document(location='%s', author='%s', date=%s)" % (self.back_end.get_uri(), self.author, self.date)

    def __repr__(self):
        return str(self)
