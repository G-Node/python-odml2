# coding=UTF-8

# Copyright (c) 2015, Adrian Stoewer (adrian.stoewer@rz.ifi.lmu.de)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the project.

import six
from future.utils import python_2_unicode_compatible

import re
import numbers
import collections
import datetime as dt
import odml2

__all__ = ("Section", "Value", "NameSpace", "PropertyDef", "TypeDef", "value_from")

PLUS_MINUS_UNICODE = u"±"
PLUS_MINUS = PLUS_MINUS_UNICODE if six.PY3 else "+-"
ALLOWED_VALUE_TYPES = (bool, numbers.Number, dt.date, dt.time, dt.datetime) + six.string_types
VALUE_EXPR = re.compile(u"^([-+]?(([0-9]+)|([0-9]*\.[0-9]+([eE][-+]?[0-9]+)?)))\s?" +
                        u"((\+-|\\xb1)(([0-9]+)|([0-9]*\.[0-9]+([eE][-+]?[0-9]+)?)))?\s?" +
                        u"([A-Za-zΩμ]{1,4})?$")


@python_2_unicode_compatible
class Section(object):
    """
    Represents an odML section entity.
    """

    def __init__(self, uuid, back_end, is_link=False):
        self.__is_link = is_link
        self.__uuid = uuid
        self.__back_end = back_end

    @property
    def uuid(self):
        return self.__uuid

    @property
    def type(self):
        return self.__back_end.sections[self.uuid].get_type()

    # noinspection PyShadowingBuiltins
    @type.setter
    def type(self, type):
        self.__back_end.sections[self.uuid].set_type(type)

    @property
    def label(self):
        return self.__back_end.sections[self.uuid].get_label()

    @label.setter
    def label(self, label):
        self.__back_end.sections[self.uuid].set_label(label)

    @property
    def reference(self):
        return self.__back_end.sections[self.uuid].get_reference()

    @reference.setter
    def reference(self, reference):
        self.__back_end.sections[self.uuid].set_reference(reference)

    @property
    def is_link(self):
        return self.__is_link

    #
    # dict like access to sections and values
    #

    def items(self):
        sec = self.__back_end.sections[self.uuid]
        for key in sec.value_properties:
            yield (key, self.get(key))
        for key in sec.section_properties:
            yield (key, self.get(key))

    def keys(self):
        sec = self.__back_end.sections[self.uuid]
        for key in sec.value_properties:
            yield key
        for key in sec.section_properties:
            yield key

    def get(self, key):
        sec = self.__back_end.sections[self.uuid]
        if key in sec.value_properties:
            return sec.value_properties[key]
        elif key in sec.section_properties:
            refs = sec.section_properties[key]
            return [Section(ref.uuid, self.__back_end, ref.is_link) for ref in refs]
        else:
            return None

    def __len__(self):
        sec = self.__back_end.sections[self.uuid]
        return len(sec.value_properties) + len(sec.section_properties)

    def __iter__(self):
        return self.keys()

    def __getitem__(self, key):
        element = self.get(key)
        if element is None:
            raise KeyError("Key '%s' not in section with uuid '%s'" % (key, self.uuid))
        elif isinstance(element, list) and len(element) == 1:
            element = element[0]
        elif isinstance(element, odml2.Value):
            element = element.value
        return element

    def __setitem__(self, key, element):
        if key in self:
            del self[key]
        if isinstance(element, list):
            for sub in element:
                if isinstance(sub, odml2.SB):
                    sub.build(self.__back_end, self.uuid, key)
                elif isinstance(sub, odml2.Section):
                    sub._copy(self.__back_end, self.uuid, key, True)
                else:
                    ValueError("Section builder expected but was %s" % type(sub))
        elif isinstance(element, odml2.SB):
            element.build(self.__back_end, self.uuid, key)
        elif isinstance(element, Section):
            element._copy(self.__back_end, self.uuid, key, True)
        else:
            val = value_from(element)
            sec = self.__back_end.sections[self.uuid]
            sec.value_properties[key] = val

    def __delitem__(self, key):
        sec = self.__back_end.sections[self.uuid]
        if key in sec.value_properties:
            del sec.value_properties[key]
        elif key in sec.section_properties:
            del sec.section_properties[key]
        else:
            raise KeyError("The section has no property with the name '%s'" % key)

    def __contains__(self, key):
        sec = self.__back_end.sections[self.uuid]
        return key in sec.value_properties or key in sec.section_properties

    #
    # built in methods
    #

    def __eq__(self, other):
        if isinstance(other, Section):
            return self.uuid == other.uuid
        else:
            return False

    def __ne__(self, other):
        return not (self == other)

    def __str__(self):
        return u"Section(type=%s, uuid=%s, label=%s)" % (self.type, self.uuid, self.label)

    #
    # Internally used methods
    #

    def _copy(self, back_end, parent_uuid=None, parent_prop=None, copy_subsections=True):
        if parent_uuid is None:
            back_end.create_root(self.type, self.uuid, self.label, self.reference)
        else:
            if parent_prop is None:
                raise ValueError("A property name is needed in order to append a sub section")
            back_end.sections.add(self.type, self.uuid, self.label, self.reference, parent_uuid, parent_prop)

        for p, thing in self.items():
            if isinstance(thing, (list, tuple)):
                for sub in thing:
                    if isinstance(sub, odml2.Section):
                        if copy_subsections:
                            sub._copy(back_end, self.uuid, p, copy_subsections)
            elif isinstance(thing, odml2.Section):
                if copy_subsections:
                    thing._copy(back_end, self.uuid, p, copy_subsections)
            elif isinstance(thing, odml2.Value):
                back_end.sections[self.uuid].value_properties.set(p, thing)
            else:
                # this should never happen
                raise ValueError("Section or Value expected, but type was '%s'" % type(thing))


class Value(object):
    """
    An odML Value class
    """

    def __init__(self, value, unit=None, uncertainty=None):
        if not isinstance(value, ALLOWED_VALUE_TYPES):
            raise ValueError("Value must be a one of the following types: %s" %
                             ", ".join(str(t) for t in ALLOWED_VALUE_TYPES))
        self.__value = value
        if unit is not None and not isinstance(unit, six.string_types):
            raise ValueError("Unit must be a string")
        if (unit is not None or uncertainty is not None) and not isinstance(value, numbers.Number):
            raise ValueError("Uncertainty and unit must be None if value is not a number")
        self.__unit = unit
        self.__uncertainty = float(uncertainty) if uncertainty is not None else None

    @property
    def value(self):
        return self.__value

    @property
    def unit(self):
        return self.__unit

    @property
    def uncertainty(self):
        return self.__uncertainty

    def copy(self, value=None, unit=None, uncertainty=None):
        return Value(
            value if value is not None else self.value,
            unit if unit is not None else self.unit,
            uncertainty if uncertainty is not None else self.uncertainty
        )

    @staticmethod
    def from_obj(thing, strict=False):
        pass

    def __lt__(self, other):
        return self.value < other.value

    def __eq__(self, other):
        if isinstance(other, Value):
            return self.value == other.value and self.unit == other.unit and self.uncertainty == other.uncertainty
        else:
            return False

    def __ne__(self, other):
        return not self == other

    @property
    def __value_str(self):
        if isinstance(self.value, (dt.date, dt.time, dt.datetime)):
            return self.value.isoformat()
        elif isinstance(self.value, six.string_types):
            return self.value
        else:
            return str(self.value)

    def __str__(self):
        parts = [self.__value_str]
        if self.uncertainty is not None:
            parts.append(PLUS_MINUS)
            parts.append(str(self.uncertainty))
        if self.unit is not None:
            parts.append(self.unit)
        return str().join(parts)

    def __unicode__(self):
        parts = [self.__value_str]
        if self.uncertainty is not None:
            parts.append(PLUS_MINUS_UNICODE)
            parts.append(str(self.uncertainty))
        if self.unit is not None:
            parts.append(self.unit)
        return u"".join(parts)


def value_from(thing):
    if isinstance(thing, six.string_types):
        match = VALUE_EXPR.match(thing)
        if match is None:
            return Value(thing)
        else:
            g = match.groups()
            num, is_float, uncertainty, unit = (g[0], g[3], g[7], g[11])
            num = float(num) if is_float is not None else int(num)
            uncertainty = float(uncertainty) if uncertainty is not None else None
            return Value(num, unit, uncertainty)
    if isinstance(thing, ALLOWED_VALUE_TYPES):
        return Value(thing)
    elif isinstance(thing, Value):
        return thing
    else:
        raise ValueError("Can't covert '%s' to a value" % repr(thing))


@python_2_unicode_compatible
class NameSpace(object):

    def __init__(self, prefix, uri):
        self.__prefix = prefix
        self.__uri = uri

    @property
    def prefix(self):
        return self.__prefix

    @property
    def uri(self):
        return self.__uri

    def copy(self, prefix=None, uri=None):
        return NameSpace(
            str(prefix) if prefix is not None else self.__prefix,
            str(uri) if uri is not None else self.__uri
        )

    @staticmethod
    def from_str(ns, strict=False):
        pass

    def __eq__(self, other):
        if not isinstance(other, NameSpace):
            return False
        return self.prefix == other.prefix and self.uri == other.uri

    def __ne__(self, other):
        return not self == other

    def __str__(self):
        return u"NameSpace(prefix=%s, uri=%s)" % (self.prefix, self.uri)


@python_2_unicode_compatible
class NameSpaceMap(collections.MutableMapping):

    def __init__(self, back_end):
        self.__back_end = back_end

    def set(self, prefix, uri):
        self[prefix] = NameSpace(prefix, uri)

    def __len__(self):
        return len(self.__back_end.namespaces)

    def __iter__(self):
        return iter(self.__back_end.namespaces)

    def __getitem__(self, prefix):
        ns = self.__back_end.namespaces[prefix]
        return NameSpace(ns.get_prefix(), ns.get_uri())

    def __delitem__(self, prefix):
        del self.__back_end.namespaces[prefix]

    def __setitem__(self, prefix, ns):
        if ns.prefix is not None and prefix != ns.prefix:
            raise ValueError("Non matching prefixes: %s != %s" % (prefix, ns.prefix))

        if prefix in self.__back_end.namespaces:
            self.__back_end.namespaces[prefix].set_uri(ns.uri)
        else:
            self.__back_end.namespaces.add(prefix, ns.uri)

    def __str__(self):
        return u"NameSpaceMap(size=%d)" % len(self)


@python_2_unicode_compatible
class TypeDef(object):

    def __init__(self, name, definition, properties):
        self.__name = name
        self.__definition = definition
        self.__properties = frozenset(properties)

    @property
    def name(self):
        return self.__name

    @property
    def definition(self):
        return self.__definition

    @property
    def properties(self):
        return self.__properties

    def copy(self, name=None, definition=None, properties=frozenset()):
        return TypeDef(
                str(name) if name is not None else self.__name,
                str(definition) if definition is not None else self.__definition,
                properties if properties != frozenset() else self.__properties
        )

    def __eq__(self, other):
        if not isinstance(other, TypeDef):
            return False
        return self.name == other.name

    def __ne__(self, other):
        return not self == other

    def __str__(self):
        return u"TypeDef(name=%s, properties=set(%s))" % (self.name, u", ".join(str(i) for i in self.properties))


@python_2_unicode_compatible
class TypeDefMap(collections.MutableMapping):

    def __init__(self, back_end):
        self.__back_end = back_end

    def __len__(self):
        return len(self.__back_end.type_defs)

    def __iter__(self):
        return iter(self.__back_end.type_defs)

    def __getitem__(self, name):
        td = self.__back_end.type_defs[name]
        return TypeDef(td.get_name(), td.get_definition(), td.get_properties())

    def __delitem__(self, name):
        del self.__back_end.type_defs[name]

    def __setitem__(self, name, td):
        if td.name is not None and name != td.name:
            raise ValueError("Non matching type names: %s != %s" % (name, td.name))

        if name in self.__back_end.type_defs:
            type_def = self.__back_end.type_defs[name]
            type_def.set_definition(td.definition)
            type_def.set_properties(td.properties)
        else:
            self.__back_end.type_defs.add(name, td.definition, td.properties)

    def __str__(self):
        return u"TypeDefMap(size=%d)" % len(self)


@python_2_unicode_compatible
class PropertyDef(object):

    def __init__(self, name, definition, types):
        self.__name = name
        self.__definition = definition
        self.__types = frozenset(types)

    @property
    def name(self):
        return self.__name

    @property
    def definition(self):
        return self.__definition

    @property
    def types(self):
        return self.__types

    def copy(self, name=None, definition=None, types=frozenset()):
        return PropertyDef(
                str(name) if name is not None else self.__name,
                str(definition) if definition is not None else self.__definition,
                types if types != frozenset() else self.__types
        )

    def __eq__(self, other):
        if not isinstance(other, PropertyDef):
            return False
        return self.name == other.name

    def __ne__(self, other):
        return not self == other

    def __str__(self):
        return u"PropertyDef(name=%s, types=set(%s))" % (self.name, u", ".join(str(i) for i in self.types))


@python_2_unicode_compatible
class PropertyDefMap(collections.MutableMapping):

    def __init__(self, back_end):
        self.__back_end = back_end

    def __len__(self):
        return len(self.__back_end.property_defs)

    def __iter__(self):
        return iter(self.__back_end.property_defs)

    def __getitem__(self, name):
        pd = self.__back_end.property_defs[name]
        return PropertyDef(pd.get_name(), pd.get_definition(), pd.get_types())

    def __delitem__(self, name):
        del self.__back_end.property_defs[name]

    def __setitem__(self, name, pd):
        if pd.name is not None and name != pd.name:
            raise ValueError("Non matching property names: %s != %s" % (name, pd.name))

        if name in self.__back_end.property_defs:
            prop_def = self.__back_end.property_defs[name]
            prop_def.set_definition(pd.definition)
            prop_def.set_types(pd.types)
        else:
            self.__back_end.property_defs.add(name, pd.definition, pd.types)

    def __str__(self):
        return u"PropertyDefMap(size=%d)" % len(self)
