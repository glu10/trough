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

# Threading imports
from threading import Thread
from queue import Queue, Empty
from gi.repository import Gdk


class Gatherer():
    """ Gatherer is a singleton responsible for handling network requests """

    def __init__(self, parent, config):
        self.parent = parent
        self.config = config
        self.collected_items = None
        self.request_queue = Queue()
        self.fulfilled_queue = Queue()

        self.thread = GathererWorkerThread(self, self.request_queue, self.fulfilled_queue)
        self.thread.start()

    def emit(self, *args):
        self.parent.emit(*args)

    def grab_scrape_result(self):
        try:
            item = self.fulfilled_queue.get(block=False)
            return item
        except Empty:
            return None

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

        # Not sure if this is my problem or feedparser's but XML Character Entity References aren't all getting caught
        description = re.sub(r'\&\#8211\;', '-', description)
        description = re.sub(r'\&\#8212\;', '—', description)
        description = re.sub(r'\&\#8216\;', '‘', description)
        description = re.sub(r'\&\#8217\;', '’', description)
        description = re.sub(r'\&\#8220\;', '“', description)
        description = re.sub(r'\&\#8221\;', '”', description)
        description = re.sub(r'(\[)*\&\#8230\;(\])*', '…', description)

        return re.sub(r'<.*?>', '', description)

    @staticmethod
    def get_and_set_article(item):
        if not item.article:  # Don't bother if the article has already been set
            article_html = requests.get(item.link).content
            item.article = select_rule(item.link, article_html)
        return item.article


class GathererWorkerThread(Thread):
    def __init__(self, parent, request_queue, fulfilled_queue):
        super().__init__(target=self.serve_requests)
        self.parent = parent
        self.daemon = True
        self.request_queue = request_queue
        self.fulfilled_queue = fulfilled_queue

    def serve_requests(self):
        while True:
            item = self.request_queue.get(block=True)
            if not item.article:
                article_html = requests.get(item.link).content
                item.article = select_rule(item.link, article_html)
                self.fulfilled_queue.put(item)
                Gdk.threads_enter()
                self.parent.emit('new_story_event')
                Gdk.threads_leave()









