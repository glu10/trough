"""
    Trough - a GTK+ RSS news reader

    Copyright (C) 2017 Andrew Asp
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

from unittest import TestCase

from feed import Feed


class TestFeed(TestCase):

    def setUp(self):
        self.test_uri = 'http://127.0.0.1:8080'
        self.test_name = 'test name'

    def test_dict_serialization(self):
        feed = Feed(self.test_name, self.test_uri)
        feed_dict = feed.to_dict()
        expected = {'name': self.test_name, 'uri': self.test_uri}
        self.assertEqual(feed_dict, expected)

        from_feed = Feed.from_dict(feed_dict)
        self.assertEqual(from_feed, feed)
        self.assertEqual(feed_dict, from_feed.to_dict())

    def test_failing_from_dict(self):
        unknown_key_dict = {
                'name': self.test_name,
                'uri': self.test_uri,
                'unknown_key': '_',
        }
        self.assertRaises(TypeError, Feed.from_dict, unknown_key_dict)

        missing_keys_dict = {}
        self.assertRaises(TypeError, Feed.from_dict, missing_keys_dict)

    def test_equality(self):
        name_1 = 'name1'
        name_2 = 'name2'
        uri_1 = 'uri1'
        uri_2 = 'uri2'

        self.assertNotEqual(name_1, name_2)
        self.assertNotEqual(uri_1, uri_2)

        same_name_feed = Feed(name_1, uri_1)
        same_name_feed_2 = Feed(same_name_feed.name, uri_2)
        self.assertEqual(same_name_feed, same_name_feed_2)

        diff_name_feed = Feed(name_2, uri_1)
        self.assertNotEqual(same_name_feed, diff_name_feed)
        self.assertNotEqual(same_name_feed, None)

    def test_value_list(self):
        expected = [self.test_name, self.test_uri]
        actual = Feed(self.test_name, self.test_uri).to_value_list()
        self.assertEqual(expected, actual)
