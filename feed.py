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

from threading import Lock


class Feed:
    """ An RSS Feed, contains RSS Items """

    def __init__(self, name, uri, category="Uncategorized", refresh_limit=None):
        self.name = name  # Externally enforced as unique
        self.uri = uri
        self.items = list()
        self.lock = Lock()  # for preventing multiple requests
        self.category = category

    @staticmethod
    def from_dict(attribute_dict):
        """ Deserialization """
        attributes = ['name', 'uri', 'category']
        for attribute in attributes:
            if attribute not in attribute_dict:
                raise RuntimeError('A Feed Object could not be deserialized correctly, ' + attribute +
                                   ' was not present in the dictionary ' + str(attribute_dict))
        return Feed(*[attribute_dict[attribute] for attribute in attributes])

    def to_dict(self):
        """ Serialization """
        return {'name': self.name, 'uri': self.uri, 'category': self.category}

    def to_value_list(self):
        return [self.name, self.uri]

    def sort_items(self):
        """ Bucket sort with 3 buckets. """
        if self.items:
            buckets = [list(), list(), list()]
            for item in self.items:
                buckets[item.ranking()].append(item)

            i = 0
            for bucket in buckets:
                for item in bucket:
                    self.items[i] = item
                    i += 1

    def is_fake(self):
        return not self.uri

    def __eq__(self, other):
        return self.name == other.name
