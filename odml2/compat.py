# coding=UTF-8

# Copyright (c) 2015, Adrian Stoewer (adrian.stoewer@rz.ifi.lmu.de)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the project.

"""
Some utilities for python 2 and 3 compliant code
"""

import sys
import abc

__all__ = ("PY2", "PY3", "ABC", "unicode", "is_str")

PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3

if PY2:
    class ABC(object):
        __metaclass__ = abc.ABCMeta
else:
    from abc import ABC

if PY2:
    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    unicode = unicode
else:
    unicode = str


def is_str(string):
    if PY2:
        # noinspection PyUnresolvedReferences
        return isinstance(string, basestring)
    else:
        return isinstance(string, str)
