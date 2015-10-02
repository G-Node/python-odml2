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
from odml2.back_end.yaml import YamlBackEnd


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
        return odml2.Section(self.__back_end.root_get(), self)

    @root.setter
    def root(self, element):
        if isinstance(element, odml2.SB):
            element.build(self.__back_end)
        if isinstance(element, odml2.Section):
            # TODO implement setting a section as subsection
            raise NotImplementedError()
        else:
            raise ValueError("Only Section and SB can be used as root")


def load_document(location):
    return Document(YamlBackEnd(), location)


def save_document(document, location=None):
    raise NotImplementedError()
