# Copyright (c) 2014, Adrian Stoewer (adrian.stoewer@rz.ifi.lmu.de)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.

from __future__ import unicode_literals, absolute_import, division, print_function, generators
import unittest


class TestWithSections(unittest.TestCase):
    pass


if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite.addTests(unittest.makeSuite(TestWithSections))
    unittest.TextTestRunner(verbosity=2).run(suite)