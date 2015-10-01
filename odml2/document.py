# coding=UTF-8

# Copyright (c) 2015, Adrian Stoewer (adrian.stoewer@rz.ifi.lmu.de)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the project.

__all__ = ("Document", "load_document", "save_document")

from odml2.back_end.yaml import YamlBackEnd


class Document(object):

    def __init__(self, location, back_end):
        self.__location = location
        self.__back_end = back_end

    @property
    def author(self):
        raise NotImplemented()

    @property
    def date(self):
        raise NotImplemented()

    @property
    def root(self):
        raise NotImplemented()

    @root.setter
    def root(self):
        raise NotImplemented()


def load_document(location):
    return Document(YamlBackEnd(), location)


def save_document(document, location=None):
    raise NotImplemented()
