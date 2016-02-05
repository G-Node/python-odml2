# coding=UTF-8

# Copyright (c) 2015, Adrian Stoewer (adrian.stoewer@rz.ifi.lmu.de)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the project.

import six
from future.utils import python_2_unicode_compatible

import odml2
from odml2.api import yml, base

__all__ = ("BACK_ENDS", "Document", "load_document", "save_document")

BACK_ENDS = (yml.YamlDocument, )


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
        return self.__back_end.is_attached()

    @property
    def is_writable(self):
        return self.__back_end.is_writable()

    @property
    def location(self):
        return self.__back_end.get_uri()

    @property
    def author(self):
        return self.__back_end.get_author()

    @author.setter
    def author(self, author):
        self.__back_end.set_author(author)

    @property
    def date(self):
        return self.__back_end.get_date()

    @date.setter
    def date(self, date):
        self.__back_end.set_date(date)

    @property
    def version(self):
        return self.__back_end.get_version()

    @version.setter
    def version(self, version):
        self.__back_end.set_version(version)

    @property
    def root(self):
        uuid = self.__back_end.get_root()
        if uuid is None:
            return None
        return odml2.Section(uuid, self.__back_end)

    @root.setter
    def root(self, thing):
        if isinstance(thing, odml2.SB):
            thing.build(self.__back_end)
        elif isinstance(thing, odml2.Section):
            # noinspection PyProtectedMember
            thing._copy(self.__back_end)
        else:
            raise ValueError("Only Section and SB can be used as root")

    @property
    def namespaces(self):
        return self.__namespaces

    @property
    def type_definitions(self):
        return self.__type_defs

    @property
    def property_definitions(self):
        return self.__property_defs

    def save(self, destination=None):
        self.__back_end.save(destination)

    def load(self, source):
        self.__back_end.load(source)

    def __str__(self):
        return u"Document(location='%s', author='%s', date=%s)" % (self.__back_end.get_uri(), self.author, self.date)

    def __repr__(self):
        return str(self)
