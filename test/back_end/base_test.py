# coding=UTF-8

# Copyright (c) 2015, Adrian Stoewer (adrian.stoewer@rz.ifi.lmu.de)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the project.

import nose
import unittest

from odml2.back_end.base import ValData, SecData


class SecDataTest(unittest.TestCase):

    def test_init(self):
        sec = SecData("some_type", "some_uuid", "some_label", "some_ref")
        self.assertEqual(sec.type, "some_type")
        self.assertEqual(sec.uuid, "some_uuid")
        self.assertEqual(sec.label, "some_label")
        self.assertEqual(sec.reference, "some_ref")

        sec = SecData(typ="some_type", label="some_label", reference="some_ref")
        self.assertEqual(sec.type, "some_type")
        self.assertEqual(len(sec.uuid), 36)
        self.assertEqual(sec.label, "some_label")
        self.assertEqual(sec.reference, "some_ref")

    def test_using(self):
        sec = SecData(typ="some_type", label="some_label", reference="some_ref")
        sec = sec.using(typ="other_type")
        self.assertEqual(sec.type, "other_type")
        self.assertEqual(sec.label, "some_label")
        self.assertEqual(sec.reference, "some_ref")
        sec = sec.using(label="other_label")
        self.assertEqual(sec.type, "other_type")
        self.assertEqual(sec.label, "other_label")
        self.assertEqual(sec.reference, "some_ref")
        sec = sec.using(reference="other_ref")
        self.assertEqual(sec.type, "other_type")
        self.assertEqual(sec.label, "other_label")
        self.assertEqual(sec.reference, "other_ref")


class ValDataTest(unittest.TestCase):

    def test_init(self):
        val = ValData(20, "mV", 0.1)
        self.assertEqual(val.value, 20)
        self.assertEqual(val.unit, "mV")
        self.assertEqual(val.uncertainty, 0.1)

    def test_using(self):
        val = ValData(0, "mV", 0)
        val = val.using(value=20)
        self.assertEqual(val.value, 20)
        self.assertEqual(val.unit, "mV")
        self.assertEqual(val.uncertainty, 0)
        val = val.using(unit="mA")
        self.assertEqual(val.value, 20)
        self.assertEqual(val.unit, "mA")
        self.assertEqual(val.uncertainty, 0)
        val = val.using(uncertainty=0.0001)
        self.assertEqual(val.value, 20)
        self.assertEqual(val.unit, "mA")
        self.assertEqual(val.uncertainty, 0.0001)

if __name__ == '__main__':
    nose.main()
