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

    The full project can be found at: https://github.com/glu10/trough
"""

from bs4 import BeautifulSoup
import re

"""
This file contains scraping rules for fetching information that is linked to in an RSS feed.

These rules are not an all-encompassing list. There are too many possible sites to scrape, and the temporary nature of
most web designs ensures that even these provided rules will break eventually. Due to this, you shouldn't be surprised
if scraped information isn't perfect.

A heuristic is used for sites that do not have an explicit rule.

It is planned to provide functionality that allows a user to add to or modify these base rules.
"""

def select_rule(link, html):
    soup = BeautifulSoup(html, 'html.parser')

    for identifier, scrape_rule in rules.items():  # see bottom of file for rules dictionary
        if identifier in link:
            return cleanup(scrape_rule(soup))

    return unknown_source(soup)

def unknown_source(soup):
        """ Making a best guess as to where the article is contained """
        paragraphs = cleanup(soup.find_all('p'))

        # Only keep paragraphs past a certain threshold length
        return [p for p in paragraphs if len(p) >= 20]  # TODO: Configuration for this threshold

def cleanup(paragraphs):

    cleaned = list()
    for p in paragraphs:
        p = p.getText()

        # Remove extraneous whitespace
        p = re.sub(r'\s+', ' ', p)
        p = re.sub(r'\n\n(\n+)', '\n\n', p)
        # Remove any leftovers from HTML
        p = re.sub(r'<.*?>', '', p)

        cleaned.append(p)

    return cleaned

def abc_news(soup):
    return soup.findAll('p', {'itemprop':'articleBody'})

def bloomberg(soup):
    return soup.find('div', {'class': 'article-body__content'}).findAll('p')

def cnn(soup):
    return soup.findAll('p', 'zn-body__paragraph')

def fox_news(soup):
    return soup.find('article').findAll('p')

def huffington_post(soup):
    return soup.find('div', {'class': 'entry-component__content'}).findAll('p')

def nbc_news(soup):
    return soup.find('div', {'class': 'article-body'}).findAll('p')

def new_york_times(soup):
    return soup.find('article', {'id': 'story'}).findAll('p')

def npr(soup):
    return soup.find('div', {'id': 'storytext'}).find_all('p')

def reuters(soup):
    return soup.find('span', {'id': 'articleText'}).findAll('p')

def usa_today(soup):
    return soup.find('div', {'itemprop': 'articleBody'}).findAll('p')

def washington_post(soup):
    return soup.find('article', {'itemprop': 'articleBody'}).findAll('p')

rules = {'abcnews.go.com': abc_news,
         'bloomberg.com': bloomberg,
         'cnn.com': cnn,
         'foxnews.com': fox_news,
         'huffingtonpost.com': huffington_post,
         'nbcnews.com': nbc_news,
         'nytimes.com': new_york_times,
         'npr.org': npr,
         'reuters.com': reuters,
         'usatoday.com': usa_today,
         'washingtonpost.com': washington_post
         }






