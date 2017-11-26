"""
    Trough - a GTK+ RSS news reader

    Copyright (C) 2015 Andrew Asp
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

from typing import Iterable


class Item:
    """ An RSS item """

    def __init__(self, feed_name: str, uri: str, title: str = '', description: str = '', article: str = None):
        self.feed_name = feed_name
        self.uri = uri
        self.title = title
        self.description = description
        self.article = article

    def __iter__(self) -> Iterable[str]:
        return [self.feed_name, self.uri, self.title, self.description, self.article]
