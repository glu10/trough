"""
    Trough - a GTK+ RSS news reader

    Copyright (C) 2016 Andrew Asp
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see {http://www.gnu.org/licenses/}.

    Trough homepage: https://github.com/glu10/trough
"""

from collections import defaultdict
from itertools import chain


class Feed:
    """ An RSS Feed that contains RSS Items """
    serializable_attributes = ['name', 'uri', 'category']

    def __init__(self, name, uri, category="Uncategorized"):
        self.name = name  # Externally enforced as unique
        self.uri = uri
        self.items = []
        self.category = category

    @staticmethod
    def from_dict(cls, attribute_dict):
        """ Deserialization """
        try:
            return Feed(
                    *[attribute_dict[attribute] for attribute
                        in cls.serializable_attributes])
        except KeyError as e:
            missing_key = e.args[0]
            raise RuntimeError(
                    'Feed deserialization failed: {}, missing required key {}'
                    .format(attribute_dict, missing_key))

    def to_dict(self):
        """ Serialization """
        return {'name': self.name, 'uri': self.uri, 'category': self.category}

    def to_value_list(self):
        return [self.name, self.uri]

    def sort_items(self):
        """ Return items sorted by ranking """
        buckets = defaultdict(list)
        for item in self.items:
            buckets[item.ranking()].append(item)
        sorted_buckets = sorted(buckets.items(), key=lambda bucket: bucket[0])
        self.items = list(chain.from_iterable(sorted_buckets))

    def is_fake(self):
        return not self.uri

    def __eq__(self, other):
        return self.name == other.name
