"""
    Trough - a GTK+ RSS news reader

    Copyright (C) 2017 Andrew Asp
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

from typing import List

import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

from item import Item


class NewsStore:
    """ A centralized data repository of all viewable fetched content. """

    def __init__(self):
        self.store = Gtk.ListStore(
            str,  # Feed Name
            str,  # Item URI
            str,  # Item Title
            str,  # Item Description
            str, )  # Item Article

    def append(self, item: Item) -> None:
        self.store.append([
            item.feed_name,
            item.uri,
            item.title,
            item.description,
            item.article
        ])

    @staticmethod
    def row_to_item(row: List[str]) -> Item:
        return Item(*row)

    def model(self) -> Gtk.TreeModel:
        return self.store

    def clear(self) -> None:
        self.store.clear()
