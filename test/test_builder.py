# coding=UTF-8

# Copyright (c) 2015, Adrian Stoewer (adrian.stoewer@rz.ifi.lmu.de)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the project.

import unittest
import datetime as dt
from uuid import uuid4

from odml2.api import yml
from odml2 import Document, Section, SB, Value, TerminologyStrategy


class TestSB(unittest.TestCase):

    def setUp(self):
        # populate a back end to provide an empty section
        self.sec_id = str(uuid4())
        be = yml.YamlDocument()
        be.create_root("type", self.sec_id, "root", "./example.dat")
        self.sec = Section(be.get_root(), Document(be))

        be = yml.YamlDocument()
        be.create_root("some_type", str(uuid4()), None, None)
        self.other = Section(be.get_root(), Document(be))

        # create an empty document
        self.doc = Document()

    def test_document_root(self):
        today = dt.date.today()
        self.doc.root = SB(
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
                    current="0.6 +-0.001 nA"
                ),
                SB(
                    type="PulseStimulus",
                    label="second pulse",
                    offset="30 ms",
                    duration="5ms",
                    current=Value(0.8, "nA", 0.001)
                )
            ]
        )
        self.assertIsInstance(self.doc.root, Section)
        root = self.doc.root
        self.assertEqual([p for p in root], ["date", "experimenter", "stimuli"])
        self.assertEqual(root["date"], today)
        self.assertEqual(root.get("date"), Value(today))

        exp = root["experimenter"]
        self.assertEqual(exp.type, "Person")
        self.assertEqual(exp["first_name"], "John")
        self.assertEqual(exp.get("first_name"), Value("John"))
        self.assertEqual(exp["last_name"], "Doe")
        self.assertEqual(exp.get("last_name"), Value("Doe"))

        stim01, stim02 = root["stimuli"]
        self.assertEqual(stim01.type, "PulseStimulus")
        self.assertEqual(stim01.label, "first pulse")
        self.assertEqual(stim01["offset"], 10)
        self.assertEqual(stim01.get("offset"), Value(10, "ms"))
        self.assertEqual(stim01["duration"], 5)
        self.assertEqual(stim01.get("duration"), Value(5, "ms"))
        self.assertEqual(stim01["current"], 0.6)
        self.assertEqual(stim01.get("current"), Value(0.6, "nA", 0.001))
        self.assertEqual(stim02.type, "PulseStimulus")
        self.assertEqual(stim02.label, "second pulse")
        self.assertEqual(stim02["offset"], 30)
        self.assertEqual(stim02.get("offset"), Value(30, "ms"))
        self.assertEqual(stim02["duration"], 5)
        self.assertEqual(stim02.get("duration"), Value(5, "ms"))
        self.assertEqual(stim02["current"], 0.8)
        self.assertEqual(stim02.get("current"), Value(0.8, "nA", 0.001))

    def test_subsection(self):
        today = dt.date.today()
        self.sec["test"] = SB(
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
                    current="0.6 +-0.001 nA"
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
        self.assertIsInstance(self.sec["test"], Section)
        section = self.sec["test"]
        self.assertEqual([p for p in section], ["date", "experimenter", "stimuli"])
        self.assertEqual(section["date"], today)
        self.assertEqual(section.get("date"), Value(today))

        exp = section["experimenter"]
        self.assertEqual(exp.type, "Person")
        self.assertEqual(exp["first_name"], "John")
        self.assertEqual(exp.get("first_name"), Value("John"))
        self.assertEqual(exp["last_name"], "Doe")
        self.assertEqual(exp.get("last_name"), Value("Doe"))

        stim01, stim02 = section["stimuli"]
        self.assertEqual(stim01.type, "PulseStimulus")
        self.assertEqual(stim01.label, "first pulse")
        self.assertEqual(stim01["offset"], 10)
        self.assertEqual(stim01.get("offset"), Value(10, "ms"))
        self.assertEqual(stim01["duration"], 5)
        self.assertEqual(stim01.get("duration"), Value(5, "ms"))
        self.assertEqual(stim01["current"], 0.6)
        self.assertEqual(stim01.get("current"), Value(0.6, "nA", 0.001))
        self.assertEqual(stim02.type, "PulseStimulus")
        self.assertEqual(stim02.label, "second pulse")
        self.assertEqual(stim02["offset"], 30)
        self.assertEqual(stim02.get("offset"), Value(30, "ms"))
        self.assertEqual(stim02["duration"], 5)
        self.assertEqual(stim02.get("duration"), Value(5, "ms"))
        self.assertEqual(stim02["current"], 0.8)
        self.assertEqual(stim02.get("current"), Value(0.8, "nA", 0.001))

    def test_properties(self):
        session = Document(strategy=TerminologyStrategy.Ignore)
        session.namespaces.set("terms", "terms.yml")

        session.root = SB(
                "terms:RecordingSession",
                **{
                    "terms:session_nr": 42,
                    "terms:recording_date": dt.date.today(),
                    "terms:subject": SB(
                            "terms:Animal",
                            **{
                                "terms:subject_id": 12,
                                "terms:date_of_birth": dt.date(2015, 11, 25),
                                "terms:species": "Mus musculus"
                            }
                    )
                }
        )
