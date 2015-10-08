# coding=UTF-8

# Copyright (c) 2015, Adrian Stoewer (adrian.stoewer@rz.ifi.lmu.de)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the project.

import io
import unittest
import datetime as dt
from uuid import uuid4

from odml2 import Document, Section, SB, Value


class DocumentTest(unittest.TestCase):

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
        def add_root():
            self.doc.root = self.other.root
        self.assertRaises(NotImplementedError, add_root)

        self.doc.root = SB("SomeType")
        self.assertIsInstance(self.doc.root, Section)

    def test_load_save_document(self):
        today = dt.date.today()
        doc = Document()
        doc.author = "John Doe"
        doc.date = dt.date.today()
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
