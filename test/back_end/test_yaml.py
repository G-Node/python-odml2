# coding=UTF-8

# Copyright (c) 2015, Adrian Stoewer (adrian.stoewer@rz.ifi.lmu.de)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the project.

import unittest
from odml2.back_end.yaml import YamlBackEnd


class YamlBackEndTest(unittest.TestCase):

    def setUp(self):
        self.empty = YamlBackEnd()

    def test_root(self):
        self.assertFalse(self.empty.root_exists())
