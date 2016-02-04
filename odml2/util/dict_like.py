# coding=UTF-8

# Copyright (c) 2015, Adrian Stoewer (adrian.stoewer@rz.ifi.lmu.de)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the project.

import abc
import six
import collections


@six.add_metaclass(abc.ABCMeta)
class DictLike(object):
    """
    Dictionary like access to related objects.
    """

    @abc.abstractmethod
    def get(self, key):
        """
        :param key: The key of the related object.
        :return: object
        """
        pass

    @abc.abstractmethod
    def keys(self):
        """
        Iterable containing all keys.
        :rtype: collections.Iterable[str]
        """
        pass

    @abc.abstractmethod
    def remove(self, key):
        pass

    @abc.abstractmethod
    def clear(self):
        pass

    def values(self):
        for key in self.keys():
            yield self[key]

    def items(self):
        for key in self.keys():
            yield (key, self[key])

    def __getitem__(self, key):
        item = self.get(key)
        if item is None:
            raise KeyError(key)
        return item

    def __delitem__(self, key):
        self.remove(key)

    def __contains__(self, item):
        return item in self.keys() or item in self.values()

    def __iter__(self):
        return self.keys()

    def __len__(self):
        return sum(1 for _ in self.keys())

collections.Iterable.register(DictLike)
