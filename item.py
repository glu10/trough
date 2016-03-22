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
from threading import Lock
from utilityFunctions import string_to_RGBA


class Item:
    """ An RSS item """
    def __init__(self, label, title='', description='', link=''):
        self.label = label
        self.title = title
        self.description = description
        self.link = link
        self.filtered = False
        self.article = None  # from scraping
        self.lock = Lock()  # prevents an item from accidentally being scraped by multiple threads at once

    @classmethod
    def from_href(cls, label, href):
        from bs4.element import Tag
        assert(type(href) == Tag)

        link = href.get('href')
        if link is None:
            link = ''

        return cls(label, title=href.text, link=link)

    def get_color(self, appearance_dict):
        keys = ['Font Color', 'Filtered Color', 'Read Color']
        color_string = appearance_dict[keys[self.ranking()]]
        return string_to_RGBA(color_string)

    def ranking(self):
        """ Used for item ordering/classification. Priority: Unread -> Unread but Filtered -> Read """
        if self.article:
            return 2
        elif self.filtered:
            return 1
        else:
            return 0

    def __lt__(self, other):
        return self.ranking() < other.ranking()

    def __eq__(self, other):
        return self.ranking() == other.ranking()





