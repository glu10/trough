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

from typing import Dict, List


class Feed:
    """ An RSS Feed that contains RSS Items """
    serializable_attributes = ['name', 'uri']

    def __init__(self, name: str, uri: str):
        self.name = name  # Externally enforced as unique
        self.uri = uri

    @classmethod
    def from_dict(cls, attributes: Dict[str, Dict[str, str]]):
        """ Deserialization """
        return Feed(**attributes)

    def to_dict(self) -> dict:
        """ Serialization """
        return {'name': self.name, 'uri': self.uri}

    def to_value_list(self) -> List[str]:
        return [self.name, self.uri]

    def __eq__(self, other):
        if isinstance(other, Feed):
            return self.name == other.name
        else:
            return NotImplemented
