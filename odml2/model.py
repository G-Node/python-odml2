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
import itertools
import collections
import datetime as dt

import odml2
from odml2.checks import *

__all__ = ("Section", "Value", "NameSpace", "PropertyDef", "TypeDef", "Value.from_obj")

PLUS_MINUS_UNICODE = u"±"
PLUS_MINUS = PLUS_MINUS_UNICODE if six.PY3 else "+-"
ALLOWED_VALUE_TYPES = (bool, numbers.Number, dt.date, dt.time, dt.datetime) + six.string_types
VALUE_TYPE_MAP = {bool: "bool", int: "int", numbers.Number: "float", dt.datetime: "datetime",
                  dt.time: "time", dt.date: "date", six.string_types: "string"}
VALUE_EXPR = re.compile(u"^([-+]?(([0-9]+)|([0-9]*\.[0-9]+([eE][-+]?[0-9]+)?)))\s?" +
                        u"((\+-|\\xb1)(([0-9]+)|([0-9]*\.[0-9]+([eE][-+]?[0-9]+)?)))?\s?" +
                        u"([A-Za-zΩμ]{1,4})?$")


@python_2_unicode_compatible
class Section(collections.MutableMapping):
    """
    *NOTICE*: Section initialization is usually done by the API
    """

    def __init__(self, uuid, document, is_link=False):
        self.__is_link = is_link
        self.__uuid = uuid
        self.__document = document

    @property
    def uuid(self):
        """
        The uuid of the section. This is a read only property.

        :type:      str
        """
        return self.__uuid

    @property
    def type(self):
        """
        The type of the section. The type names the kind of thing the section represents.

        :type:      str
        """
        return self.document.back_end.sections[self.uuid].get_type()

    # noinspection PyShadowingBuiltins
    @type.setter
    def type(self, type):
        # TODO handle type or remove
        assert_prefixed_name(type)
        self.document.back_end.sections[self.uuid].set_type(type)

    @property
    def label(self):
        """
        The label of the section. The label is an optional, human readable identifier of
        a section.

        :type:      str
        """
        return self.document.back_end.sections[self.uuid].get_label()

    @label.setter
    def label(self, label):
        if label is not None and not isinstance(label, six.string_types):
            raise ValueError("Label must be a string")
        self.document.back_end.sections[self.uuid].set_label(label)

    @property
    def reference(self):
        """
        An URI or path to other data related to this specific section.

        :type:      str
        """
        return self.document.back_end.sections[self.uuid].get_reference()

    @reference.setter
    def reference(self, reference):
        if reference is not None and not isinstance(reference, six.string_types):
            raise ValueError("Reference must be a string")
        self.document.back_end.sections[self.uuid].set_reference(reference)

    @property
    def is_link(self):
        """
        Whether or not the section is a link. Depending on the parent from which the section
        was accessed the same section can be a link or not a link.

        :type:      bool
        """
        return self.__is_link

    @property
    def document(self):
        """
        Reference to the document the section belongs to.

        :type:      :class:`~.Document`
        """
        return self.__document

    #
    # dict like access to sections and values
    #

    def get(self, key, default=None):
        """
        Access the target object of a certain property.

        If the property is a section property the result is a list of :class:`~.Section` objects.

        If the property is a value property the result is a single :class:`~.Value`.

        :param key:     The name of the accessed property.
        :type key:      str
        :param default: The default value if the property does not exist.

        :return:        A list of sections or a value
        """

        def mk_section(ref):
            if ref.namespace is None:
                doc = self.document
            else:
                doc = self.document.namespaces[ref.namespace].get_document()
            return Section(ref.uuid, doc, ref.is_link)

        sec = self.document.back_end.sections[self.uuid]
        if key in sec.value_properties:
            return sec.value_properties[key]
        elif key in sec.section_properties:
            refs = sec.section_properties[key]
            return [mk_section(ref) for ref in refs]
        else:
            return default

    def __getitem__(self, key):
        """
        Access the target of certain property.

        If the property is a section property with a single section the result is a
        :class:`~.Section` object for other section properties the result is a list of sections.

        If the property points to an odml :class:`~.Value` the result is the values
        :attr:`~.Value.value`.

        :param key:     The name of the accessed property.
        :type key:      str

        :return:        Depending of the target a single section, a list of sections or
                        the value of the targeted value object.
        """
        element = self.get(key)
        if element is None:
            raise KeyError("Key '%s' not in section with uuid '%s'" % (key, self.uuid))
        elif isinstance(element, list) and len(element) == 1:
            element = element[0]
        elif isinstance(element, odml2.Value):
            element = element.value
        return element

    def __setitem__(self, key, element):
        """
        Set the target for a certain property. The target element can be either a
        :class:`~.Section`, :class:`~.SB`, :class:`~.Value` or any allowed value
        type.

        If the element is a :class:`~.Section` the section is linked to this property if the
        parent if it already exists in the document. Otherwise the section is copied.

        If the element is a :class:`~.SB` object an analogous section will be created in
        the document.

        If the element is a :class:`~.Value` the value is used as target for the property. In
        all other cases a :class:`~.Value` object will be constructed from the element if this
        is supported for the elements type.

        :param key:         The name of the property.
        :type key:          str
        :param element:     The target element for the given property.
        :type element:      any
        """
        if key in self:
            del self[key]
        if isinstance(element, list):
            for sub in element:
                if isinstance(sub, odml2.SB):
                    sub.build(self.document, self.uuid, key)
                elif isinstance(sub, odml2.Section):
                    sub._copy_section(self.document, self.uuid, key)
                else:
                    ValueError("Section builder expected but was %s" % type(sub))
        elif isinstance(element, odml2.SB):
            element.build(self.document, self.uuid, key)
        elif isinstance(element, Section):
            element._copy_section(self.document, self.uuid, key)
        else:
            sec = self.document.back_end.sections[self.uuid]
            val = Value.from_obj(element)
            self.document.terminology_strategy.handle_triple(self.document, self.type, key, val.type)
            sec.value_properties[key] = Value.from_obj(element)

    def __delitem__(self, key):
        """
        Remove a property from the section. If the property is a section property the whole
        subtree of the document is removed.

        :param key:     The name of the property to remove.
        :type key:      str
        """
        sec = self.document.back_end.sections[self.uuid]
        if key in sec.value_properties:
            del sec.value_properties[key]
        elif key in sec.section_properties:
            del sec.section_properties[key]
        else:
            raise KeyError("The section has no property with the name '%s'" % key)

    def __len__(self):
        """
        The number of properties in the section.

        :rtype:         int
        """
        sec = self.document.back_end.sections[self.uuid]
        return len(sec.value_properties) + len(sec.section_properties)

    def __iter__(self):
        """
        Iterate over all targets of all properties of the section. Depending on the property
        the target is either a list of :class:`~.Section` objects or a :class:`~.Value`.

        :return:        A generator over all property targets
        """
        sec = self.document.back_end.sections[self.uuid]
        return itertools.chain(iter(sec.value_properties), iter(sec.section_properties))

    def items(self):
        """
        Iterate over all property, property target pairs of the section. Depending on the property
        the target is either a list of :class:`~.Section` objects or a :class:`~.Value`.

        :return:        A generator over all property, property target pairs
        """
        for key in self:
            yield (key, self.get(key))

    def values(self):
        """
        Iterate over all targets of all properties of the section. Depending on the property
        the target is either a list of :class:`~.Section` objects or a :class:`~.Value`.

        :return:        A generator over all property targets
        """
        for key in self:
            yield self.get(key)

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

    def __repr__(self):
        return str(self)

    #
    # Internally used methods
    #

    # noinspection PyShadowingBuiltins
    def _create_subsection(self, prop, type, uuid, label, reference):
        self.document.terminology_strategy.handle_triple(self.document, self.type, prop, type)
        self.document.back_end.sections.add(type, uuid, label, reference, self.uuid, prop)
        return Section(uuid, self.document)

    # noinspection PyShadowingBuiltins
    def _create_subsection_link(self, prop, type, uuid, prefix):
        self.document.terminology_strategy.handle_triple(self.document, self.type, prop, type)
        self.document.back_end.sections.add_link(uuid, prefix, self.uuid, prop)

    # noinspection PyProtectedMember
    def _copy_section(self, document, parent_uuid=None, parent_prop=None):
        if parent_uuid is None:
            section = document.create_root(self.type, self.uuid, self.label, self.reference)
            for p, thing in self.items():
                section[p] = thing
        else:
            if parent_prop is None:
                raise ValueError("A property name is needed in order to append a sub section")

            parent = document.find_section(parent_uuid)
            if parent is None:
                raise ValueError("Parent section with uuid '%s' does not exist" % parent_uuid)

            section, prefix = document.find_section_and_prefix(self.uuid, search_namespaces=True)
            if section is not None:
                parent._create_subsection_link(parent_prop, self.type, self.uuid, prefix)
            else:
                section = parent._create_subsection(parent_prop, self.type, self.uuid, self.label, self.reference)
                for p, thing in self.items():
                    section[p] = thing


class Value(object):
    """
    Create a new value.

    If the values value is not a :class:`numbers.Number` unit and
    uncertainty are expected to be None.

    :param value:           The actual value of the value :-)
    :type value:            bool | float | int | str | datetime | time
    :param unit:            The SI unit of the value.
    :type unit:             str
    :param uncertainty:     The uncertainty of the value.
    :type uncertainty:      float
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
        self.__type = None

    @property
    def value(self):
        """
        :type:      bool | float | int | str | datetime | time
        """
        return self.__value

    @property
    def unit(self):
        """
        :type:      str
        """
        return self.__unit

    @property
    def uncertainty(self):
        """
        :type:      float
        """
        return self.__uncertainty

    @property
    def type(self):
        """
        The name of the values data type.
        """
        if self.__type is None:
            for t, s in VALUE_TYPE_MAP.items():
                if isinstance(self.value, t):
                    self.__type = s
        return self.__type

    def copy(self, value=None, unit=None, uncertainty=None):
        """
        Since values should be treated as immutable objects, the :meth:`~.Value.copy` method
        can be used instead of setting the attributes of the value.

        Just assign a modified copy:

        .. code-block:: python

            v = Value(10, unit="V")
            v = v.copy(unit="mV")

        :param value:           The actual value of the value (optional)
        :type value:            bool | float | int | str | datetime | time
        :param unit:            The SI unit of the value (optional)
        :type unit:             str
        :param uncertainty:     The uncertainty of the value (optional)
        :type uncertainty:      float

        :return:    A (modified) copy of the value.
        """
        return Value(
            value if value is not None else self.value,
            unit if unit is not None else self.unit,
            uncertainty if uncertainty is not None else self.uncertainty
        )

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

    def __repr__(self):
        return str(self)

    @staticmethod
    def from_obj(thing):
        """
        Creates a value from all sorts of types of objects.

        If the value is a sting like '10 +-0.001 mV' it will be parsed to an equivalent of ``Value(10, 'mV', 0.001)``

        :param thing:   The object to create a value from.

        :return:        The created value object.
        :rtype:         :class:`~.Value`

        :raises:        ValueError if the object can't be converted to a value.
        """
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
    """
    Create a new namespace object.

    :param prefix:      The prefix used to reference the linked document.
    :type prefix:       str
    :param uri:         The URI or path to the linked document.
    :type uri:          str
    """

    def __init__(self, prefix, uri):
        assert_prefix(prefix)
        self.__prefix = prefix
        self.__uri = uri
        self.__doc = None

    @property
    def prefix(self):
        """
        The prefix used to reference the linked document.

        :type:      str
        """
        return self.__prefix

    @property
    def uri(self):
        """
        The uri to the linked document.

        :type:      str
        """
        return self.__uri

    def get_document(self):
        """
        Try to open the document the uri of the name space points to.

        :return:    The odML document the uri points to.
        :rtype:     :class:`~.Document`
        """
        if self.__doc is None:
            doc = odml2.Document()
            doc.load(self.uri, is_writable=False)
            self.__doc = doc
        return self.__doc

    def copy(self, prefix=None, uri=None):
        """
        Since instances of :class:`~.NameSpace` should be treated as immutable objects
        the :meth:`~.NameSpace.copy` method can be used as an alternative to change the
        objects attributes.

        Just reassign a modified copy:

        .. code-block:: python

            ns = doc.namespaces["gnode"]
            doc.namespaces["gnode"] = ns.copy(uri="gnode-terms.yml")

        :param prefix:      The prefix used to reference the linked document.
        :type prefix:       str
        :param uri:         The URI or path to the linked document.
        :type uri:          str

        :return:            A (modified) copy of the name space.
        """
        return NameSpace(
            str(prefix) if prefix is not None else self.__prefix,
            str(uri) if uri is not None else self.__uri
        )

    def __eq__(self, other):
        if not isinstance(other, NameSpace):
            return False
        return self.prefix == other.prefix and self.uri == other.uri

    def __ne__(self, other):
        return not self == other

    def __str__(self):
        return u"NameSpace(prefix=%s, uri=%s)" % (self.prefix, self.uri)

    def __repr__(self):
        return str(self)


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
        return self.__back_end.namespaces[prefix]

    def __delitem__(self, prefix):
        del self.__back_end.namespaces[prefix]

    def __setitem__(self, prefix, ns):
        self.__back_end.namespaces[prefix] = ns

    def __str__(self):
        return u"NameSpaceMap(size=%d)" % len(self)

    def __repr__(self):
        return str(self)


@python_2_unicode_compatible
class TypeDef(object):
    """
    Creates a new type definition.

    :param name:        The name of the type.
    :type name:         str
    :param definition:  The verbal definition of the type.
    :type definition:   str
    :param properties:  A set of property names.
    :type properties:   frozenset[str]
    """
    def __init__(self, name, definition=None, properties=frozenset()):
        assert_name(name)
        for p in properties:
            assert_name(p)
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

    def __repr__(self):
        return str(self)


@python_2_unicode_compatible
class TypeDefMap(collections.MutableMapping):

    def __init__(self, back_end):
        self.__back_end = back_end

    def set(self, name, definition=None, properties=frozenset()):
        self[name] = TypeDef(name, definition, properties)

    def __len__(self):
        return len(self.__back_end.type_defs)

    def __iter__(self):
        return iter(self.__back_end.type_defs)

    def __getitem__(self, name):
        return self.__back_end.type_defs[name]

    def __delitem__(self, name):
        del self.__back_end.type_defs[name]

    def __setitem__(self, name, td):
        self.__back_end.type_defs[name] = td

    def __str__(self):
        return u"TypeDefMap(size=%d)" % len(self)

    def __repr__(self):
        return str(self)


@python_2_unicode_compatible
class PropertyDef(object):
    """
    Crates a new property definition.

    :param name:        The name of the property.
    :type name:         str
    :param definition:  A verbal definition of the property.
    :type definition:   str
    :param types:       A set of type names (names of types that can be used as
                        target / 'rvalue') of the property.
    :type types:        frozenset[str]
    """

    def __init__(self, name, definition=None, types=frozenset()):
        assert_name(name)
        for t in types:
            assert_name(t)
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

    def __repr__(self):
        return str(self)


@python_2_unicode_compatible
class PropertyDefMap(collections.MutableMapping):

    def __init__(self, back_end):
        self.__back_end = back_end

    def set(self, name, definition=None, types=frozenset()):
        self[name] = PropertyDef(name, definition, types)

    def __len__(self):
        return len(self.__back_end.property_defs)

    def __iter__(self):
        return iter(self.__back_end.property_defs)

    def __getitem__(self, name):
        return self.__back_end.property_defs[name]

    def __delitem__(self, name):
        del self.__back_end.property_defs[name]

    def __setitem__(self, name, pd):
        self.__back_end.property_defs[name] = pd

    def __str__(self):
        return u"PropertyDefMap(size=%d)" % len(self)

    def __repr__(self):
        return str(self)
