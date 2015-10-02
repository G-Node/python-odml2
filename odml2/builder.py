# coding=UTF-8

# Copyright (c) 2015, Adrian Stoewer (adrian.stoewer@rz.ifi.lmu.de)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the project.

__all__ = ("SB", )


class SB(object):
    """
    A section builder
    """

    def __init__(self, typ, uuid=None, label=None, references=None, **properties):
        raise NotImplementedError()

    def build(self, back_end, parent_uuid=None, prop=None):
        raise NotImplementedError()
