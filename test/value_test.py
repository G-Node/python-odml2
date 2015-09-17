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

import odml2.compat as compat
from odml2.value import Value


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

        v1 = v1.using(value=100)
        self.assertEqual(v1.value, 100)
        self.assertIsNone(v1.unit)
        self.assertIsNone(v1.uncertainty)

        v1 = v1.using(unit="mV")
        self.assertEqual(v1.value, 100)
        self.assertEqual(v1.unit, "mV")
        self.assertIsNone(v1.uncertainty)

        v1 = v1.using(uncertainty=0.1)
        self.assertEqual(v1.value, 100)
        self.assertEqual(v1.unit, "mV")
        self.assertEqual(v1.uncertainty, 0.1)

    def test_eq(self):
        self.assertEqual(Value("foo"), Value("foo"))
        self.assertEqual(Value(10, "mV"), Value(10.0, "mV"))
        self.assertEqual(Value(1, "ms", 0.11), Value(1, "ms", 0.11))

        self.assertNotEqual(Value("foo"), Value("bar"))
        self.assertNotEqual(Value(10, "mV"), Value(10.1, "mV"))
        self.assertNotEqual(Value(1, "ms", 0.11), Value(1, "ms", 0.0))

    def test_str(self):
        v1 = Value(1, "mV", 0.1)

        if compat.PY2:
            self.assertEqual(str(v1), "1mV+-0.1")
            self.assertEqual(compat.unicode(v1), u"1mV±0.1")
        else:
            self.assertEqual(str(v1), "1mV±0.1")

if __name__ == '__main__':
    nose.main()
