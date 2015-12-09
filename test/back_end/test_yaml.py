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

from odml2 import Value
from odml2.back_end.yaml_io import YamlBackEnd


class YamlBackEndTest(unittest.TestCase):

    def setUp(self):
        self.empty = YamlBackEnd()

    def test_root(self):
        be = self.empty
        self.assertFalse(be.metadata.root_exists())
        be.metadata.root_create("Experiment", label="Experiment 01", reference="./example.dat")
        self.assertTrue(be.metadata.root_exists())
        root_id = be.metadata.root_get()
        self.assertTrue(be.metadata.section_exists(root_id))
        self.assertEqual(be.metadata.section_get_type(root_id), "Experiment")
        self.assertEqual(be.metadata.section_get_label(root_id), "Experiment 01")
        self.assertEqual(be.metadata.section_get_reference(root_id), "./example.dat")
        be.metadata.section_remove(root_id)
        self.assertFalse(be.metadata.section_exists(root_id))
        self.assertFalse(be.metadata.root_exists())

    def test_value(self):
        be = self.empty
        be.metadata.root_create("Experiment", label="Experiment 01", reference="./example.dat")
        root_id = be.metadata.root_get()
        be.metadata.property_set_value(root_id, "date", Value("2011-10-31"))
        self.assertListEqual(be.metadata.section_get_properties(root_id), ["date"])
        be.metadata.property_remove_value(root_id, "date")
        self.assertListEqual(be.metadata.section_get_properties(root_id), [])

    def test_subsections(self):
        ids = tuple(str(uuid4()) for _ in range(4))
        id_1, id_11, id_111, id_112 = ids
        be = self.empty
        be.metadata.root_create("type", id_1, "root")
        be.metadata.property_add_section(id_1, "prop_11", "type", id_11)
        be.metadata.property_add_section(id_11, "prop_111", "type", id_111)
        be.metadata.property_add_section(id_11, "prop_112", "type", id_112)
        for i in ids:
            self.assertTrue(be.metadata.section_exists(i))
        self.assertListEqual(be.metadata.section_get_properties(id_1), ["prop_11"])
        self.assertListEqual(be.metadata.section_get_properties(id_11), ["prop_111", "prop_112"])

        be.metadata.section_remove(id_11)
        self.assertTrue(be.metadata.section_exists(id_1))
        for i in ids[1:]:
            self.assertFalse(be.metadata.section_exists(i))