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
from typing import Awaitable, Tuple, Union

import aiohttp
import feedparser
from aiohttp import ClientSession
from newspaper import fulltext

from feed import Feed
import gi
gi.require_version('Gdk', '3.0')
from gi.repository import Gdk, GLib
from item import Item
from newsStore import NewsStore


class Gatherer(Thread):
    def __init__(self, store: NewsStore):
        super().__init__(target=self.work_loop, daemon=True)
        self.loop = asyncio.new_event_loop()
        self.session = aiohttp.ClientSession(loop=self.loop)
        self.store = store
        self.start()

    def work_loop(self) -> None:
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()
        self.session.close()
        self.loop.close()

    def stop(self) -> None:
        self.loop.call_soon_threadsafe(self.loop.stop)

    def request(self, request: Union[Feed, Item]) -> None:
        asyncio.run_coroutine_threadsafe(self.serve_request(request, self.session), self.loop)

    def batch_requests(self, requests, session: ClientSession) -> Awaitable:
        return asyncio.gather(*[self.serve_request(r, session) for r in requests])

    async def serve_request(self, request, session: ClientSession) -> None:
        async with session.get(request.uri) as resp:
            response_text = await resp.text()
            await self.service(request, session, response_text)

    async def service(self, request: Union[Feed, Item], session: ClientSession, response_text: str) -> None:
        if isinstance(request, Feed):
            await self.service_feed(request, session, response_text)
        elif isinstance(request, Item):
            self.service_item(request, response_text)
        else:
            raise ValueError('Unknown request sent to Gatherer.')

    async def service_feed(self, feed: Feed, session: ClientSession, feed_xml: str) -> Awaitable:
        content = feedparser.parse(feed_xml)
        items = []
        for entry in content['entries']:
            items.append(
                Item(feed.name, entry['link'], entry['title']))
        return self.batch_requests(items, session)

    def service_item(self, item: Item, html: str) -> None:
        item.article = fulltext(html)
        Gdk.threads_add_idle(GLib.PRIORITY_DEFAULT_IDLE, self.main_thread_add_item_to_store, (self.store, item))

    @staticmethod
    def main_thread_add_item_to_store(arg_tuple: Tuple[NewsStore, Item]) -> bool:
        """ Needed due to GTK thread safety """
        store, item = arg_tuple
        store.append(item)
        return False  # Discard this event after we are done
