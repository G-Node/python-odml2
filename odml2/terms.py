# coding=UTF-8

# Copyright (c) 2015, Adrian Stoewer (adrian.stoewer@rz.ifi.lmu.de)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the project.

import six
import enum

from odml2.model import ALLOWED_VALUE_TYPES
from odml2.checks import assert_prefixed_name

__all__ = ("TerminologyStrategy", "BasicStrategy")


class BasicStrategy(object):
    """
    Just checks whether the property and type names are valid names.
    """
    def handle_triple(self, document, source_type, prop, target_type):
        assert_prefixed_name(source_type)
        assert_prefixed_name(prop)
        if isinstance(target_type, six.string_types):
            assert_prefixed_name(target_type)
        elif not issubclass(target_type, ALLOWED_VALUE_TYPES):
            raise ValueError("Not a valid target type: %s" % target_type)

    # noinspection PyShadowingBuiltins
    def handle_type(self, document, type):
        assert_prefixed_name(type)


# TODO implement create strategy
class CreateStrategy(BasicStrategy):
    """
    Creates properties and types on the fly.
    """
    def handle_triple(self, document, source_type, prop, target_type):
        super(CreateStrategy, self).handle_triple(document, source_type, prop, target_type)

    # noinspection PyShadowingBuiltins
    def handle_type(self, document, type):
        super(CreateStrategy, self).handle_type(document, type)


# TODO implement loose strategy
class LooseStrategy(BasicStrategy):
    """
    Only checks known properties and types for consistency.
    """
    def handle_triple(self, document, source_type, prop, target_type):
        super(LooseStrategy, self).handle_triple(document, source_type, prop, target_type)

    # noinspection PyShadowingBuiltins
    def handle_type(self, document, type):
        super(LooseStrategy, self).handle_type(document, type)


# TODO implement strict strategy
class StrictStrategy(BasicStrategy):
    """
    Only allows consistent use of known properties or types.
    """
    def handle_triple(self, document, source_type, prop, target_type):
        super(StrictStrategy, self).handle_triple(document, source_type, prop, target_type)

    # noinspection PyShadowingBuiltins
    def handle_type(self, document, type):
        super(StrictStrategy, self).handle_type(document, type)


class TerminologyStrategy(BasicStrategy, enum.Enum):
    Ignore = BasicStrategy()
    Create = CreateStrategy()
    Loose = LooseStrategy()
    Strict = StrictStrategy()
