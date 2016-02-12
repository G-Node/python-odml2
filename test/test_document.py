# coding=UTF-8

# Copyright (c) 2015, Adrian Stoewer (adrian.stoewer@rz.ifi.lmu.de)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the project.

import os
import io
import unittest
import datetime as dt
from uuid import uuid4

from odml2 import *


class TestDocument(unittest.TestCase):

    def setUp(self):
        self.root_uuid = str(uuid4())
        self.doc = Document()
        self.doc.root = SB("Experiment", self.root_uuid, "Experiment 01", "./example.dat")
        self.other = Document()
        self.other.root = SB("OtherType")

    def test_author(self):
        self.assertIsNone(self.doc.author)
        self.doc.author = "John Doe"
        self.assertEqual(self.doc.author, "John Doe")

    def test_date(self):
        d = dt.date.today()
        self.assertIsNone(self.doc.date)
        self.doc.date = d
        self.assertEqual(self.doc.date, d)

    def test_get_root(self):
        root = self.doc.root
        self.assertIsInstance(root, Section)
        self.assertEqual(root.uuid, self.root_uuid)

    def test_set_root(self):
        self.doc.root = SB("SomeType")
        self.assertIsInstance(self.doc.root, Section)

    def test_load_save_document(self):
        today = dt.date.today()
        doc = Document()
        doc.author = "John Doe"
        doc.date = dt.date.today()
        doc.type_definitions["Experiment"] = TypeDef("Experiment", properties=("date", ))
        root_builder = SB(
            type="RecordingSession",
            label="session one",
            date=today,
            experimenter=SB(
                type="Person",
                first_name="John",
                last_name="Doe",
                birthday=dt.date(1970, 11, 11)
            ),
            stimuli=[
                SB(
                    type="PulseStimulus",
                    label="first pulse",
                    offset="10ms",
                    duration=Value(5, "ms"),
                    current="0.6+-0.001nA"
                ),
                SB(
                    type="PulseStimulus",
                    label="second pulse",
                    offset="30ms",
                    duration="5ms",
                    current=Value(0.8, "nA", 0.001)
                )
            ]
        )
        doc.root = root_builder

        f1 = io.StringIO()
        doc.save(f1)
        yaml_str = f1.getvalue()
        f1.close()
        f1 = io.StringIO(yaml_str)
        doc = Document()
        doc.load(f1)
        f1.close()
        f1 = io.StringIO()
        doc.save(f1)
        self.assertEqual(yaml_str, f1.getvalue())
        f1.close()


class TestDocumentLinks(unittest.TestCase):

    def setUp(self):
        self.parent = Document()
        self.parent.root = SB(
                "Experiment",
                label="Experiment 01",
                subjects=[
                    SB("Subject", name="subject one"),
                    SB("Subject", name="subject two")
                ]
        )
        self.parent.save("parent.yml")

        self.doc = Document()
        self.doc.root = SB(
                "RecordingSession",
                label="session one",
                stimuli=[
                    SB("PulseStimulus", label="low pulse"),
                    SB("PulseStimulus", label="high pulse")
                ],
                trials=[
                    SB("Trial", label="trial 01"),
                    SB("Trial", label="trial 02")
                ]
        )

    def tearDown(self):
        os.remove("parent.yml")

    def test_in_document_links(self):
        s1 = self.doc.root["stimuli"][0]
        t1 = self.doc.root["trials"][0]

        self.assertFalse(s1.is_link)
        self.assertFalse("width" in s1)
        self.assertFalse("stimulus" in t1)

        t1["stimulus"] = s1

        self.assertTrue("stimulus" in t1)

        link = t1["stimulus"]
        self.assertEqual(s1.uuid, link.uuid)
        self.assertTrue(link.is_link)

        link["width"] = 1
        self.assertTrue("width" in s1)
        self.assertTrue("width" in link)

    def test_inter_document_copy(self):
        sub1 = self.parent.root["subjects"][0]
        t1 = self.doc.root["trials"][0]

        self.assertFalse("age" in sub1)
        self.assertFalse("subject" in t1)

        t1["subject"] = sub1
        self.assertTrue("subject" in t1)

        copy = t1["subject"]
        self.assertEqual(sub1.uuid, copy.uuid)
        self.assertFalse(copy.is_link)

        copy["age"] = 1
        self.assertFalse("age" in sub1)
        self.assertTrue("age" in copy)

    def test_inter_document_link(self):
        self.doc.namespaces.set("p", "parent.yml")

        sub1 = self.parent.root["subjects"][0]
        t1 = self.doc.root["trials"][0]

        self.assertFalse("age" in sub1)
        self.assertFalse("subject" in t1)

        t1["subject"] = sub1
        self.assertTrue("subject" in t1)

        link = t1["subject"]
        self.assertEqual(sub1.uuid, link.uuid)
        self.assertTrue(link.is_link)

        def set_age():
            link["age"] = 1
        self.assertRaises(RuntimeError, set_age)
