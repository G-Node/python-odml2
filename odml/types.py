# Copyright (c) 2014, Adrian Stoewer (adrian.stoewer@rz.ifi.lmu.de)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.

from __future__ import unicode_literals, absolute_import, division, print_function, generators

from enum import Enum
from base64 import b64encode, b64decode
from datetime import datetime, date, time


__all__ = ('Type', 'guess_odml_type', 'is_valid_typename', 'is_valid_value', 'is_valid_string',
           'value_to_string', 'string_to_value')


class Type(str, Enum):
    """
    Enum that specifies a constant for every valid odML data type.
    """

    int = 'int'
    double = 'double'
    string = 'string'
    text = 'text'
    boolean = 'boolean'
    date = 'date'
    time = 'time'
    datetime = 'datetime'
    base64 = 'base64'


TYPE_NAMES = tuple(x.name for x in Type)

TYPE_MAP = {
    int: Type.int, float: Type.double, bool: Type.boolean,
    date: Type.date, time: Type.time, datetime: Type.datetime,
    str: Type.string, bytes: Type.string
}


def guess_odml_type(val):
    """
    Guess a odML type from a given value.

    :param val: The value to get the type from.
    :type val: int|float|bool|str|date|time|datetime|bytes

    :return: The odML type of the value. If the value can't be guessed the function will return None.
    :rtype: Type|None
    """
    for data_type, odml_type in TYPE_MAP.items():
        if type(val) == data_type:
            return odml_type

    for data_type, odml_type in TYPE_MAP.items():
        if isinstance(val, data_type):
            return odml_type

    return None


def is_valid_typename(typ):
    """
    Check if a string represents the name of a valid odML data type.

    :param typ: A sting that may be the name of an odML data type.
    :type typ: str

    :return: True if typ is a valid type False otherwise.
    :rtype: bool
    """
    return typ.lower() in TYPE_NAMES


def is_valid_value(val, typ):
    """
    Check if a given value matches the given odML type.

    :param val:
    :type val: int|float|bool|str|date|time|datetime|bytes
    :param typ:
    :type typ: Type

    :return: True if the type matches false otherwise.
    :rtype: bool
    """
    guessed = guess_odml_type(val)
    return guessed == typ


def is_valid_string(string, typ):
    """
    Check if a string value is a valid encoding of the respective data type.

    :param string: A string that encodes a value of a certain type.
    :type string: str|bytes
    :param typ: The type of the value.
    :type typ: Type

    :return: True if the value is valid, False otherwise.
    :rtype: bool
    """
    try:
        string_to_value(string, typ)
    except (ValueError, TypeError):
        return False

    return True


def value_to_string(val, typ):
    """
    Converts a value into a string according to the specified type
    information.

    :param val: The value that should be converted to a string.
    :type val: int|float|bool|str|date|time|datetime|bytes
    :param typ: The type of the value.
    :type typ: Type

    :return: The value encoded as string.
    :rtype: str
    """
    typ = typ.lower()
    if val is None:
        return None

    if typ in (Type.string, Type.text):
        result = val

    elif typ in (Type.int, Type.double, Type.boolean):
        result = str(val).lower()

    elif typ == Type.datetime:
        result = val.strftime('%Y-%m-%d %H:%M:%S')

    elif typ == Type.date:
        result = val.strftime('%Y-%m-%d')

    elif typ == Type.time:
        result = val.strftime('%H:%M:%S')

    elif typ == Type.base64:
        result = b64encode(val)

    else:
        raise RuntimeError('Unsupported type: %s' % typ)

    return result


def string_to_value(val, typ):
    """
    Convert a string into a native python type that represents the value according to
    the specified odML type information.

    :param val: The value string.
    :type val: str|bytes
    :param typ: The odML type of the value.
    :type typ: Type

    :return: The value as native python type
    :rtype: int|float|bool|str|date|time|datetime
    """
    typ = typ.lower()

    if typ in (Type.string, Type.text):
        result = val

    elif typ == Type.int:
        result = int(val)

    elif typ == Type.double:
        result = float(val)

    elif typ == Type.boolean:
        val = val.strip()
        if val in ('0', 'false'):
            result = False
        elif val in ('1', 'true'):
            result = True
        else:
            raise ValueError('Illegal value for a boolean: %s' % val)

    elif typ == Type.datetime:
        result = datetime.strptime(val, '%Y-%m-%d %H:%M:%S')

    elif typ == Type.date:
        result = datetime.strptime(val, '%Y-%m-%d').date()

    elif typ == Type.time:
        result = datetime.strptime(val, '%H:%M:%S').time()

    elif typ == Type.base64:
        result = b64decode(val)

    else:
        raise RuntimeError('Unsupported type: %s' % typ)

    return result