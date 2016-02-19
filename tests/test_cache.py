import unittest
from unittest import mock
from unittest.mock import call, patch

import gi
gi.require_version('Gtk', '3.0')  # Silences warning
from cache import Cache
import builtins
import utilityFunctions
import os


class TestCache(unittest.TestCase):
    def setUp(self):
        self.cache = Cache()

    def tearDown(self):
        self.cache = None

    def test_put(self):
        self.assertIsNone(self.cache.put(None, 'item'))

        with self.assertRaises(AssertionError):
            self.cache.put('identifier', None)

        self.assertFalse(self.cache.cache)

        self.assertIsNone(self.cache.put('identifier', 'string'))
        self.assertIsNone(self.cache.put('identifier', list()))

    def test_query(self):
        self.assertIsNone(self.cache.query('Never inserted'))

    @patch('utilityFunctions.ensure_directory_exists', mock.Mock())
    @patch('builtins.open', mock.mock_open(read_data='{\"identifier\":\"value\"}'))
    def test_load_cache(self):
            self.cache.load_cache()
            self.assertEquals(self.cache.query('identifier'), 'value')

    @patch('utilityFunctions.ensure_directory_exists', mock.Mock())
    def test_write_cache(self):
        self.cache.put('identifier', 'value')

        m = mock.mock_open()
        with patch('builtins.open', m):
            self.cache.write_cache()

        m.assert_called_once_with(os.path.join(self.cache.cache_directory, self.cache.cache_file), 'w')

        # JSON dump splits the write calls apparently, this is the cleanest way to verify the ordering
        expected = [call('{'),
                    call('\"identifier\"'),
                    call(': '),
                    call('\"value\"'),
                    call('}'),
                    ]

        self.assertEquals(m().write.call_args_list, expected)

    def test_put_then_query(self):
        self.cache.put('identifier', 'string')
        self.assertEquals(self.cache.query('identifier'), 'string')

        self.cache.put('identifier', 'overwritten')
        self.assertEquals(self.cache.query('identifier'), 'overwritten')

        t = list()
        self.cache.put('listgoeshere', t)
        self.assertEquals(self.cache.query('listgoeshere'), t)
