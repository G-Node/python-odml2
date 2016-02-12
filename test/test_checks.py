# coding=UTF-8

# Copyright (c) 2015, Adrian Stoewer (adrian.stoewer@rz.ifi.lmu.de)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the project.

import string
import unittest
from uuid import uuid4
from random import randint

from odml2.checks import *


ALLOWED = string.ascii_letters + string.digits + "-_"
HEX = string.digits + "abcdefABCDEF"


def random_str(n, alpha=ALLOWED):
    return "".join([alpha[randint(0, len(alpha) - 1)] for _ in range(0, n)])


class TestChecks(unittest.TestCase):

    def test_is_name(self):
        self.assertFalse(is_name(""))
        self.assertFalse(is_name("a" * 257))
        self.assertTrue(is_name("a"))
        self.assertTrue(is_name("a" * 256))

        self.assertTrue(is_name(random_str(256)))
        self.assertFalse(is_name(random_str(255) + "."))
        self.assertFalse(is_name(random_str(255) + ":"))
        self.assertFalse(is_name(random_str(255) + "/"))
        self.assertFalse(is_name(random_str(255) + "\\"))
        self.assertFalse(is_name(random_str(255) + " "))

    def test_is_prefix(self):
        self.assertFalse(is_prefix(""))
        self.assertFalse(is_prefix("a" * 128))
        self.assertTrue(is_prefix("a"))
        self.assertTrue(is_prefix("a" * 127))

        self.assertTrue(is_prefix(random_str(127)))
        self.assertFalse(is_prefix(random_str(126) + "."))
        self.assertFalse(is_prefix(random_str(126) + ":"))
        self.assertFalse(is_prefix(random_str(126) + "/"))
        self.assertFalse(is_prefix(random_str(126) + "\\"))
        self.assertFalse(is_prefix(random_str(126) + " "))

    def test_is_prefixed_name(self):
        self.assertFalse(is_prefixed_name(""))
        self.assertFalse(is_prefixed_name(":"))
        self.assertFalse(is_prefixed_name(":a"))
        self.assertFalse(is_prefixed_name("a:"))
        self.assertFalse(is_prefixed_name("a" * 128 + ":a"))
        self.assertFalse(is_prefixed_name("a:" + "a" * 257))
        self.assertTrue(is_prefixed_name("a"))
        self.assertTrue(is_prefixed_name("a:a"))
        self.assertTrue(is_prefixed_name("a" * 127 + ":a"))
        self.assertTrue(is_prefixed_name("a:" + "a" * 256))

        self.assertTrue(is_prefixed_name(random_str(256)))
        self.assertTrue(is_prefixed_name(random_str(127) + ":" + random_str(256)))
        self.assertFalse(is_prefixed_name(random_str(127) + ":" + random_str(255) + ":"))
        self.assertFalse(is_prefixed_name(random_str(127) + ":" + random_str(255) + "."))
        self.assertFalse(is_prefixed_name(random_str(127) + ":" + random_str(255) + "/"))
        self.assertFalse(is_prefixed_name(random_str(127) + ":" + random_str(255) + "\\"))
        self.assertFalse(is_prefixed_name(random_str(127) + ":" + random_str(255) + " "))

    def test_is_uuid(self):
        self.assertFalse(is_uuid("a" * 35))
        self.assertFalse(is_uuid("a" * 37))
        self.assertTrue(is_uuid("a" * 36))

        for _ in range(0, 100):
            self.assertTrue(is_uuid(random_str(36, HEX+"-")))
            self.assertTrue(is_uuid(str(uuid4())))
        self.assertFalse(is_uuid(random_str(35, HEX+"-") + "."))
        self.assertFalse(is_uuid(random_str(35, HEX+"-") + ":"))
        self.assertFalse(is_uuid(random_str(35, HEX+"-") + "/"))
        self.assertFalse(is_uuid(random_str(35, HEX+"-") + "\\"))
        self.assertFalse(is_uuid(random_str(35, HEX+"-") + " "))
