# coding=UTF-8

# Copyright (c) 2015, Adrian Stoewer (adrian.stoewer@rz.ifi.lmu.de)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the project.

"""
This module contains some sanity checks for certain inputs.
"""

import re

__all__ = ("is_name", "assert_name", "is_prefix", "assert_prefix", "is_prefixed_name", "assert_prefixed_name",
           "is_uuid", "assert_uuid", "is_prefixed_uuid", "assert_prefixed_uuid", "split_prefixed_name",
           "join_prefixed_name")

NAME_PART = "[\d\w\-_]{1,256}"
UUID_PART = "[0-9a-fA-F\-]{36}"
PREFIX_PART = "[\d\w\-_]{1,127}"

NAME_EXP = re.compile("^%s$" % NAME_PART)
PREFIX_EXP = re.compile("^%s$" % PREFIX_PART)
PREFIX_NAME_EXP = re.compile("^(%s:)?%s$" % (PREFIX_PART, NAME_PART))
UUID_EXP = re.compile("^%s$" % UUID_PART)
PREFIX_UUID_EXP = re.compile("^(%s:)?%s$" % (PREFIX_PART, UUID_PART))


def split_prefixed_name(name):
    parts = name.split(":", 1)
    if len(parts) == 1:
        return None, parts[0]
    else:
        return parts


def join_prefixed_name(prefix, name):
    return "%s:%s" % (prefix, name) if prefix is not None else name


def is_name(name):
    return NAME_EXP.match(name) is not None


def assert_name(name, msg="A name must only consist of alphanumeric characters and _ or -"):
    if not is_name(name):
        raise ValueError(msg)


def is_prefix(prefix):
    return PREFIX_EXP.match(prefix) is not None


def assert_prefix(prefix, msg="A prefix must only consist of alphanumeric characters and _ or -"):
    if not is_prefix(prefix):
        raise ValueError(msg)


def is_prefixed_name(name):
    return PREFIX_NAME_EXP.match(name) is not None


def assert_prefixed_name(name, msg="A prefixed name must contains only alphanumeric characters and _ or - \n" +
                                   "the optional prefix is separated by a ':' character"):
    if not is_prefixed_name(name):
        raise ValueError(msg)


def is_uuid(uuid):
    return UUID_EXP.match(uuid) is not None


def assert_uuid(uuid, msg="A uuid string must contain only the following characters: 0-9, A-F, a-f and '-'"):
    if not is_uuid(uuid):
        raise ValueError(msg)


def is_prefixed_uuid(uuid):
    return PREFIX_UUID_EXP.match(uuid) is not None


def assert_prefixed_uuid(uuid, msg="A uuid string must contain only the following characters: 0-9, A-F, a-f and '-' \n" +
                                   "the optional prefix is separated by a ':' character"):
    if not is_prefixed_uuid(uuid):
        raise ValueError(msg)
