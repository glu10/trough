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

""" This file will contain rules for RSS feeds whose format does not bode well
    with the defaults. Each rule will be associated with a URI identifier. """

from abc import ABCMeta, abstractmethod
import feedparser
from item import Item

#TODO: This class is currently unused but here for future reference
#TODO: Currently not protected against missing titles/descriptions

class RssRule(metaclass=ABCMeta):

    @abstractmethod
    def parse_for_items(self, uri, label):
        """ Return a list of items in the news feed. """
        items = list()
        content = feedparser.parse(uri)
        for entry in content['entries']:
            item = Item(label, self.item_title(entry), self.item_description(entry), self.item_link['link'])
            items.append(item)
        return items

    @abstractmethod
    def item_title(self, entry):
        """ Given an entry, return what should be its title. """
        return entry['title']

    @abstractmethod
    def item_description(self, entry):
        """ Given an entry, return what should be its description. """
        return entry['description']

    @abstractmethod
    def item_link(self, entry):
        """ Given an entry, return what should be its link. """
        return entry['link']












