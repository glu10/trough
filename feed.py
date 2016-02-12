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

class Feed:
    """ An RSS Feed, contains RSS Items """

    def __init__(self, name, uri, category=None, refresh_limit=None):
        self.name = name  # Externally enforced as unique
        self.uri = uri
        self.items = list()

        # TO BE IMPLEMENTED:
        #self.category = category
        #self.refresh_limit = refresh_limit  # ms

    @staticmethod
    def from_dict(attribute_dict):
        attributes = ['name', 'uri']
        for attribute in attributes:
            if attribute not in attribute_dict:
                raise RuntimeError('A Feed Object could not be deserialized correctly, ' + attribute +
                                   ' was not present in the dictionary ' + str(attribute_dict))

        return Feed(attribute_dict['name'], attribute_dict['uri'])

    def to_dict(self):
        # Can't just use __dict__ because the items list is going to be excluded
        return {'name': self.name, 'uri': self.uri}

    def __eq__(self, other):  # TODO: URI check?
        return self.name == other.name
