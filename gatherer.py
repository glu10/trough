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
from feed import Feed
from collections import defaultdict
from cache import Cache

# Threading imports
from threading import Thread
from queue import Queue, Empty
from gi.repository import Gdk


class Gatherer:
    """ Gatherer is a singleton responsible for handling network requests """

    def __init__(self, parent, config):
        self.parent = parent
        self.config = config
        self.cache = Cache()
        self.request_queue = Queue()  # Can contain Feed Requests and Item (scraping) requests
        self.fulfilled_feed_queue = Queue()
        self.fulfilled_scrape_queue = Queue()

        self.threads = self.create_and_start_threads(2)

    def create_and_start_threads(self, num_threads):
        threads = list()
        for i in range(num_threads):
            thread = GathererWorkerThread(self, self.cache,
                                          self.request_queue, self.fulfilled_feed_queue, self.fulfilled_scrape_queue)
            threads.append(thread)
            thread.start()
        return threads

    def emit(self, *args):
        self.parent.emit(*args)

    def request_feeds(self):
        for feed in self.config.feed_list():
            self.request(feed)

    def request(self, request):
        self.request_queue.put(request, block=False)

    def grab_feed_result(self):
        return self.poll(self.fulfilled_feed_queue)

    def grab_scrape_result(self):
        return self.poll(self.fulfilled_scrape_queue)

    @staticmethod
    def poll(q):
        """
        Called poll instead of dequeue because of possible confusion with double-ended queue
        :param q: A Queue
        :return: Next member of the queue, or None if the queue is empty
        """
        try:
            result = q.get(block=False)
            return result
        except Empty:
            return None

    def item(self, feed_name, index):
        feeds = self.config.feeds()
        if feed_name and feed_name in feeds:
            feed = feeds[feed_name]
            if feed.items and 0 <= index < len(feed.items):
                return feed.items[index]
        else:
            return None

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
        description = re.sub(r'\&\#8230\;', '…', description)

        return re.sub(r'<.*?>', '', description)


class GathererWorkerThread(Thread):
    def __init__(self, parent, cache, request_queue, fulfilled_feed_queue, fulfilled_scrape_queue):
        super().__init__(target=self.serve_requests)
        self.parent = parent
        self.cache = cache
        self.request_queue = request_queue
        self.fulfilled_feed_queue = fulfilled_feed_queue
        self.fulfilled_scrape_queue = fulfilled_scrape_queue
        self.session = requests.Session()
        self.daemon = True

    def notify_main_thread(self, signal):
        Gdk.threads_enter()
        self.parent.emit(signal)
        Gdk.threads_leave()

    def serve_requests(self):
        while True:
            request = self.request_queue.get(block=True)
            request_type = type(request)

            if request_type == Feed:
                feed = request
                self.gather_feed(feed)
                self.fulfilled_feed_queue.put(feed)
                self.notify_main_thread('feed_gathered_event')

            elif request_type == Item:
                item = request
                self.gather_item(item)
                self.fulfilled_scrape_queue.put(item)
                self.notify_main_thread('item_scraped_event')

            else:
                raise RuntimeError('Invalid request of type ' + str(request_type) + ' given to GathererWorkerThread' +
                                   ' the item was ' + str(request))

    def gather_item(self, item):
        if not item.article:
            hit = self.cache.query(item.link)
            if hit:
                item.article = hit
            else:
                article_html = self.session.get(item.link).content
                item.article = select_rule(item.link, article_html)
                self.cache.put(item.link, item.article)
        return item

    def gather_feed(self, feed):
        """ Given a feed, retrieves the items of the feed """
        content = utilityFunctions.feedparser_parse(feed.uri)
        items = list()
        if content:
            for entry in content['entries']:
                d = defaultdict(str, entry)

                description = d['description']
                if not description:
                    description = d['summary']
                title = d['title']
                link = d['link']

                if not title and not description and not link:
                    print('WARNING: An entry from the feed with label ' + feed.name +
                          ' has no title, description, or link. Skipped.' + str(entry))
                else:
                    item = Item(feed.name, title, Gatherer.description_cleanup(description), link)
                    items.append(item)

        feed.items = items
