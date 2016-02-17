# coding=UTF-8

# Copyright (c) 2015, Adrian Stoewer (adrian.stoewer@rz.ifi.lmu.de)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the project.

import six
# noinspection PyUnresolvedReferences
from six.moves import StringIO
# noinspection PyUnresolvedReferences
from six.moves.urllib.parse import urlparse

import io
import os
import requests
import datetime as dt
from future.utils import python_2_unicode_compatible

import odml2
from odml2.checks import split_prefixed_name
from odml2.api import yml, base

__all__ = ("BACK_ENDS", "Document", "TerminologyMode")


BACK_ENDS = (yml.YamlDocument, )


@python_2_unicode_compatible
class Document(object):
    """
    :param back_end:    The name of the back-end to use for this document or a back-end instance.
    :type back_end:     str | :class:`odml2.api.base.BaseDocument`
    :param strategy:    How to deal with definitions and terminologies.
    :type strategy:     :class:`~.TerminologyStrategy`
    """

    def __init__(self, back_end="yaml", strategy=odml2.TerminologyStrategy.Ignore):
        if isinstance(back_end, six.string_types):
            found = False
            for be in BACK_ENDS:
                if be.NAME == back_end:
                    found = True
                    self.__back_end = be()
                    break
            if not found:
                raise ValueError("No back-end found for '%s'" % back_end)
        elif isinstance(back_end, base.BaseDocument):
            self.__back_end = back_end
        else:
            raise ValueError("Not a valid back-end %s" % type(back_end))

        self.__strategy = strategy
        self.__namespaces = odml2.NameSpaceMap(self.__back_end)
        self.__property_defs = odml2.PropertyDefMap(self.__back_end)
        self.__type_defs = odml2.TypeDefMap(self.__back_end)

    @property
    def is_attached(self):
        """
        Whether or not the back-end used by the odML document is attached to a data source.
        This is a read only property.

        :type:     bool
        """
        return self.back_end.is_attached()

    @property
    def is_writable(self):
        """
        Whether or not the the document is writable. This is a read only property.

        :type:      bool
        """
        return self.back_end.is_writable()

    @property
    def location(self):
        """
        An uri or path to the location of the document. Is `None` for newly created documents.
        This is a read only property.

        :type:      str
        """
        return self.back_end.get_uri()

    @property
    def author(self):
        """
        The name of the documents author. Is `None` if not specified otherwise.

        :type:      str
        """
        return self.back_end.get_author()

    @author.setter
    def author(self, author):
        if not isinstance(author, six.string_types):
            raise ValueError("Author must be a string")
        self.back_end.set_author(author)

    @property
    def date(self):
        """
        The creation date of the document.

        :type:      :class:`datetime.date`
        """
        return self.back_end.get_date()

    @date.setter
    def date(self, date):
        if not isinstance(date, dt.date):
            raise ValueError("Date must be a date or datetime")
        self.back_end.set_date(date)

    @property
    def version(self):
        """
        The version of the document. Is `1` unless specified otherwise.

        :type:      int
        """
        return self.back_end.get_version()

    @version.setter
    def version(self, version):
        if not isinstance(version, int):
            raise ValueError("The document version must be an integer")
        self.back_end.set_version(version)

    @property
    def root(self):
        """
        The root section of the document. Is always `None` for newly created documents.
        If the document already contains sections the whole content of the document will be
        replaces with the new root.

        :type:      :class:`~.Section` | :class:`~.SB`
        """
        uuid = self.back_end.get_root()
        if uuid is None:
            return None
        return odml2.Section(uuid, self)

    # noinspection PyProtectedMember
    @root.setter
    def root(self, thing):
        if isinstance(thing, odml2.SB):
            thing.build(self)
        elif isinstance(thing, odml2.Section):
            thing._copy_section(self)
        else:
            raise ValueError("Only Section and SB can be used as root")

    # noinspection PyShadowingBuiltins
    def create_root(self, type, uuid, label=None, reference=None):
        """
        Create an empty root section. If the document already contains sections the whole content
        of the document will be replaces with the new root.

        *NOTICE:* This method is primarily for internal use (see :attr:`~.Document.root` as alternative)

        :param type:        The odML type name of the new section.
        :type type:         str
        :param uuid:        The uuid of the section.
        :type uuid:         str
        :param label:       The label (a human readable identifier) of the section
        :type label:        str|None
        :param reference:   A uri or path to other data referenced by this section.
        :type reference:    str|None

        :return:        :class:`~.Section`
        """
        self.terminology_strategy.handle_type(self, type)
        self.back_end.create_root(type, uuid, label, reference)
        return odml2.Section(uuid, self)

    def find_section_and_prefix(self, uuid, search_namespaces=False):
        """
        Find a :class:`~.Section` and its namespace within the document and associated
        documents.

        :param uuid:        The UUID of the section
        :type uuid:         str
        :param search_namespaces:   If True also search in other namespaces.
        :type search_namespaces:    bool

        :return:    The section with its namespace or None
        """
        document, prefix, is_link = None, None, False

        if uuid in self.back_end.sections:
            document = self
        elif search_namespaces:
            p, uuid = split_prefixed_name(uuid)
            if p is None:
                for ns in self.namespaces.values():
                    tmp = ns.get_document()
                    if uuid in tmp.back_end.sections:
                        document, prefix, is_link = tmp, ns.prefix, True
                        break
            if p in self.namespaces:
                tmp = self.namespaces[p].get_document()
                if uuid in tmp.back_end.sections:
                    document, prefix, is_link = tmp, p, True

        if document is not None:
            return odml2.Section(uuid, document), prefix
        else:
            return None, None

    def find_section(self, uuid, search_namespaces=False):
        """
        Find a :class:`~.Section` within the document and associated documents.

        :param uuid:        The UUID of the section
        :type uuid:         str
        :param search_namespaces:   If True also search in other namespaces.
        :type search_namespaces:    bool

        :return:    The found section or None
        """
        section, prefix = self.find_section_and_prefix(uuid, search_namespaces)
        return section

    def iter_sections(self):
        """
        Iterate over all :class:`~.Section` objects of the odML document.

        :rtype:     generator
        """
        for uuid in self.back_end.sections:
            yield odml2.Section(uuid, self)

    @property
    def namespaces(self):
        """
        A dictionary like access to all name spaces of the document. Name spaces can be
        used to include other documents under a certain prefix.

        :type:      :class:`~.NameSpaceMap`
        """
        return self.__namespaces

    @property
    def type_definitions(self):
        """
        Dictionary like access to all type definitions. Type definitions are terms
        that provide descriptions for section types which may occur in a document.

        :type:      :class:`~.TypeDefMap`
        """
        return self.__type_defs

    @property
    def property_definitions(self):
        """
        Dictionary like access to all property definitions. Property definitions are terms
        that provide descriptions for properties which may occur in sections of the document.

        :type:      :class:`~.PropertyDefMap`
        """
        return self.__property_defs

    @property
    def back_end(self):
        """
        The back-end used by a document.

        *NOTICE*: This is mostly for internal use.

        :type:      :class:`odml2.api.base.BaseDocument`
        """
        return self.__back_end

    @property
    def terminology_strategy(self):
        """
        The terminology strategy defines how section types and property names are
        handled with respect to a given terminology.

        :class:`~.TerminologyStrategy`
        """
        return self.__strategy

    @terminology_strategy.setter
    def terminology_strategy(self, strategy):
        self.__strategy = strategy

    def save(self, destination=None):
        """
        Save a document to a given destination.

        :param destination:     Where to store the content of the document.
        :type destination:      str | io.FileIO | io.StringIO
        """
        if not hasattr(destination, "write"):
            parsed = urlparse(destination)
            if parsed.scheme == "file" or parsed.scheme == "":
                with io.open(destination, "w", encoding="utf-8") as f:
                    self.back_end.save(f, destination)
            else:
                raise RuntimeError("Unable to save to destination: %s" % destination)
        else:
            uri = destination.name if hasattr(destination, "name") else None
            self.back_end.save(destination, uri)

    def load(self, source, is_writable=True):
        """
        Load data to the document from a certain source.

        :param source:      Where to load the content of the document from.
        :type source:       str | io.FileIO | io.StringIO
        :param is_writable: Whether or not the loaded document should be writable.
        :type is_writable:  bool
        """
        if not hasattr(source, "read"):
            parsed = urlparse(source)
            if parsed.scheme == "file" or parsed.scheme == "":
                _, extension = os.path.splitext(source)
                back_end = self.__find_back_end(extension)(is_writable)
                with io.open(source, "r", encoding="utf-8") as f:
                    back_end.load(f, source)
                self.__set_back_end(back_end)
            elif parsed.scheme == "http":
                result = requests.get(source)
                mime_type = result.headers["content-type"].split(";")[0]
                back_end = self.__find_back_end(mime_type)(is_writable)
                back_end.load(StringIO(result.text), source)
                self.__set_back_end(back_end)
            else:
                raise RuntimeError("Unable to load from source: %s" % source)
        else:
            self.back_end.load(source)

    # noinspection PyMethodMayBeStatic
    def __find_back_end(self, hint):
        for be in BACK_ENDS:
            if hint == be.NAME or hint in be.FEXT or hint in be.MIME:
                return be
        raise ValueError("No suitable back-end fund for: %s" % hint)

    def __set_back_end(self, be):
        self.__back_end = be
        self.__namespaces = odml2.NameSpaceMap(self.__back_end)
        self.__property_defs = odml2.PropertyDefMap(self.__back_end)
        self.__type_defs = odml2.TypeDefMap(self.__back_end)

    def __str__(self):
        return u"Document(location='%s', author='%s', date=%s)" % (self.back_end.get_uri(), self.author, self.date)

    def __repr__(self):
        return str(self)
