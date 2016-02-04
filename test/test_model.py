# coding=UTF-8

# Copyright (c) 2015, Adrian Stoewer (adrian.stoewer@rz.ifi.lmu.de)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the project.

import six
import unittest
from uuid import uuid4

from odml2.api import yml
from odml2 import *


class TestSection(unittest.TestCase):

    def setUp(self):
        # populate a backend to provide a section with subsections
        id_1, id_11, id_111, id_112 = tuple(str(uuid4()) for _ in range(4))

        be = yml.YamlDocument()

        be.create_root("type", id_1, "root", "./example.dat")
        sec = be.sections[id_1]
        sec.value_properties.set("prop_foo", value_from("foo"))

        be.sections.add("type", id_11, None, None, id_1, "prop_11")
        be.sections.add("type", id_111, None, None, id_11, "prop_111")
        be.sections.add("type", id_112, None, None, id_11, "prop_112")
        self.sec_id = id_1
        self.sec = Section(id_1, be)

        # populate a back end to provide an empty section
        self.empty_id = str(uuid4())
        be = yml.YamlDocument()
        be.create_root("type", self.empty_id, "root", "./example.dat")
        self.empty = Section(self.empty_id, be)

    def test_uuid(self):
        self.assertEqual(self.empty.uuid, self.empty_id)

    def test_type(self):
        self.assertEqual(self.empty.type, "type")
        self.empty.type = "other_type"
        self.assertEqual(self.empty.type, "other_type")

    def test_label(self):
        self.assertEqual(self.empty.label, "root")
        self.empty.label = "other_label"
        self.assertEqual(self.empty.label, "other_label")

    def test_reference(self):
        self.assertEqual(self.empty.reference, "./example.dat")
        self.empty.reference = "./other.dat"
        self.assertEqual(self.empty.reference, "./other.dat")

    def test_items(self):
        for p, element in self.sec.items():
            self.assertIsInstance(p, str)
            if p == "prop_11":
                self.assertIsInstance(element, list)
                for s in element:
                    self.assertIsInstance(s, Section)
            elif p == "prop_foo":
                self.assertIsInstance(element, Value)

    def test_keys_iter_and_contains(self):
        for p in self.sec:
            self.assertIsInstance(p, str)
            self.assertTrue(p in self.sec)
        for p in self.sec.keys():
            self.assertIsInstance(p, str)
            self.assertTrue(p in self.sec)
        self.assertFalse("not_existing" in self.sec)

    def test_len(self):
        self.assertEqual(len(self.sec), 2)
        self.assertEqual(len(self.sec["prop_11"]), 2)

    def test_get_and_getitem(self):
        self.assertIsInstance(self.sec.get("prop_11"), list)
        self.assertIsInstance(self.sec["prop_11"], Section)
        self.assertIsInstance(self.sec.get("prop_foo"), Value)
        self.assertIsInstance(self.sec["prop_foo"], str)
        self.assertIsNone(self.sec.get("not_existing"))

        self.assertRaises(KeyError, lambda: self.sec["not_existing"])

    def test_setitem(self):
        self.assertEqual(len(self.empty), 0)
        self.empty["sec"] = SB("type")
        self.assertEqual(len(self.empty), 1)
        self.assertEqual(self.empty["sec"].type, "type")
        self.assertEqual(self.empty.get("sec")[0].type, "type")
        self.empty["prop"] = "some_str_value"
        self.assertEqual(len(self.empty), 2)
        self.assertEqual(self.empty["prop"], "some_str_value")
        self.assertEqual(self.empty.get("prop"), Value("some_str_value"))
        # TODO test setting of subsections

    def test_delitem(self):
        # TODO is flaky due to unsorted properties
        # self.assertEqual([p for p in self.sec], ["prop_11", "prop_foo"])
        del self.sec["prop_foo"]
        self.assertEqual([p for p in self.sec], ["prop_11"])
        del self.sec["prop_11"]
        self.assertEqual([p for p in self.sec], [])

    def test_eq(self):
        self.assertTrue(self.sec == self.sec)
        self.assertFalse(self.sec != self.sec)
        self.assertFalse(self.sec == self.empty)
        self.assertTrue(self.sec != self.empty)
        self.assertFalse(self.sec == "not_a_section")
        self.assertTrue(self.sec != "not_a_section")


class ValueTest(unittest.TestCase):

    def test_init(self):
        v1 = Value("hello")
        self.assertEqual(v1.value, "hello")
        self.assertIsNone(v1.unit)
        self.assertIsNone(v1.uncertainty)

        v2 = Value(100, "mV", 0.001)
        self.assertEqual(v2.value, 100)
        self.assertEqual(v2.unit, "mV")
        self.assertEqual(v2.uncertainty, 0.001)

    def test_set(self):
        v1 = Value(0)
        self.assertEqual(v1.value, 0)
        self.assertIsNone(v1.unit)
        self.assertIsNone(v1.uncertainty)

        v1 = v1.copy(value=100)
        self.assertEqual(v1.value, 100)
        self.assertIsNone(v1.unit)
        self.assertIsNone(v1.uncertainty)

        v1 = v1.copy(unit="mV")
        self.assertEqual(v1.value, 100)
        self.assertEqual(v1.unit, "mV")
        self.assertIsNone(v1.uncertainty)

        v1 = v1.copy(uncertainty=0.1)
        self.assertEqual(v1.value, 100)
        self.assertEqual(v1.unit, "mV")
        self.assertEqual(v1.uncertainty, 0.1)

    def test_value_from(self):
        v = value_from("foo")
        self.assertEqual(v.value, "foo")
        self.assertIsNone(v.unit)
        self.assertIsNone(v.uncertainty)
        v = value_from(u"µ")
        self.assertEqual(v.value, u"µ")
        self.assertIsNone(v.unit)
        self.assertIsNone(v.uncertainty)
        v = value_from(u"10±0.2e-2μΩ")
        self.assertEqual(v.value, 10)
        self.assertIsInstance(v.value, int)
        self.assertEqual(v.unit, u"μΩ")
        self.assertEqual(v.uncertainty, 0.002)
        v = value_from(u"10.2kmol")
        self.assertEqual(v.value, 10.2)
        self.assertIsInstance(v.value, float)
        self.assertEqual(v.unit, u"kmol")
        self.assertIsNone(v.uncertainty)

    def test_eq(self):
        self.assertEqual(Value("foo"), Value("foo"))
        self.assertEqual(Value(10, "mV"), Value(10.0, "mV"))
        self.assertEqual(Value(1, "ms", 0.11), Value(1, "ms", 0.11))

        self.assertNotEqual(Value("foo"), Value("bar"))
        self.assertNotEqual(Value(10, "mV"), Value(10.1, "mV"))
        self.assertNotEqual(Value(1, "ms", 0.11), Value(1, "ms", 0.0))

    def test_str(self):
        v1 = Value(1, "mV", 0.1)

        if six.PY2:
            self.assertEqual(str(v1), "1+-0.1mV")
            self.assertEqual(unicode(v1), u"1±0.1mV")
        else:
            self.assertEqual(str(v1), "1±0.1mV")


class NameSpaceTest(unittest.TestCase):

    def setUp(self):
        self.doc = Document()

    def test_copy_namespace(self):
        ns = NameSpace("ns", "uri")
        self.assertEqual(ns.prefix, "ns")
        self.assertEqual(ns.uri, "uri")

        ns = ns.copy(prefix="other_ns")
        self.assertEqual(ns.prefix, "other_ns")
        self.assertEqual(ns.uri, "uri")

        ns = ns.copy(uri="other_uri")
        self.assertEqual(ns.prefix, "other_ns")
        self.assertEqual(ns.uri, "other_uri")

        def assign_prefix():
            ns.prefix = "test"
        self.assertRaises(AttributeError, assign_prefix)

        def assign_uri():
            ns.uri = "test"
        self.assertRaises(AttributeError, assign_uri)

    def test_namespace_access(self):
        self.assertEqual(len(self.doc.namespaces), 0)
        self.assertFalse("ns" in self.doc.namespaces)

        self.doc.namespaces["ns"] = NameSpace("ns", "http://foo/bar")
        self.assertEqual(len(self.doc.namespaces), 1)
        self.assertTrue("ns" in self.doc.namespaces)
        ns = self.doc.namespaces["ns"]
        self.assertEqual(ns.prefix, "ns")
        self.assertEqual(ns.uri, "http://foo/bar")
        self.doc.namespaces["ns"] = ns.copy(uri="http://example.com")
        ns = self.doc.namespaces["ns"]
        self.assertEqual(ns.prefix, "ns")
        self.assertEqual(ns.uri, "http://example.com")

        del self.doc.namespaces["ns"]
        self.assertEqual(len(self.doc.namespaces), 0)
        self.assertFalse("ns" in self.doc.namespaces)


class TypeDefTest(unittest.TestCase):

    def setUp(self):
        self.doc = Document()

    def test_copy_type_def(self):
        td = TypeDef("TypeName", "some def", {"foo", "bar"})
        self.assertEqual(td.name, "TypeName")
        self.assertEqual(td.definition, "some def")
        self.assertEqual(td.properties, {"foo", "bar"})

        td = td.copy(name="OtherName")
        self.assertEqual(td.name, "OtherName")
        self.assertEqual(td.definition, "some def")
        self.assertEqual(td.properties, {"foo", "bar"})

        td = td.copy(definition="other def")
        self.assertEqual(td.name, "OtherName")
        self.assertEqual(td.definition, "other def")
        self.assertEqual(td.properties, {"foo", "bar"})

        td = td.copy(properties=td.properties - {"bar", })
        self.assertEqual(td.name, "OtherName")
        self.assertEqual(td.definition, "other def")
        self.assertEqual(td.properties, {"foo", })

    def test_type_def_access(self):
        self.assertEqual(len(self.doc.type_definitions), 0)
        self.assertFalse("SomeType" in self.doc.type_definitions)

        self.doc.type_definitions["SomeType"] = TypeDef("SomeType", "some definition", {"foo", "bar"})
        self.assertEqual(len(self.doc.type_definitions), 1)
        self.assertTrue("SomeType" in self.doc.type_definitions)
        td = self.doc.type_definitions["SomeType"]
        self.assertEqual(td.name, "SomeType")
        self.assertEqual(td.definition, "some definition")
        self.doc.type_definitions["SomeType"] = td.copy(definition="other definition")
        td = self.doc.type_definitions["SomeType"]
        self.assertEqual(td.name, "SomeType")
        self.assertEqual(td.definition, "other definition")

        del self.doc.type_definitions["SomeType"]
        self.assertEqual(len(self.doc.type_definitions), 0)
        self.assertFalse("SomeType" in self.doc.type_definitions)


class PropertyDefTest(unittest.TestCase):

    def setUp(self):
        self.doc = Document()

    def test_copy_property_def(self):
        pd = PropertyDef("prop_name", "some def", {"Foo", "Bar"})
        self.assertEqual(pd.name, "prop_name")
        self.assertEqual(pd.definition, "some def")
        self.assertEqual(pd.types, {"Foo", "Bar"})

        pd = pd.copy(name="other_name")
        self.assertEqual(pd.name, "other_name")
        self.assertEqual(pd.definition, "some def")
        self.assertEqual(pd.types, {"Foo", "Bar"})

        pd = pd.copy(definition="other def")
        self.assertEqual(pd.name, "other_name")
        self.assertEqual(pd.definition, "other def")
        self.assertEqual(pd.types, {"Foo", "Bar"})

        pd = pd.copy(types=pd.types - {"Bar", })
        self.assertEqual(pd.name, "other_name")
        self.assertEqual(pd.definition, "other def")
        self.assertEqual(pd.types, {"Foo", })

    def test_property_def_access(self):
        self.assertEqual(len(self.doc.property_definitions), 0)
        self.assertFalse("some_prop" in self.doc.property_definitions)

        self.doc.property_definitions["some_prop"] = PropertyDef("some_prop", "some definition", {"Foo", "Bar"})
        self.assertEqual(len(self.doc.property_definitions), 1)
        self.assertTrue("some_prop" in self.doc.property_definitions)
        pd = self.doc.property_definitions["some_prop"]
        self.assertEqual(pd.name, "some_prop")
        self.assertEqual(pd.definition, "some definition")
        self.doc.property_definitions["some_prop"] = pd.copy(definition="other definition")
        pd = self.doc.property_definitions["some_prop"]
        self.assertEqual(pd.name, "some_prop")
        self.assertEqual(pd.definition, "other definition")

        del self.doc.property_definitions["some_prop"]
        self.assertEqual(len(self.doc.property_definitions), 0)
        self.assertFalse("some_prop" in self.doc.property_definitions)
