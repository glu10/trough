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

from typing import Optional, Union

from aiohttp import ClientSession

from feed import Feed
from item import Item
from newsStore import NewsStore


class StubGatherer:
    """
    Avoids network requests during development.
    """

    def __init__(self, store: NewsStore):
        self.store = store
        lorem = self.__lorem()

        description = lorem.split('\n\n', maxsplit=1)[0]

        self.stub_item = \
            Item(
                'Lorem Feed Dolor',
                'http://127.0.0.1',
                'Lorem Title Dolor',
                description,
                lorem,
            )

    def __lorem(self) -> str:
        with open('tests/resources/lorem', 'r') as f:
            return f.read()

    def work_loop(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def request(self, request: Union[Feed, Item]) -> None:
        self.service_item(None, None)

    def batch_requests(self, requests, session):
        pass

    async def serve_request(self, request: Union[Feed, Item], session: ClientSession) -> None:
        self.service_item(None, None)

    async def service(self, request: Union[Feed, Item], session: ClientSession, response_text: str) -> None:
        pass

    def service_item(self, item: Optional[Item], html: Optional[str]) -> None:
        self.store.append(self.stub_item)

    async def service_feed(self, feed: Feed, session: ClientSession, feed_xml: str) -> None:
        self.service_item(None, None)
