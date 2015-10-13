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
from odml2.back_end import yaml_io, base

BACK_ENDS = (yaml_io.YamlBackEnd, )


class Document(object):

    def __init__(self, back_end="yaml"):
        self.__location = None
        if compat.is_str(back_end):
            found = False
            for be in BACK_ENDS:
                if be.NAME == back_end:
                    found = True
                    self.__back_end = be()
                    break
            if not found:
                raise ValueError("No back-end found for '%s'" % back_end)
        elif isinstance(back_end, base.DocumentBackEnd):
            self.__back_end = back_end
        else:
            raise ValueError("Not a valid back-end %s" % type(back_end))

    @property
    def location(self):
        return self.__location

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
        if not self.__back_end.metadata.root_exists():
            return None
        else:
            return odml2.Section(self.__back_end.metadata.root_get(), self.__back_end)

    @root.setter
    def root(self, element):
        if isinstance(element, odml2.SB):
            element.build(self.__back_end)
        elif isinstance(element, odml2.Section):
            # TODO handle sections
            raise NotImplementedError()
        else:
            raise ValueError("Only Section and SB can be used as root")

    def save(self, destination=None):
        if destination is None:
            destination = self.__location
        self.__back_end.save(destination)

    def load(self, source):
        if compat.is_str(source):
            self.__location = source
        self.__back_end.load(source)

    def __str__(self):
        return "Document(location='%s', author='%s', date=%s)" % (self.__location, self.author, self.date)

    def __repr__(self):
        return str(self)

    def __unicode__(self):
        return compat.unicode(str(self))
