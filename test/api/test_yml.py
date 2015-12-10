# coding=UTF-8

# Copyright (c) 2015, Adrian Stoewer (adrian.stoewer@rz.ifi.lmu.de)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the project.

import unittest
from uuid import uuid4
from datetime import datetime

from odml2 import Value
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
        self.assertIsNone(self.doc.get_version())
        self.doc.set_version(2)
        self.assertEqual(self.doc.get_version(), 2)

    def test_create_root(self):
        self.assertIsNone(self.doc.get_root())
        self.doc.create_root("Experiment", uuid4(), "First Experiment")
        self.assertEqual(len(self.doc.sections), 1)
        self.assertIsInstance(self.doc.get_root(), str)

    def test_to_fom_dict(self):
        self.doc.create_root("Experiment", uuid4(), "First Experiment")
        d = self.doc.to_dict()
        pass
