# Copyright (c) 2014, Adrian Stoewer (adrian.stoewer@rz.ifi.lmu.de)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.

from __future__ import unicode_literals, absolute_import, division, print_function, generators

# use standard etree API for writing
from xml.etree.ElementTree import SubElement
from odml.types import Type, string_to_value, value_to_string


__all__ = ("xml_indent", "make_name", "elem_get_opt", "elem_get_strict", "elem_read_opt", "elem_read_strict",
           "elem_add_opt", "elem_add_strict", "attr_read_opt", "attr_read_strict")


# adopted from: http://effbot.org/zone/element-lib.htm#prettyprint
def xml_indent(element, level=0):
    """
    Nicely indents xml trees. Modifies the tree inplace.

    :param element: The element to indent.
    :type element:  xml.etree.Element
    :param level:   Current indention level.
    :type level:    int
    """
    i = "\n" + level * "  "
    if len(element):
        if not element.text or not element.text.strip():
            element.text = i + "  "
        if not element.tail or not element.tail.strip():
            element.tail = i
        for element in element:
            xml_indent(element, level+1)
        if not element.tail or not element.tail.strip():
            element.tail = i
    else:
        if level and (not element.tail or not element.tail.strip()):
            element.tail = i


def make_name(name, ns=None):
    """
    Make an element name (as used by lxml) from the name and the namespace.
    The result looks like this '{<namespace>}<name>'

    :param name:    The name of the element.
    :type name:     str
    :param ns:      The namespace of the element.
    :type ns:       str

    :return: The combined name as described above.
    :rtype:   str
    """
    return "{%s}%s" % (ns, name) if ns is not None else name


def elem_get_opt(element, name):
    """
    Get a single child element with a certain name from all children of an element.

    :param name:    The name of the element.
    :type name:     str

    :return:    The first child element or None if not found.
    """
    for child in element.iter(name):
        return child

    return None


def elem_get_strict(element, name):
    """
    Get a single child element with a certain name from all children of an element.

    :param name:    The name of the element.
    :type name:     str

    :return:    The first child element.
    """
    for child in element.iter(name):
        return child

    raise RuntimeError("Element '%s' does not exist!" % name)


def elem_read_opt(element, name, typ=Type.string):
    """
    Read the text content from an optional child element. If a type is specified
    the method will try to convert the content according to the provided type
    information.

    :param element: The element
    :type element:  xml.etree.Element
    :param name:    The name of the child element.
    :type name:     str
    :param typ:     Try to convert the element content to the specified odML type.
    :type typ:      Type

    :return:    The content of the element.
    """
    elem = elem_get_opt(element, name)
    val = elem.text if elem is not None else None

    if val is not None and typ != Type.string:
        return string_to_value(val, typ)
    else:
        return val


def elem_read_strict(element, name, typ=Type.string):
    """
    Read the text content from a mandatory child element. If a type is specified
    the method will try to convert the content according to the provided type
    information.

    :param element: The element
    :type element:  xml.etree.Element
    :param name:    The name of the child element.
    :type name:     str
    :param typ:     Try to convert the element content to the specified odML type.
    :type typ:      Type

    :return:    The content of the element.
    :throws:    RuntimeError if the child element doesn't exist.
    """
    elem = elem_get_strict(element, name)
    val = elem.text

    if val is None:
        raise RuntimeError("Element '%s' is empty!" % name)

    if typ == Type.string:
        return val
    else:
        return string_to_value(val, typ)


def attr_read_opt(element, name, typ=Type.string):
    """
    Read the text value from an optional attribute. If a type is specified
    the method will try to convert the value according to the provided type
    information.

    :param element: The element from where to read the attribute.
    :type element:  xml.etree.Element
    :param name:    The name of the attribute.
    :type name:     str
    :param typ:     Try to convert the attribute value to the specified odML type.
    :type typ:      Type

    :return:    The value of the attribute.
    """
    attr = None

    if name in element.attrib:
        attr = element.attrib[name]

    if attr is not None and typ != Type.string:
        return string_to_value(attr, typ)
    else:
        return attr


def attr_read_strict(element, name, typ=Type.string):
    """
    Read the text value from a mandatory attribute. If a type is specified
    the method will try to convert the value according to the provided type
    information.


    :param element: The element from where to read the attribute
    :type element:  xml.etree.Element
    :param name:    The name of the attribute.
    :type name:     str
    :param typ:     Try to convert the attribute value to the specified odML type.
    :type typ:      Type

    :return:    The content of the attribute.
    :throws:    RuntimeError if the attribute doesn't exist.
    """
    if name not in element.attrib:
        raise RuntimeError("Attribute '%s' does not exist!" % name)

    attr = element.attrib[name]

    if attr is None:
        raise RuntimeError("Attribute '%s' is empty!" % name)

    if typ == Type.string:
        return attr
    else:
        return string_to_value(attr, typ)


def elem_add_opt(element, name, val, typ=Type.string):
    """
    Add a sub element to the element passed as first argument and set the
    element text to the given value. If the value is not a string a type must
    be provided as last argument in order to convert the value to a string.

    If the value is None or an empty string the element will not be added.

    :param element: The parent element.
    :type element:  xml.etree.Element
    :param name:    The tag name of the child element to add.
    :type name:     str
    :param val:     The value of the child elements body.
    :type val:      int|float|bool|str|date|time|datetime|bytes
    :param typ:     The type of the given value (default odml.types.Type.string)
    :type typ:      odml.types.Type
    """
    if typ != Type.string:
        val = value_to_string(val, typ)

    if val:
        val = val.strip()
        child = SubElement(element, name)
        child.text = val


def elem_add_strict(element, name, val, typ=Type.string):
    """
    Add a sub element to the element passed as first argument and set the
    element text to the given value. If the value is not a string a type must
    be provided as last argument in order to convert the value to a string.

    If the value is None or an empty string an exception will be thrown.

    :param element: The parent element.
    :type element:  xml.etree.Element
    :param name:    The tag name of the child element to add.
    :type name:     str
    :param val:     The value of the child elements body.
    :type val:      int|float|bool|str|date|time|datetime|bytes
    :param typ:     The type of the given value (default odml.types.Type.string)
    :type typ:      odml.types.Type

    :throws:    RuntimeError if the value is None or an empty string.
    """
    if typ == Type.string:
        val = val.strip()

    if not val:
        raise RuntimeError("Element '%s' is empty!" % name)

    elem_add_opt(element, name, val, typ)
