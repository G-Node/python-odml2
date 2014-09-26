# Copyright (c) 2014, Adrian Stoewer (adrian.stoewer@rz.ifi.lmu.de)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.

from __future__ import unicode_literals, absolute_import, division, print_function, generators

from abc import abstractproperty


class WithStrictMode(object):

    def __init__(self, strict_mode=False):
        self.__strict_mode = bool(strict_mode)

    @property
    def strict_mode(self):
        return self.__strict_mode

    @strict_mode.setter
    def strict_mode(self, strict_mode):
        self.__strict_mode = bool(strict_mode)


class WithSections(object):
    """
    Base class for entities that have child sections namely section
    and document.
    """

    def __init__(self, sections=None):
        if sections is None:
            self.__sections = []
        else:
            self.__sections = sections

    @abstractproperty
    def is_section(self):
        raise NotImplementedError

    @property
    def sections(self):
        return self.__sections

    @sections.setter
    def sections(self, sections):
        self.__sections = sections
