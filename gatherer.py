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

    The full project can be found at: https://github.com/glu10/trough
"""

import feedparser
import requests
from scraping import select_rule
from item import Item

class Gatherer:

    def __init__(self):
        self.collected_items = None

    #TODO: Error checking, temp variable collection used to mitigate blowing up current list.
    def collect(self, feeds):
        collection = list()

        for label, uri in feeds.items():
            content = feedparser.parse(uri)
            for entry in content['entries']:
                item = Item(label, entry['title'], entry['description'], entry['link'])
                #if 'image' in entry.keys():
                 #   self.fetch_image(item, entry['image'])
                collection.append(item)

        if collection is not None:
            self.collected_items = collection

        return self.collected_items

    @staticmethod
    def get_article(link):
        article_html = requests.get(link).content
        return select_rule(link, article_html)

    @staticmethod
    def get_and_set_article(item):
        if not item.article:  # Don't bother if the article has already been set
            article_html = requests.get(item.link).content
            item.article = select_rule(item.link, article_html)
        return item.article
