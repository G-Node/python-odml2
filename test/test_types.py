# Copyright (c) 2014, Adrian Stoewer (adrian.stoewer@rz.ifi.lmu.de)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.

import unittest

from datetime import datetime, date, time
from odml.types import *


class TestTypes(unittest.TestCase):

    def test_is_valid_type(self):
        for name in [x.name for x in Type]:
            assert(is_valid_type(name))
            assert(not is_valid_type(name + 'x'))
            assert(not is_valid_type('y' + name))
            assert(not is_valid_type(name[0:len(name) - 2]))
            assert(not is_valid_type(name[1:len(name)]))

    def test_is_valid_value(self):
        assert(is_valid_value('99 ', Type.int))
        assert(is_valid_value(' 00', Type.int))
        assert(not is_valid_value('a99', Type.int))
        assert(not is_valid_value('1.1', Type.int))

        assert(is_valid_value('9.9 ', Type.double))
        assert(is_valid_value(' 0.0e10', Type.double))
        assert(not is_valid_value('a9.9', Type.double))
        assert(not is_valid_value('1.1e', Type.double))

        assert(is_valid_value('true ', Type.boolean))
        assert(is_valid_value(' false', Type.boolean))
        assert(is_valid_value('0 ', Type.boolean))
        assert(is_valid_value('1', Type.boolean))
        assert(not is_valid_value('9', Type.boolean))
        assert(not is_valid_value('False', Type.boolean))

        assert(is_valid_value('2004-10-10', Type.date))
        assert(not is_valid_value('2003/01/02', Type.date))

        assert(is_valid_value('16:50:50', Type.time))
        assert(not is_valid_value('16:70:90', Type.time))

        assert(is_valid_value('2004-10-10 16:50:50', Type.datetime))
        assert(not is_valid_value('2004/10/10 16:70:90', Type.datetime))
        assert(not is_valid_value('2004-10-0T13:10:10', Type.datetime))

        assert(is_valid_value('Zm9vYmFy', Type.base64))
        assert(not is_valid_value('foo', Type.base64))

    def test_value_to_string(self):
        assert(value_to_string(11, Type.int) == '11')
        assert(value_to_string(1.1, Type.double) == '1.1')
        assert(value_to_string(True, Type.boolean) == 'true')
        assert(value_to_string(False, Type.boolean) == 'false')
        assert(value_to_string(date(2001, 10, 11), Type.date) == '2001-10-11')
        assert(value_to_string(time(12, 30, 45), Type.int) == '12:30:45')
        assert(value_to_string(datetime(2001, 10, 11, 12, 30, 45), Type.int) == '2001-10-11 12:30:45')
        assert(value_to_string(b'foobar', Type.base64) == b'Zm9vYmFy')

    def test_string_to_value(self):
        assert(string_to_value(' 1', Type.int) == 1)
        assert(string_to_value('2.2 ', Type.double) == 2.2)
        assert(string_to_value(' 1', Type.boolean))
        assert(not string_to_value(' false', Type.boolean))
        assert(string_to_value('2001-10-11', Type.date) == date(2001, 10, 11))
        assert(string_to_value('12:30:45', Type.time) == time(12, 30, 45))
        assert(string_to_value('2001-10-11 12:30:45', Type.datetime) == datetime(2001, 10, 11, 12, 30, 45))
        assert(string_to_value(b'Zm9vYmFy', Type.base64) == b'foobar')


if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite.addTests(unittest.makeSuite(TestTypes))
    unittest.TextTestRunner(verbosity=2).run(suite)