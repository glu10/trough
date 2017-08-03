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

from collections import defaultdict
from threading import Thread
from queue import LifoQueue, Empty

import aiohttp
import asyncio
import async_timeout

from gi.repository import Gdk
from newspaper import fulltext

from feed import Feed
from item import Item
import utilityFunctions

class Gatherer:
    def __init__(self, parent):
        self.q = LifoQueue()
        self.loop = asyncio.get_event_loop()

    def start(self):
        self.loop.run_until_complete(self.serve_requests())

    def request(self, request):
        print("Putting ", request)
        self.q.put_nowait(request)

    async def serve_requests(self):
        async with aiohttp.ClientSession() as session:
            print("Got session", session)
            req = self.q.get()
            # TODO: Differentiate feed requests/item requests
            print("Got out of queue with", req)
            async with session.get(req.uri) as resp:
                if isinstance(req, Item):
                    html = await resp.text()
                    req.article = fulltext(html)
                    self.parent.on_item_scraped(req)
                else:
                    feed_xml = await resp.text()
                    content = utilityFunctions.feedparser_parse(feed_xml)
                    for entry in content['entries']:
                        self.request(Item(req.name, d['title'], d['summary'], d['link']))
                    
    def stop(self):
        self.loop.stop()

