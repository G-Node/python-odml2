# Copyright (c) 2014, Adrian Stoewer (adrian.stoewer@rz.ifi.lmu.de)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.

from __future__ import unicode_literals, absolute_import, division, print_function, generators

from enum import Enum

# try to use lxml for parsing, if not installed use standard etree API
try:
    from lxml.etree import XMLSchema, XMLParser, parse
except ImportError:
    from xml.etree.ElementTree import parse
    XMLSchema = None
    XMLParser = None

# use standard etree API for writing
from xml.etree.ElementTree import ElementTree, Element, SubElement, register_namespace

from odml import Document, Section, Property, Value
from odml.types import Type, string_to_value, value_to_string
from odml.io.xmlutil import *

# some global constants
# TODO change schema and namespace location as soon as it is published in the web
ODML2_NAMESPACE = "http://www.g-node.org"
ODML2_SCHEMA = "odml/resources/odml-2.xsd"

# register namespaces (this is a global setting and needs to be called only once)
register_namespace("xsi", "http://www.w3.org/2001/XMLSchema-instance")


class Odml2(str, Enum):
    """
    Names in the odml namespace defined for use with the etree API
    """
    odml = make_name("odml", ODML2_NAMESPACE)
    section = make_name("section", ODML2_NAMESPACE)
    sections = make_name("sections", ODML2_NAMESPACE)
    property = make_name("property", ODML2_NAMESPACE)
    properties = make_name("properties", ODML2_NAMESPACE)
    values = make_name("values", ODML2_NAMESPACE)

    author = make_name("author", ODML2_NAMESPACE)
    date = make_name("date", ODML2_NAMESPACE)
    time = make_name("time", ODML2_NAMESPACE)
    repository = make_name("repository", ODML2_NAMESPACE)
    version = make_name("version", ODML2_NAMESPACE)
    documentversion = make_name("documentversion", ODML2_NAMESPACE)

    name = make_name("name", ODML2_NAMESPACE)
    type = make_name("type", ODML2_NAMESPACE)
    definition = make_name("definition", ODML2_NAMESPACE)
    link = make_name("link", ODML2_NAMESPACE)
    mapping = make_name("mapping", ODML2_NAMESPACE)
    unit = make_name("unit", ODML2_NAMESPACE)

    order = make_name("order", ODML2_NAMESPACE)
    uncertainty = make_name("uncertainty", ODML2_NAMESPACE)
    checksum = make_name("checksum", ODML2_NAMESPACE)
    filename = make_name("filename", ODML2_NAMESPACE)

    def __str__(self):
        # lxml on python 2.x seems to need this method
        return self.value


# noinspection PyMethodMayBeStatic
class Odml2XmlReader(object):

    def __init__(self, validate=True, schema=ODML2_SCHEMA):
        """
        :param validate:    Whether or not the file should be validated (needs lxml to be installed)
        :type validate:     bool
        :param schema:      Path to the schema file (by default the shipped version is used)
        :type schema:       str
        """
        if validate and XMLSchema is not None:
            self.__parser = XMLParser(schema=XMLSchema(file=schema))
        else:
            self.__parser = None

    @property
    def parser(self):
        """
        The parser used by the reader or None if the default parser is used.
        """
        return self.__parser

    def read(self, filename):
        """
        Reads in and parses an odML file.

        :param filename:    The path to the file to parse.
        :type filename:     str

        :return:    The parsed document.
        :rtype:     odml.Document
        """
        if self.parser is not None:
            xml_doc = parse(filename, self.parser)
        else:
            xml_doc = parse(filename)
        root = xml_doc.getroot()

        return self.__read_document(root)

    def __read_document(self, element):
        return Document(
            author=elem_read_opt(element, Odml2.author),
            date=elem_read_opt(element, Odml2.date, Type.date),
            time=elem_read_opt(element, Odml2.time, Type.time),
            repository=elem_read_opt(element, Odml2.repository),
            odml_version=attr_read_strict(element, 'version', Type.double),
            document_version=elem_read_opt(element, Odml2.documentversion, Type.double),
            sections=self.__read_section_list(element)
        )

    def __read_section_list(self, element):
        sections = []
        node_elem = elem_get_opt(element, Odml2.sections)

        if node_elem is not None:
            for sec_elem in node_elem.iter(Odml2.section):
                sections.append(self.__read_section(sec_elem))

        return sections

    def __read_section(self, element):
        return Section(
            name=elem_read_strict(element, Odml2.name),
            typ=elem_read_strict(element, Odml2.type),
            definition=elem_read_opt(element, Odml2.definition),
            link=elem_read_opt(element, Odml2.link),
            repository=elem_read_opt(element, Odml2.repository),
            mapping=elem_read_opt(element, Odml2.mapping),
            sections=self.__read_section_list(element),
            properties=self.__read_property_list(element)
        )

    def __read_property_list(self, element):
        properties = []
        node_elem = elem_get_opt(element, Odml2.properties)

        if node_elem is not None:
            for prop_elem in node_elem.iter(Odml2.property):
                properties.append(self.__read_property(prop_elem))

        return properties

    def __read_property(self, element):
        return Property(
            name=elem_read_strict(element, Odml2.name),
            unit=elem_read_opt(element, Odml2.unit),
            definition=elem_read_opt(element, Odml2.definition),
            mapping=elem_read_opt(element, Odml2.mapping),
            values=self.__read_value_list(element)
        )

    def __read_value_list(self, element):
        values = []
        node_elem = elem_get_opt(element, Odml2.values)

        if node_elem is not None:
            for val_elem in node_elem:
                values.append(self.__read_value(val_elem))

        return values

    def __read_value(self, element):
        typ = element.tag
        typ = Type(typ[typ.find("}") + 1:])
        val = string_to_value(element.text, typ)

        return Value(
            value=val,
            dtype=typ,
            uncertainty=attr_read_opt(element, "uncertainty", Type.double),
            order=attr_read_strict(element, "order", Type.int),
            checksum=attr_read_opt(element, "checksum", Type.string),
            filename=attr_read_opt(element, "filename", Type.string)
        )


# noinspection PyMethodMayBeStatic
class Odml2XmlWriter(object):

    __ROOT_ATTRIB = {
        make_name("schemaLocation", "http://www.w3.org/2001/XMLSchema-instance"): "http://www.g-node.org odml-2.xsd",
        make_name("version", ODML2_NAMESPACE): "2.0"
    }

    def write(self, document, filename):
        root = self.__create_document(document)
        xml_indent(root)
        tree = ElementTree(root)
        tree.write(filename, encoding="utf-8", xml_declaration=True, default_namespace=ODML2_NAMESPACE)

    def __create_document(self, document):
        element = Element(Odml2.odml)
        for k, v in self.__ROOT_ATTRIB.items():
            element.set(k, v)

        elem_add_opt(element, Odml2.author, document.author)
        elem_add_opt(element, Odml2.date, document.date, Type.date)
        elem_add_opt(element, Odml2.time, document.time, Type.time)
        elem_add_opt(element, Odml2.repository, document.repository)
        elem_add_opt(element, Odml2.documentversion, document.document_version, Type.double)

        if len(document.sections) > 0:
            sections_elem = SubElement(element, Odml2.sections)
            for sec in document.sections:
                self.__add_section(sections_elem, sec)

        return element

    def __add_section(self, element, section):
        sec_elem = SubElement(element, Odml2.section)
        elem_add_strict(sec_elem, Odml2.name, section.name)
        elem_add_strict(sec_elem, Odml2.type, section.type)
        elem_add_opt(sec_elem, Odml2.definition, section.definition)
        elem_add_opt(sec_elem, Odml2.link, section.link)
        elem_add_opt(sec_elem, Odml2.repository, section.repository)
        elem_add_opt(sec_elem, Odml2.mapping, section.mapping)

        if len(section.sections) > 0:
            sections_elem = SubElement(sec_elem, Odml2.sections)
            for sec in section.sections:
                self.__add_section(sections_elem, sec)

        if len(section) > 0:
            properties_elem = SubElement(sec_elem, Odml2.properties)
            for prop in section:
                self.__add_property(properties_elem, prop)

    def __add_property(self, element, prop):
        prop_elem = SubElement(element, Odml2.property)
        elem_add_strict(prop_elem, Odml2.name, prop.name)
        elem_add_opt(prop_elem, Odml2.unit, prop.unit)
        elem_add_opt(prop_elem, Odml2.definition, prop.definition)
        elem_add_opt(prop_elem, Odml2.mapping, prop.mapping)

        if len(prop) > 0:
            values_elem = SubElement(prop_elem, Odml2.values)
            order = 0
            for value in prop:
                value.order = order
                order += 1
                self.__add_value(values_elem, value)

    def __add_value(self, element, value):
        dtype = value.dtype
        value_elem = SubElement(element, make_name(dtype.value, ODML2_NAMESPACE))
        value_elem.text = value_to_string(value.get(), dtype)
        value_elem.set(Odml2.order, value_to_string(value.order, Type.int))

        if value.uncertainty is not None:
            value_elem.set(Odml2.uncertainty, value_to_string(value.uncertainty, Type.double))

        if value.dtype == Type.base64:
            if value.checksum is not None:
                value_elem.set(Odml2.checksum, value.checksum)

            if value.filename is not None:
                value_elem.set(Odml2.filename, value.filename)


class Odml2Xml(Odml2XmlReader, Odml2XmlWriter):

    def __init__(self, validate=True, schema=ODML2_SCHEMA):
        """
        :param validate:    Whether or not the file should be validated (needs lxml to be installed)
        :type validate:     bool
        :param schema:      Path to the schema file (by default the shipped version is used)
        :type schema:       str
        """
        super(Odml2Xml, self).__init__(validate, schema)