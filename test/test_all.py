# Copyright (c) 2014, Adrian Stoewer (adrian.stoewer@rz.ifi.lmu.de)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.

import unittest

from test.test_types import TestTypes
from test.test_base import TestWithSections


class TestAll(unittest.TestSuite):

    def __init__(self):
        super(TestAll, self).__init__()
        self.addTests(unittest.makeSuite(TestTypes))
        self.addTests(unittest.makeSuite(TestWithSections))


if __name__ == "__main__":
    test = TestAll()
    unittest.TextTestRunner(verbosity=2).run(test)
