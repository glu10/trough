import unittest
from feed import Feed


class TestFeed(unittest.TestCase):

    def setUp(self):
        self.feed = Feed('name_here', 'uri_here')

    def tearDown(self):
        self.feed = None

    def test_lock(self):
        self.assertIsNotNone(self.feed.lock)
        self.feed.lock.acquire(blocking=False)
        self.feed.lock.release()

    def test_from_dict(self):
        example_name = 'Name here'
        example_uri = 'URI here'

        attribute_dict = {'name': example_name, 'uri': example_uri}
        f = Feed.from_dict(attribute_dict)
        self.assertEquals(f.name, example_name)
        self.assertEquals(f.uri, example_uri)

        # Unsupported attributes should just be ignored
        invalid = 'invalid'
        attribute_dict[invalid] = 'better not show up'
        f = Feed.from_dict(attribute_dict)
        with self.assertRaises(AttributeError):
            f.invalid
        attribute_dict.pop(invalid)

        # Missing attributes should trigger an error
        attribute_dict.pop('name')
        with self.assertRaises(RuntimeError):
            Feed.from_dict(attribute_dict)

    def test_to_dict(self):
        d = self.feed.to_dict()

        self.assertEquals(d['name'], self.feed.name)
        self.assertEquals(d['uri'], self.feed.uri)
        # The items attribute should not be written out
        with self.assertRaises(KeyError):
            d['items']








