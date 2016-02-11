# coding=UTF-8

# Copyright (c) 2015, Adrian Stoewer (adrian.stoewer@rz.ifi.lmu.de)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the project.

import os
import unittest

from odml2 import *


class TestStrictStrategy(unittest.TestCase):

    def setUp(self):
        terms = Document()
        terms.type_definitions["Experiment"] = TypeDef("Experiment", properties=("date", ))
        terms.property_definitions["date"] = PropertyDef("date", types=("datetime", "date"))
        terms.save("terms.yml")
        self.terms = terms

        doc = Document()
        doc.namespaces.set("terms", "terms.yml")
        self.doc = doc
        self.doc.terminology_strategy = TerminologyStrategy.Strict

    def tearDown(self):
        os.remove("terms.yml")

    def test_handle_type(self):
        ts = self.doc.terminology_strategy

        try:
            ts.handle_type(self.doc, "terms:Experiment")
        except ValueError:
            self.assertTrue(False)

        self.assertRaises(ValueError, lambda: ts.handle_type(self.doc, "not_exist:Experiment"))
        self.assertRaises(ValueError, lambda: ts.handle_type(self.doc, "terms:NotExist"))
        self.assertRaises(ValueError, lambda: ts.handle_type(self.doc, "Experiment"))

    def test_handle_triple(self):
        ts = self.doc.terminology_strategy

        try:
            ts.handle_triple(self.doc, "terms:Experiment", "terms:date", "datetime")
            ts.handle_triple(self.doc, "terms:Experiment", "terms:date", "date")
        except ValueError:
            self.assertTrue(False)

        self.assertRaises(ValueError, lambda: ts.handle_triple(self.doc, "terms:Experiment", "terms:date", "float"))
        self.assertRaises(ValueError, lambda: ts.handle_triple(self.doc, "terms:Experiment", "date", "date"))
        self.assertRaises(ValueError, lambda: ts.handle_triple(self.doc, "terms:Experiment", "terms:foo", "date"))
        self.assertRaises(ValueError, lambda: ts.handle_triple(self.doc, "Experiment", "terms:date", "date"))
        self.assertRaises(ValueError, lambda: ts.handle_triple(self.doc, "terms:Bar", "terms:date", "date"))


class TestCreateStrategy(unittest.TestCase):

    def setUp(self):
        terms = Document()
        terms.type_definitions["Experiment"] = TypeDef("Experiment", properties=("date", ))
        terms.property_definitions["date"] = PropertyDef("date", types=("datetime", "date"))
        terms.save("terms.yml")
        self.terms = terms

        doc = Document()
        doc.namespaces.set("terms", "terms.yml")
        self.doc = doc
        self.doc.terminology_strategy = TerminologyStrategy.Create

    def test_handle_type(self):
        ts = self.doc.terminology_strategy

        ts.handle_type(self.doc, "terms:Experiment")
        self.assertEqual(len(self.doc.type_definitions), 0)

        self.assertRaises(ValueError, lambda: ts.handle_type(self.doc, "terms:Foo"))

        ts.handle_type(self.doc, "RecordingSession")
        self.assertTrue("RecordingSession" in self.doc.type_definitions)
        self.assertEqual(len(self.doc.type_definitions), 1)

    def test_handle_triple(self):
        ts = self.doc.terminology_strategy
        ts.handle_triple(self.doc, "terms:Experiment", "terms:date", "date")

        self.assertEqual(len(self.doc.type_definitions), 0)
        self.assertEqual(len(self.doc.property_definitions), 0)

        self.assertRaises(ValueError, lambda: ts.handle_triple(self.doc, "terms:Experiment", "terms:foo", "date"))
        self.assertRaises(ValueError, lambda: ts.handle_triple(self.doc, "terms:Bar", "terms:date", "date"))

        self.assertEqual(len(self.doc.type_definitions), 0)
        self.assertEqual(len(self.doc.property_definitions), 0)

        ts.handle_triple(self.doc, "RecordingSession", "experimenter", "string")
        self.assertEqual(len(self.doc.type_definitions), 1)
        self.assertTrue("RecordingSession" in self.doc.type_definitions)
        self.assertEqual(len(self.doc.property_definitions), 1)
        self.assertTrue("experimenter" in self.doc.property_definitions)
