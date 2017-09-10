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

import asyncio
from threading import Thread

import aiohttp
from newspaper import fulltext

from feed import Feed
from item import Item
from utilityFunctions import feedparser_parse

class Gatherer(Thread):

    def __init__(self, parent):
        self.loop = asyncio.new_event_loop()
        self.session = aiohttp.ClientSession(loop=self.loop)
        self.parent = parent
        super().__init__(target=self.work_loop, daemon=True)
        super().start()

    def work_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()
        self.loop.close()

    def stop(self):
        self.loop.call_soon_threadsafe(self.loop.stop)

    def request(self, request):
        asyncio.run_coroutine_threadsafe(self.serve_request(request, self.session), self.loop)

    def batch_requests(self, requests, session):
        return asyncio.gather(*[self.serve_request(r, session) for r in requests])

    async def serve_request(self, request, session):
        async with session.get(request.uri) as resp:
            response_text = await resp.text()
            await self.service(request, session, response_text)

    async def service(self, request, session, response_text):
        if isinstance(request, Item):
            self.service_item(request, response_text)
        elif isinstance(request, Feed):
            await self.service_feed(request, session, response_text)
        else:
            raise ValueError('Unknown request sent to Gatherer.')

    def service_item(self, item, html):
        item.article = fulltext(html)
        self.parent.on_item_scraped(item)

    async def service_feed(self, feed, session, feed_xml):
        content = feedparser_parse(feed_xml)
        items = []
        for entry in content['entries']:
            items.append(
                    Item(feed.name, entry['link'], entry['title']))
        await self.batch_requests(items, session)

