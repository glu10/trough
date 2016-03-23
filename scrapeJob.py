"""
    Trough - a GTK+ RSS news reader

    Copyright (C) 2016 Andrew Asp
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

from collections import deque
from bs4 import BeautifulSoup


def check_link_for_cycle(func):
        def wrapper(self, link):
            assert(type(link) == str)
            if self._add_link(link):
                return func(self, link)
            else:
                raise RuntimeError('Link cycle detected on ' + link + ' Abandoning the scrape job.')
        return wrapper


class ScrapeJob:
    """ Provides an API for requesting links for the resolution of a singular rule resolution job.
        When multiple links need to be scraped for one job, detect cycles. """

    def __init__(self, session, resolver):
        self.visited = set()
        self.to_be_visited = deque()
        self.session = session
        self.resolver = resolver

    def clear(self):
        self.visited.clear()
        self.to_be_visited.clear()

    def makes_cycle(self, link):
        return link in self.visited

    def _add_link(self, link):
        """ Returns True when no cycle was detected, False otherwise. """
        if self.makes_cycle(link):
            return False
        else:
            self.visited.add(link)
            self.to_be_visited.append(link)
            return True

    @check_link_for_cycle
    def get_soup(self, link):
        user_agent = 'Mozilla/5.0 (X11; Linux x86_64; rv:45.0) Gecko/20100101 Firefox/45.0'
        html = self.session.get(link, headers={'User-Agent': user_agent}).content
        return BeautifulSoup(html, 'html.parser')

    def get_contents(self, link):
        return self.resolver.select_rule(link, self)

