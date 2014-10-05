# Copyright (c) 2014, Adrian Stoewer (adrian.stoewer@rz.ifi.lmu.de)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.

import unittest
from datetime import datetime, date, time

from odml import Value, Type


class TestValue(unittest.TestCase):

    def setUp(self):
        self.v_int = Value(0)
        self.v_bool = Value(True)
        self.v_float = Value(0.0)
        self.v_str = Value("foo")
        self.v_date = Value(date(2001, 10, 11))
        self.v_time = Value(time(12, 30, 45))
        self.v_dt = Value(datetime(2001, 10, 11, 12, 30, 45))
        self.v_base = Value("foo", Type.base64)

    def test_init(self):
        self.assertEqual(self.v_int.dtype, Type.int)
        self.assertEqual(self.v_int.get(), 0)

        self.assertEqual(self.v_bool.dtype, Type.boolean)
        self.assertEqual(self.v_bool.get(), True)

        self.assertEqual(self.v_float.dtype, Type.double)
        self.assertEqual(self.v_float.get(), 0.0)

        self.assertEqual(self.v_str.dtype, Type.string)
        self.assertEqual(self.v_str.get(), "foo")

        self.assertEqual(self.v_date.dtype, Type.date)
        self.assertEqual(self.v_date.get(), date(2001, 10, 11))

        self.assertEqual(self.v_time.dtype, Type.time)
        self.assertEqual(self.v_time.get(), time(12, 30, 45))

        self.assertEqual(self.v_dt.dtype, Type.datetime)
        self.assertEqual(self.v_dt.get(), datetime(2001, 10, 11, 12, 30, 45))

        self.assertEqual(self.v_base.dtype, Type.base64)
        self.assertEqual(self.v_base.get(), "foo")

    def test_set_strict(self):
        self.v_int.strict_mode = True

        self.v_int.set(100)
        self.assertEqual(self.v_int.get(), 100)

        self.assertRaises(ValueError, lambda: self.v_int.set(True))
        self.assertRaises(ValueError, lambda: self.v_int.set(0.11))
        self.assertRaises(ValueError, lambda: self.v_int.set("NoInt"))
        self.assertRaises(ValueError, lambda: self.v_int.set(date(2000, 1, 1)))
        self.assertRaises(ValueError, lambda: self.v_int.set(time(11, 20, 50)))

        self.v_date.strict_mode = True

        self.v_date.set(date(1999, 1, 2))
        self.assertEqual(self.v_date.get(), date(1999, 1, 2))

        self.assertRaises(ValueError, lambda: self.v_date.set(time(11, 20, 50)))
        self.assertRaises(ValueError, lambda: self.v_date.set("NoDate"))
        self.assertRaises(ValueError, lambda: self.v_date.set(11.11))
        self.assertRaises(ValueError, lambda: self.v_date.set(False))

    def test_dtype_strict(self):
        pass