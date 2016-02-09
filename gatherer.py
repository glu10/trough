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

import requests
import re
import utilityFunctions

from scraping import select_rule
from item import Item

class Gatherer:
    """ Gatherer is a singleton responsible for handling network requests """

    def __init__(self, config):
        self.config = config
        self.collected_items = None

    def item(self, index):
        if self.collected_items and 0 <= index <= len(self.collected_items):
            return self.collected_items[index]
        else:
            return None

    def collect(self):
        collection = list()

        feeds = self.config.feeds()

        if not feeds:  # If there are no feeds, don't gather anything because there isn't anything to gather.
            pass

        for label, uri in feeds.items():

            content = utilityFunctions.feedparser_parse(uri)

            if content:
                for entry in content['entries']:
                    keys = list(entry.keys())

                    title = ""
                    description = ""
                    link = ""

                    if 'description' in keys:
                        description = entry['description']
                    elif 'summary' in keys:
                        description = entry['summary']

                    if 'title' in keys:
                        title = entry['title']

                    if 'link' in keys:
                        link = entry['link']

                    if not title and not description and not link:
                        print('WARNING: The following entry with label ' + label +
                              ' has no title, description, or link. Skipped.' + str(entry))
                        continue

                    item = Item(label, title, self.description_cleanup(description), link)
                    collection.append(item)

        self.collected_items = collection
        return self.collected_items

    @staticmethod
    def description_cleanup(description):
        description = re.sub(r'\s+', ' ', description)
        description = re.sub(r'\n\n(\n+)', '\n\n', description)
        return re.sub(r'<.*?>', '', description)

    @staticmethod
    def get_and_set_article(item):
        if not item.article:  # Don't bother if the article has already been set
            article_html = requests.get(item.link).content
            item.article = select_rule(item.link, article_html)
        return item.article
