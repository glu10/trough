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
import scraping
import re
try:
    import custom.custom_scraping as custom_scraping
    custom_there = len(custom_scraping.ordered_rules) > 0 # also probes attribute error
except (ImportError, AttributeError):
    custom_there = False

class ScrapeJob:
    """ Provides an API for scraping links. When multiple links need to be scraped for one job, detect cycles. """

    def __init__(self, session):
        self.visited = set()
        self.to_be_visited = deque()
        self.session = session

    def clear(self):
        self.visited.clear()
        self.to_be_visited.clear()

    def makes_cycle(self, link):
        return link in self.visited

    def add_link(self, link):
        """ Returns True when no cycle was detected, False otherwise. """
        if self.makes_cycle(link):
            print('Cycle in scrape job detected for the link ' + link + '. Abandoning the scrape job.')
            return False
        else:
            self.visited.add(link)
            self.to_be_visited.append(link)
            return True

    def add_links(self, *args):
        """ Convenience function """
        for arg in args:
            if not self.add_link(arg):
                return False
        return True

    def single_scrape(self, link=None, scraping_function=None):
        if link and self.makes_cycle(link):
            return ['Scrape job was abandoned due to cyclic links.']
        elif not link and self.to_be_visited:
            link = self.to_be_visited.popleft()
        else:
            raise RuntimeError('A scrape job was called with no link to scrape.')

        html = self.session.get(link, headers={'User-Agent': 'Mozilla/5.0'}).content
        soup = BeautifulSoup(html, 'html.parser')

        if scraping_function:
            return scraping_function(soup)

        result = None
        if custom_there:
            result = scraping.select_rule(link, soup, custom_scraping.ordered_rules, self)
        if not result:
            result = scraping.select_rule(link, soup, scraping.ordered_rules, self)

        return result

    def scrape_until_done(self, args):
        if args and not self.add_links(args):
            return ['Scrape job was abandoned due to cyclic links.']
        else:
            paragraphs = list()
            while self.to_be_visited:
                result = self.single_scrape()
                for p in result:
                    paragraphs.append(p)

            return paragraphs

