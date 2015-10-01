# coding=UTF-8

# Copyright (c) 2015, Adrian Stoewer (adrian.stoewer@rz.ifi.lmu.de)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the project.

__all__ = ("BaseSection", "Section", "Value")

import abc
import datetime as dt
import odml2.compat as compat


PLUS_MINUS_UNICODE = u"±"
PLUS_MINUS = PLUS_MINUS_UNICODE if compat.PY3 else "+-"


class BaseSection(compat.ABC):

    @abc.abstractproperty
    def type(self):
        raise NotImplemented()

    @abc.abstractproperty
    def uuid(self):
        raise NotImplemented()

    @abc.abstractproperty
    def label(self):
        raise NotImplemented()

    @abc.abstractproperty
    def reference(self):
        raise NotImplemented()

    def __eq__(self, other):
        if isinstance(other, BaseSection):
            return self.uuid == other.uuid
        else:
            return False

    def __str__(self):
        return "%s(type=%s, uuid=%s, label=%s)" % (self.__class__.__name__, self.type, self.uuid, self.label)

    def __repr__(self):
        return str(self)

    def __unicode__(self):
        return compat.unicode(str(self))


class Section(BaseSection):
    """
    Represents an odML section entity.
    """

    def __init__(self, uuid, back_end):
        self.__uuid = uuid
        self.__back_end = back_end

    @property
    def uuid(self):
        return self.__uuid

    @property
    def type(self):
        raise NotImplemented()

    # noinspection PyMethodOverriding
    @type.setter
    def type(self, typ):
        raise NotImplemented()

    @property
    def label(self):
        raise NotImplemented()

    # noinspection PyMethodOverriding
    @label.setter
    def label(self, label):
        raise NotImplemented()

    @property
    def reference(self):
        raise NotImplemented()

    # noinspection PyMethodOverriding
    @reference.setter
    def reference(self, reference):
        raise NotImplemented()

    #
    # value and related section access
    #

    def __getitem__(self, item):
        pass

    def __setitem__(self, key, value):
        pass

    def __delitem__(self, key):
        pass


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
