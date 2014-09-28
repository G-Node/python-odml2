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
        self.assertEqual(self.v_int.data, 0)

        self.assertEqual(self.v_bool.dtype, Type.boolean)
        self.assertEqual(self.v_bool.data, True)

        self.assertEqual(self.v_float.dtype, Type.double)
        self.assertEqual(self.v_float.data, 0.0)

        self.assertEqual(self.v_str.dtype, Type.string)
        self.assertEqual(self.v_str.data, "foo")

        self.assertEqual(self.v_date.dtype, Type.date)
        self.assertEqual(self.v_date.data, date(2001, 10, 11))

        self.assertEqual(self.v_time.dtype, Type.time)
        self.assertEqual(self.v_time.data, time(12, 30, 45))

        self.assertEqual(self.v_dt.dtype, Type.datetime)
        self.assertEqual(self.v_dt.data, datetime(2001, 10, 11, 12, 30, 45))

        self.assertEqual(self.v_base.dtype, Type.base64)
        self.assertEqual(self.v_base.data, "foo")

    def test_data_strict(self):
        pass

    def test_dtype_strict(self):
        pass