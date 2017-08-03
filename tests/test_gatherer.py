import unittest

import asyncio
from gatherer import Gatherer

class TestGatherer(unittest.TestCase):

    def setUp(self):
        loop = asyncio.new_event_loop()
        self.gatherer = Gatherer(None)
        self.test_uri = None # Used to paste in representative test URIs

    def tearDown(self):
        self.gatherer.stop()
    
    def test_request_url(self):
        self.gatherer.request(self.test_uri)
        self.gatherer.start()
        
        
