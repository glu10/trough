import unittest
from unittest.mock import MagicMock
from unittest.mock import patch
import gi
gi.require_version('Gtk', '3.0')  # Silences warning
from twoPaneView import TwoPaneView
from threePaneView import ThreePaneView
from preferences import Preferences
from feed import Feed
from item import Item

# NOTE: These tests were made pre-category support, some tests may break once the TreeView is altered for that.
# TODO: Once feed category support is added, look into whether adding a Base test class would be clean.


class CommonViewSetup:

    @staticmethod
    def make_feeds():
        feeds = [
                 Feed('name here', 'uri here'),
                 Feed('different name here', 'different uri here'),
                 Feed('fake feed with a blank uri', ''),
                ]

        for feed in feeds:
            CommonViewSetup.make_items_for_feed(feed)

        return feeds

    @staticmethod
    def names_to_feed_dict(feed_list):
        d = dict()
        for feed in feed_list:
            d[feed.name] = feed
        return d

    @staticmethod
    def make_items_for_feed(feed):
        name = feed.name
        feed.items = [
                      Item(name, title='just a title'),
                      Item(name, description='just a description'),
                      Item(name, title='title', description='description'),
                      Item(name, title='title 2', description='description 2', link='link'),
                      Item(name, link='link')
                     ]

    @staticmethod
    def mock_gatherer(feed_dict):
        def fake_item_getter(feed_name, index):  # Simulates retrieving an item from active current feeds
            return feed_dict[feed_name].items[index]

        def fake_feed_getter(feed_name):
            return feed_dict[feed_name]

        gatherer = MagicMock()
        gatherer.item = MagicMock(side_effect=fake_item_getter)
        gatherer.get_feed = MagicMock(side_effect=fake_feed_getter)

        return gatherer


class TestTwoPaneView(unittest.TestCase):

    def setUp(self):
        self.feeds = CommonViewSetup.make_feeds()
        feed_dict = CommonViewSetup.names_to_feed_dict(self.feeds)
        self.gatherer = CommonViewSetup.mock_gatherer(feed_dict)
        preferences = MagicMock()
        preferences.appearance_preferences.return_value = Preferences.default_appearance_preferences()
        self.view = TwoPaneView(preferences, self.gatherer)

    def test_refresh(self):
        self.view.refresh()
        self.assertEqual(-1, self.view.last_item_index)
        self.assertIsNone(self.view.last_item_feed_name)
        self.assertTrue(self.gatherer.request_feeds.called)

    def test_receive_feed(self):
        feed = self.feeds[0]
        self.assertEqual(0, len(self.view.received_feeds))
        self.view.receive_feed(feed)
        self.assertEqual(1, len(self.view.received_feeds))
        for i, item in enumerate(feed.items):
            self.assertEqual(feed.name, self.view.headline_store[i][0])
            self.assertEqual(item.title, self.view.headline_store[i][1])
            self.assertEqual(i, self.view.headline_store[i][2])

    def test_populate(self):
        self.view.populate(self.feeds)
        self.assertEqual(len(self.view.received_feeds), len(self.feeds))
        item_count = sum(len(feed.items) for feed in self.feeds)
        self.assertEqual(item_count, len(self.view.headline_store))

    def test_clear_headlines(self):

        view = self.view  # just for readability
        view.populate(self.feeds)
        m = MagicMock()

        with patch('twoPaneView.TwoPaneView.show_new_content', m):
            view.clear_store(view.headline_store, view.toggle_headline_listening)
            # This was a problem that had to be mitigated, a clear should NOT be throwing signals causing this call
            self.assertFalse(m.called)

    def test_text_containing_widgets(self):
        self.assertEqual(2, len(self.view.text_containing_widgets()))

    def test_show_content(self):
        feed = self.feeds[0]
        target_item = feed.items[0]
        self.view.receive_feed(feed)

        # Case where an item article is present, the content should be prepared
        target_item.article = ['article']
        m = MagicMock()
        with patch('textFormat.TextFormat.prepare_content_display', m):
            self.view.headline_view.set_cursor(0)
            m.assert_called_with(target_item, self.view.content_view)

    def test_missing_content(self):
        feed = self.feeds[0]
        target_item = feed.items[0]
        self.view.receive_feed(feed)

        # Case where no item article present, the content should be requested
        target_item.article = None
        self.view.headline_view.set_cursor(0)
        self.gatherer.request.assert_called_with(target_item)


class TestThreePaneView(unittest.TestCase):

    def setUp(self):
        self.feeds = CommonViewSetup.make_feeds()
        feed_dict = CommonViewSetup.names_to_feed_dict(self.feeds)
        self.gatherer = CommonViewSetup.mock_gatherer(feed_dict)
        preferences = MagicMock()
        preferences.appearance_preferences.return_value = Preferences.default_appearance_preferences()
        self.view = ThreePaneView(preferences, self.gatherer)

    def test_receive_feed(self):
        feed = self.feeds[0]
        self.assertEqual(0, len(self.view.received_feeds))
        self.view.receive_feed(feed)
        self.assertEqual(1, len(self.view.received_feeds))
        self.assertEqual(feed.name, self.view.label_store[0][0])

    def test_populate(self):
        self.view.populate(self.feeds)
        for i, feed in enumerate(self.feeds):
            self.assertEqual(feed.name, self.view.label_store[i][0])

    def test_show_headlines(self):
        self.view.populate(self.feeds)
        for i, feed in enumerate(self.feeds):
            self.assertEqual(feed.name, self.view.label_store[i][0])
            self.view.preferences = self.gatherer  # mocks getting the feed by name
            self.view.label_view.set_cursor(i)
            self.assertEqual(len(self.view.headline_store), len(feed.items))
            for j, item in enumerate(feed.items):
                self.assertEqual(item.title, self.view.headline_store[j][0])

    def test_clear_labels(self):
        view = self.view
        view.populate(self.feeds)
        m = MagicMock()

        with patch('threePaneView.ThreePaneView.show_new_headlines', m):
            view.clear_store(view.label_store, view.toggle_label_listening)
            # This was a problem that had to be mitigated, a clear should NOT be throwing signals causing this call
            self.assertFalse(m.called)

    def test_show_content(self):
        feed = self.feeds[0]
        target_item = feed.items[0]
        self.view.receive_feed(feed)
        self.view.preferences = self.gatherer  # mocks getting the feed by name

        # Case where an item article is present, the content should be prepared
        target_item.article = ['article']
        m = MagicMock()
        with patch('textFormat.TextFormat.prepare_content_display', m):
            self.view.label_view.set_cursor(0)
            self.view.headline_view.set_cursor(0)
            m.assert_called_with(target_item, self.view.content_view)

    def test_missing_content(self):
        feed = self.feeds[0]
        target_item = feed.items[0]
        self.view.receive_feed(feed)
        self.view.preferences = self.gatherer  # mocks getting the feed by name

        # Case where no item article present, the content should be requested
        target_item.article = None
        self.view.label_view.set_cursor(0)
        self.view.headline_view.set_cursor(0)
        self.gatherer.request.assert_called_with(target_item)

    def test_text_containing_widgets(self):
        self.assertEqual(3, len(self.view.text_containing_widgets()))



























