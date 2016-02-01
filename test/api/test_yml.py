# coding=UTF-8

# Copyright (c) 2015, Adrian Stoewer (adrian.stoewer@rz.ifi.lmu.de)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the project.

import unittest
from datetime import datetime
from uuid import uuid4

from odml2 import Value
from odml2.api.base import BaseNameSpace, BasePropertyDefinition, BaseTypeDefinition, BaseSection
from odml2.api.yml import YamlDocument


class YamlDocumentTest(unittest.TestCase):

    def setUp(self):
        self.doc = YamlDocument()
        self.doc_ro = YamlDocument(is_writable=False)

    def test_is_attached(self):
        self.assertFalse(self.doc.is_attached())

    def test_is_writable(self):
        self.assertTrue(self.doc.is_writable())
        self.assertFalse(self.doc_ro.is_writable())
        # TODO check for errors when writing to a read only document

    def test_uri(self):
        self.assertIsNone(self.doc.get_uri())
        # TODO check if uri is set correctly when document is loaded or saved

    def test_author(self):
        self.assertIsNone(self.doc.get_author())
        self.doc.set_author("John Doe")
        self.assertEqual(self.doc.get_author(), "John Doe")

    def test_date(self):
        self.assertIsNone(self.doc.get_date())
        now = datetime.now()
        self.doc.set_date(now)
        self.assertEqual(self.doc.get_date(), now)

    def test_version(self):
        self.assertEqual(self.doc.get_version(), 1)
        self.doc.set_version(2)
        self.assertEqual(self.doc.get_version(), 2)

    def test_create_root(self):
        self.assertIsNone(self.doc.get_root())
        self.doc.create_root("Experiment", uuid4(), "First Experiment", None)
        self.assertEqual(len(self.doc.sections), 1)
        self.assertIsInstance(self.doc.get_root(), str)

    def test_namespace_access(self):
        self.assertEqual(len(self.doc.namespaces), 0)
        self.assertFalse("ex" in self.doc.namespaces)

        self.doc.namespaces.add("ex", "http://example.com/terms.yml")
        self.assertEqual(len(self.doc.namespaces), 1)
        self.assertTrue("ex" in self.doc.namespaces)

        del self.doc.namespaces["ex"]
        self.assertEqual(len(self.doc.namespaces), 0)
        self.assertFalse("ex" in self.doc.namespaces)

    def test_property_def_access(self):
        self.assertEqual((len(self.doc.property_defs)), 0)
        self.assertFalse("prop" in self.doc.property_defs)

        self.doc.property_defs.add("prop", "Some numerical property", ("int", "float"))
        self.assertEqual(len(self.doc.property_defs), 1)
        self.assertTrue("prop" in self.doc.property_defs)

        del self.doc.property_defs["prop"]
        self.assertEqual(len(self.doc.property_defs), 0)
        self.assertFalse("prop" in self.doc.property_defs)

    def test_type_def_access(self):
        self.assertEqual((len(self.doc.type_defs)), 0)
        self.assertFalse("SomeType" in self.doc.type_defs)

        self.doc.type_defs.add("SomeType", "Some section type", ("prop", ))
        self.assertEqual(len(self.doc.type_defs), 1)
        self.assertTrue("SomeType" in self.doc.type_defs)

        del self.doc.type_defs["SomeType"]
        self.assertEqual(len(self.doc.type_defs), 0)
        self.assertFalse("SomeType" in self.doc.type_defs)

    def test_section_access(self):
        id01 = str(uuid4())
        id02 = str(uuid4())
        self.assertEqual((len(self.doc.sections)), 0)
        self.assertFalse(id01 in self.doc.sections)
        self.assertFalse(id02 in self.doc.sections)

        self.doc.create_root("Experiment", id01, "experiment one", None)
        self.assertEqual((len(self.doc.sections)), 1)
        self.assertTrue(id01 in self.doc.sections)

        self.doc.sections.add("Session", id02, "session one", None, parent_uuid=id01, parent_prop="sessions")
        self.assertEqual((len(self.doc.sections)), 2)
        self.assertTrue(id02 in self.doc.sections)

        del self.doc.sections[id02]
        self.assertEqual((len(self.doc.sections)), 1)
        self.assertFalse(id02 in self.doc.sections)

    def test_to_fom_dict(self):
        # TODO test serialization
        pass


class YamlNameSpaceTest(unittest.TestCase):

    def setUp(self):
        self.doc = YamlDocument()
        self.doc.namespaces.add("ex", "http://example.com/terms.yml")
        self.doc.namespaces.add("gnode", "http://g-node.org/terms.yml")

    def test_get(self):
        ns = self.doc.namespaces["ex"]
        self.assertIsInstance(ns, BaseNameSpace)
        ns = self.doc.namespaces["gnode"]
        self.assertIsInstance(ns, BaseNameSpace)

        self.assertRaises(KeyError, lambda: self.doc.namespaces["not_exists"])
        self.assertIsNone(self.doc.namespaces.get("not_exists"))

    def test_prefix(self):
        ns = self.doc.namespaces["ex"]
        self.assertEqual(ns.get_prefix(), "ex")

    def test_uri(self):
        ns = self.doc.namespaces["ex"]
        self.assertEqual(ns.get_uri(), "http://example.com/terms.yml")
        ns.set_uri("http://other.com")
        self.assertEqual(ns.get_uri(), "http://other.com")
        # TODO check exception for malformed uri


class YamlPropertyDefinitionTest(unittest.TestCase):

    def setUp(self):
        self.doc = YamlDocument()
        self.doc.property_defs.add("int_prop", "Some integer", ("int", ))
        self.doc.property_defs.add("num_prop", "Some number", ("int", "float"))

    def test_get(self):
        prop = self.doc.property_defs["int_prop"]
        self.assertIsInstance(prop, BasePropertyDefinition)
        prop = self.doc.property_defs["num_prop"]
        self.assertIsInstance(prop, BasePropertyDefinition)

        self.assertRaises(KeyError, lambda: self.doc.property_defs["not_exists"])
        self.assertIsNone(self.doc.property_defs.get("not_exists"))

    def test_name(self):
        prop = self.doc.property_defs["int_prop"]
        self.assertEqual(prop.get_name(), "int_prop")

    def test_definition(self):
        prop = self.doc.property_defs["int_prop"]
        self.assertEqual(prop.get_definition(), "Some integer")
        prop.set_definition("Other definition")
        self.assertEqual(prop.get_definition(), "Other definition")

    def test_types(self):
        prop = self.doc.property_defs["num_prop"]
        self.assertEqual(prop.get_types(), ("int", "float"))
        prop.add_type("double")
        self.assertEqual(prop.get_types(), ("int", "float", "double"))
        prop.remove_type("float")
        self.assertEqual(prop.get_types(), ("int", "double"))


class YamlTypeDefinitionTest(unittest.TestCase):

    def setUp(self):
        self.doc = YamlDocument()
        self.doc.type_defs.add("SomeType", "Some section type", ("prop1", "prop2"))
        self.doc.type_defs.add("OtherType", "Another section type", ("prop3", ))

    def test_get(self):
        td = self.doc.type_defs["SomeType"]
        self.assertIsInstance(td, BaseTypeDefinition)
        td = self.doc.type_defs["OtherType"]
        self.assertIsInstance(td, BaseTypeDefinition)

        self.assertRaises(KeyError, lambda: self.doc.type_defs["NoType"])
        self.assertIsNone(self.doc.type_defs.get("NoType"))

    def test_name(self):
        td = self.doc.type_defs["SomeType"]
        self.assertEqual(td.get_name(), "SomeType")

    def test_definition(self):
        td = self.doc.type_defs["SomeType"]
        self.assertEqual(td.get_definition(), "Some section type")
        td.set_definition("Another definition")
        self.assertEqual(td.get_definition(), "Another definition")

    def test_properties(self):
        td = self.doc.type_defs["SomeType"]
        self.assertEqual(td.get_properties(), ("prop1", "prop2"))
        td.add_property("prop3")
        self.assertEqual(td.get_properties(), ("prop1", "prop2", "prop3"))
        td.remove_property("prop2")
        self.assertEqual(td.get_properties(), ("prop1", "prop3"))


class YamlSectionTest(unittest.TestCase):

    def setUp(self):
        self.doc = YamlDocument()
        self.id01 = str(uuid4())
        self.id02 = str(uuid4())
        self.doc.sections.add("Experiment", self.id01, "experiment one", None, None, None)
        self.doc.sections.add("Session", self.id02, "session one", None, parent_uuid=self.id01, parent_prop="sessions")

    def test_get(self):
        sec = self.doc.sections[self.id01]
        self.assertIsInstance(sec, BaseSection)
        sec = self.doc.sections[self.id02]
        self.assertIsInstance(sec, BaseSection)

        self.assertRaises(KeyError, lambda: self.doc.type_defs["not_exists"])
        self.assertIsNone(self.doc.type_defs.get("not_exists"))

    def test_uuid(self):
        sec = self.doc.sections[self.id02]
        self.assertEqual(sec.get_uuid(), self.id02)

    def test_type(self):
        sec = self.doc.sections[self.id02]
        self.assertEqual(sec.get_type(), "Session")
        sec.set_type("RecordingSession")
        self.assertEqual(sec.get_type(), "RecordingSession")

    def test_label(self):
        sec = self.doc.sections[self.id02]
        self.assertEqual(sec.get_label(), "session one")
        sec.set_label("other label")
        self.assertEqual(sec.get_label(), "other label")

    def test_reference(self):
        sec = self.doc.sections[self.id02]
        self.assertEqual(sec.get_reference(), None)
        sec.set_reference("some/path")
        self.assertEqual(sec.get_reference(), "some/path")

    def test_section_property_access(self):
        sec = self.doc.sections[self.id01]
        self.assertEqual(len(sec.section_properties), 1)
        self.assertTrue("sessions" in sec.section_properties)

        ref = sec.section_properties["sessions"][0]
        self.assertEqual(ref.uuid, self.id02)

        del self.doc.sections[self.id01]
        self.assertEqual(len(self.doc.sections), 0)
        self.assertIsNone(self.doc.get_root())

    def test_value_property_access(self):
        sec = self.doc.sections[self.id02]
        self.assertEqual(len(sec.value_properties), 0)
        self.assertFalse("duration" in sec.value_properties)

        sec.value_properties["duration"] = Value(1.0, "ms", 0.001)
        self.assertEqual(len(sec.value_properties), 1)
        self.assertTrue("duration" in sec.value_properties)
        val = sec.value_properties["duration"]
        self.assertEqual(val.value, 1.0)
        self.assertEqual(val.unit, "ms")
        self.assertEqual(val.uncertainty, 0.001)
        del sec.value_properties["duration"]

        self.assertEqual(len(sec.value_properties), 0)
        self.assertFalse("duration" in sec.value_properties)
        self.assertIsNone(sec.value_properties.get("duration"))
        self.assertRaises(KeyError, lambda: sec.value_properties["duration"])
