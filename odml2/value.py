# coding=UTF-8

# Copyright (c) 2015, Adrian Stoewer (adrian.stoewer@rz.ifi.lmu.de)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the project.

__all__ = ("Value", )

import datetime as dt
import odml2.compat as compat

PLUS_MINUS_UNICODE = u"±"
PLUS_MINUS = PLUS_MINUS_UNICODE if compat.PY3 else "+-"


class Value(object):
    """
    An odML Value class
    """

    def __init__(self, value, unit=None, uncertainty=None):
        self.__value = value
        self.__unit = unit
        self.__uncertainty = uncertainty

    @property
    def value(self):
        return self.__value

    @property
    def unit(self):
        return self.__unit

    @property
    def uncertainty(self):
        return self.__uncertainty

    def using(self, value=None, unit=None, uncertainty=None):
        return Value(
            value if value is not None else self.value,
            unit if unit is not None else self.unit,
            uncertainty if uncertainty is not None else self.uncertainty
        )

    def __eq__(self, other):
        if isinstance(other, Value):
            return self.value == other.value and self.unit == other.unit and self.uncertainty == other.uncertainty
        else:
            return False

    @property
    def __value_str(self):
        if isinstance(self.value, (dt.date, dt.time, dt.datetime)):
            return self.value.isoformat()
        elif isinstance(self.value, (compat.unicode, str)):
            return self.value
        else:
            return str(self.value)

    def __str__(self):
        parts = [self.__value_str]
        if self.unit is not None:
            parts.append(self.unit)
        if self.uncertainty is not None:
            parts.append(PLUS_MINUS)
            parts.append(str(self.uncertainty))
        return str().join(parts)

    def __unicode__(self):
        parts = [self.__value_str]
        if self.unit is not None:
            parts.append(self.unit)
        if self.uncertainty is not None:
            parts.append(PLUS_MINUS_UNICODE)
            parts.append(str(self.uncertainty))
        return compat.unicode().join(parts)

    def __repr__(self):
        return str(self)
