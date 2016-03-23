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
from item import Item
from feed import Feed
from collections import defaultdict
from scrapeJob import ScrapeJob
from cache import Cache
from ruleResolverFakeFeed import FakeFeedResolver
from ruleResolverScraping import WrappedScrapeResolver

# Threading imports
from threading import Thread
from queue import Queue, Empty
from gi.repository import Gdk


class Gatherer:
    """ Gatherer is a singleton responsible for handling network requests """

    def __init__(self, parent, preferences, cache):
        self.parent = parent
        self.preferences = preferences
        self.cache = cache
        self.request_queue = Queue()  # Can contain Feed Requests and Item (scraping) requests
        self.fulfilled_feed_queue = Queue()
        self.fulfilled_scrape_queue = Queue()
        self.threads = self.create_and_start_threads(2)

    def create_and_start_threads(self, num_threads):
        threads = list()
        scrape_resolver = WrappedScrapeResolver()
        fake_feed_resolver = FakeFeedResolver('custom.fake_feeds')
        for i in range(num_threads):
            thread = GathererWorkerThread(self, self.cache, scrape_resolver, fake_feed_resolver,
                                          self.request_queue, self.fulfilled_feed_queue, self.fulfilled_scrape_queue)
            threads.append(thread)
            thread.start()
        return threads

    def emit(self, *args):
        self.parent.emit(*args)

    def request_feeds(self):
        for feed in self.preferences.feed_list():
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
        feeds = self.preferences.feeds()
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
        description = re.sub(r'<.*?>', '', description)

        return description


class GathererWorkerThread(Thread):
    def __init__(self, parent, cache, scrape_resolver, fake_feed_resolver,
                 request_queue, fulfilled_feed_queue, fulfilled_scrape_queue):
        super().__init__(target=self.serve_requests)
        self.parent = parent
        self.cache = cache
        self.scrape_resolver = scrape_resolver
        self.fake_feed_resolver = fake_feed_resolver
        self.request_queue = request_queue
        self.fulfilled_feed_queue = fulfilled_feed_queue
        self.fulfilled_scrape_queue = fulfilled_scrape_queue
        self.session = requests.Session()
        self.scrape_job = ScrapeJob(self.session, self.scrape_resolver)
        self.daemon = True

    def notify_main_thread(self, signal):
        Gdk.threads_enter()
        self.parent.emit(signal)
        Gdk.threads_leave()

    def _fresh_scrape_job(self):
        self.scrape_job.clear()
        return self.scrape_job

    def serve_requests(self):
        while True:
            request = self.request_queue.get(block=True)

            if request.lock.acquire(blocking=False):  # Can't use the cleaner "with lock:" syntax due to non-blocking

                try:
                    request_type = type(request)

                    if request_type == Feed:
                        feed = request
                        if feed.is_fake():
                            self.gather_fake_feed(feed)
                        else:
                            self.gather_feed(feed)

                        if feed.items:
                            # Checks the cache for any item link before handing the feed over
                            for item in feed.items:
                                hit = self.cache.query(item.link)
                                if hit:
                                    item.article = hit

                            self.fulfilled_feed_queue.put(feed)
                            self.notify_main_thread('feed_gathered_event')

                    elif request_type == Item:
                        item = request
                        if not item.article and item.link:
                            self.gather_item(item)
                            if item.article:
                                self.fulfilled_scrape_queue.put(item)
                                self.notify_main_thread('item_scraped_event')

                    else:
                        raise RuntimeError('Invalid request of type ' + str(request_type) +
                                           ' given to GathererWorkerThread the item was ' + str(request))
                finally:
                    request.lock.release()

    def gather_item(self, item):
        hit = self.cache.query(item.link)
        if hit:
            item.article = hit
        else:
            item.article = self.scrape_resolver.select_rule(item.link, self._fresh_scrape_job())
            self.cache.put(item.link, item.article)
        return item

    def gather_fake_feed(self, feed):
        feed.items = self.fake_feed_resolver.select_rule(feed.name, self._fresh_scrape_job())

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
