import asyncio
import time
import unittest

from unittest.mock import MagicMock

from gatherer import Gatherer
from item import Item
from feed import Feed

class TestGatherer(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.loop = asyncio.new_event_loop()
        cls.mock_parent = MagicMock()
        cls.mock_parent.on_item_scraped = MagicMock()
        cls.gatherer = Gatherer(cls.mock_parent)

    @classmethod
    def tearDownClass(cls):
        cls.gatherer.stop()

    def test_request_item(self):
        test_uri = 'http://money.cnn.com/2017/09/10/news/companies/disney-world-closing/index.html'
        item = Item('', test_uri)
        self.gatherer.request(item)
        while not self.mock_parent.on_item_scraped.called:
            print('Item Sleeping')
            time.sleep(1)

    def test_request_feed(self):
        feed = Feed('test', 'http://rss.cnn.com/rss/cnn_topstories.rss')
        self.gatherer.request(feed)
        while not self.mock_parent.on_item_scraped.called:
            print('Feed Sleeping')
            time.sleep(1)
