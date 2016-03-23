import unittest
import gi
gi.require_version('Gtk', '3.0')
from bs4 import BeautifulSoup
from item import Item


class TestItem(unittest.TestCase):

    def test_from_href(self):
        url = 'url'
        text = 'text'
        feed_name = 'feed name here'
        href_html = '<html><a href="' + url + '">' + text + '</a></html>'
        soup = BeautifulSoup(href_html, 'html.parser')
        item = Item.from_href(feed_name, soup.find('a', href=True))

        self.assertEquals(url, item.link)
        self.assertEquals(feed_name, item.label)
        self.assertEquals(text, item.title)

