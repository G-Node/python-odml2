# coding=UTF-8

# Copyright (c) 2015, Adrian Stoewer (adrian.stoewer@rz.ifi.lmu.de)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the project.

__all__ = ("Document", "load_document", "save_document")

import odml2
from odml2 import compat

class Document(object):

    def __init__(self, location, back_end):
        self.__location = location
        self.__back_end = back_end

    @property
    def author(self):
        return self.__back_end.author_get()

    @author.setter
    def author(self, author):
        self.__back_end.author_set(author)

    @property
    def date(self):
        return self.__back_end.date_get()

    @date.setter
    def date(self, date):
        self.__back_end.date_set(date)

    @property
    def root(self):
        if not self.__back_end.root_exists():
            return None
        else:
            return odml2.Section(self.__back_end.root_get(), self.__back_end)

    @root.setter
    def root(self, element):
        if isinstance(element, odml2.SB):
            element.build(self.__back_end)
        elif isinstance(element, odml2.Section):
            # TODO handle sections
            raise NotImplementedError()
        else:
            raise ValueError("Only Section and SB can be used as root")

    def __str__(self):
        return "Document(location='%s', author='%s', date=%s)" % (self.__location, self.author, self.date)

    def __repr__(self):
        return str(self)

    def __unicode__(self):
        return compat.unicode(str(self))


def load_document(location):
    # TODO implement load_document
    # TODO can be a class method
    # return Document(YamlBackEnd(), location)
    raise NotImplementedError()


def save_document(document, location=None):
    # TODO implement save_document
    # TODO can be a method
    raise NotImplementedError()
