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

import odml2
from odml2.back_end.yaml import YamlBackEnd

class DocumentTest(unittest.TestCase):

    def setUp(self):
        self.root_uuid = str(uuid4())
        self.back_end = YamlBackEnd()
        self.back_end.root_create("Experiment", self.root_uuid, "Experiment 01", "./example.dat")
        self.doc = odml2.Document("example.yml", self.back_end)
        other_be = YamlBackEnd()
        other_be.root_create("OtherType")
        self.other = odml2.Document("other.yml", other_be)

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
        self.assertIsInstance(root, odml2.Section)
        self.assertEqual(root.uuid, self.root_uuid)

    def test_set_root(self):
        def add_root():
            self.doc.root = self.other.root
        self.assertRaises(NotImplementedError, add_root)

    def test_load_document(self):
        pass

    def test_save_document(self):
        pass