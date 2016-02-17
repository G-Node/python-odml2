# coding=UTF-8

# Copyright (c) 2015, Adrian Stoewer (adrian.stoewer@rz.ifi.lmu.de)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the project.

from future.utils import python_2_unicode_compatible
import enum

import odml2
from odml2.model import VALUE_TYPE_MAP
from odml2.checks import assert_prefixed_name, split_prefixed_name, join_prefixed_name

__all__ = ("TerminologyStrategy", )


VALUE_TYPE_NAMES = tuple(VALUE_TYPE_MAP.values())


# noinspection PyShadowingBuiltins
def _get_type_definition(document, prefix, type):
    if prefix is not None:
        if prefix in document.namespaces:
            document = document.namespaces[prefix].get_document()
        else:
            raise ValueError("The namespace '%s' is not known in this document" %
                             join_prefixed_name(prefix, type))

    if type not in document.type_definitions:
        raise ValueError("The type '%s' is not known in this document" %
                         join_prefixed_name(prefix, type))

    return document.type_definitions[type]


def _get_prop_definition(document, prefix, prop):
    if prefix is not None:
        if prefix in document.namespaces:
            document = document.namespaces[prefix].get_document()
        else:
            raise ValueError("The namespace '%s' is not known in this document" %
                             join_prefixed_name(prefix, prop))

    if prop not in document.property_definitions:
        raise ValueError("The property '%s' in not known in this document" %
                         join_prefixed_name(prefix, prop))

    return document.property_definitions[prop]


class BasicStrategy(object):
    """
    Just checks whether the property and type names are valid names.
    """

    def handle_triple(self, document, source_type, prop, target_type):
        assert_prefixed_name(source_type)
        assert_prefixed_name(prop)
        assert_prefixed_name(target_type)

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

        target_prefix, target_type = split_prefixed_name(target_type)
        if target_prefix is None:
            if target_type not in document.type_definitions and target_type not in VALUE_TYPE_NAMES:
                document.type_definitions[target_type] = odml2.TypeDef(target_type)
        else:
            _get_type_definition(document, target_prefix, target_type)

        prop_prefix, prop = split_prefixed_name(prop)
        if prop_prefix is None:
            full_target_type = join_prefixed_name(target_prefix, target_type)
            if prop not in document.property_definitions:
                document.property_definitions[prop] = odml2.PropertyDef(prop, types={full_target_type})
            else:
                prop_def = document.property_definitions[prop]
                prop_def.copy(types=prop_def.types | {full_target_type})
                document.property_definitions[prop] = prop_def
        else:
            _get_prop_definition(document, prop_prefix, prop)

        source_prefix, source_type = split_prefixed_name(source_type)
        if source_prefix is None:
            full_prop_name = join_prefixed_name(prop_prefix, prop)
            if source_type not in document.type_definitions:
                document.type_definitions[source_type] = odml2.TypeDef(source_type, properties={full_prop_name})
            else:
                source_def = document.type_definitions[source_type]
                source_def = source_def.copy(properties=source_def.properties | {full_prop_name})
                document.type_definitions[source_type] = source_def
        else:
            _get_type_definition(document, source_prefix, source_type)

    # noinspection PyShadowingBuiltins
    def handle_type(self, document, type):
        super(CreateStrategy, self).handle_type(document, type)
        prefix, type = split_prefixed_name(type)
        if prefix is None:
            if type not in document.type_definitions:
                document.type_definitions[type] = odml2.TypeDef(type)
        else:
            _get_type_definition(document, prefix, type)


# TODO implement strict strategy
class StrictStrategy(BasicStrategy):
    """
    Only allows consistent use of known properties or types.
    """

    def handle_triple(self, document, source_type, prop, target_type):
        super(StrictStrategy, self).handle_triple(document, source_type, prop, target_type)
        source_prefix, source_type = split_prefixed_name(source_type)
        source_def = _get_type_definition(document, source_prefix, source_type)

        property_prefix, prop = split_prefixed_name(prop)
        if prop not in source_def.properties:
            raise ValueError("The property '%s' is not defined for type '%s'" %
                             (prop, join_prefixed_name(source_prefix, source_type)))

        property_def = _get_prop_definition(document, property_prefix, prop)
        target_prefix, target_type = split_prefixed_name(target_type)
        if target_type not in property_def.types:
            raise ValueError("The type '%s' is not defined for property '%s'" %
                             (target_type, join_prefixed_name(property_prefix, prop)))

    # noinspection PyShadowingBuiltins
    def handle_type(self, document, type):
        super(StrictStrategy, self).handle_type(document, type)
        prefix, type = split_prefixed_name(type)
        _get_type_definition(document, prefix, type)


@python_2_unicode_compatible
class TerminologyStrategy(BasicStrategy, enum.Enum):
    Ignore = BasicStrategy()
    Create = CreateStrategy()
    Strict = StrictStrategy()

    def handle_triple(self, document, source_type, prop, target_type):
        self.value.handle_triple(document, source_type, prop, target_type)

    # noinspection PyShadowingBuiltins
    def handle_type(self, document, type):
        self.value.handle_type(document, type)

    def __str__(self):
        return "TerminologyStrategy.%s" % self.name

    def __repr__(self):
        return str(self)
