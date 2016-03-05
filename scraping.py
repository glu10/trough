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
import re
from bs4 import BeautifulSoup
"""
This file contains scraping rules for fetching information that is linked to in an RSS feed.

These rules are not an all-encompassing list. There are too many possible sites to scrape, and the temporary nature of
most web designs ensures that even these provided rules will break eventually. Due to this, you shouldn't be surprised
if scraped information isn't perfect.

A heuristic is used for sites that do not have an explicit rule.

It is planned to provide functionality that allows a user to add to or modify these base rules.
"""


def select_rule(link, soup, given_rules, job):
    for rule in given_rules:
        identifier = rule[0]
        scrape_rule = rule[1]
        if re.search(identifier, link):
            try:
                return cleanup(scrape_rule(soup, job))
            except AttributeError:  # A rule couldn't find what it assumed would be there
                print('NOTICE: The link', link, 'matched with ' + identifier +
                      ', but the scraping rule returned None. Using the default scraping rule as a fallback.')
                return unknown_source(soup)

    return unknown_source(soup)


def unknown_source(soup):
        """ Making a best guess as to where the article is contained """
        paragraphs = cleanup(soup.find_all('p'))

        # Only keeps paragraphs past a certain threshold length
        filtered_paragraphs = [p for p in paragraphs if len(p) >= 20]  # TODO: Configuration for this threshold

        if filtered_paragraphs:
            return filtered_paragraphs
        elif paragraphs:
            return paragraphs
        else:
            return ['No paragraphs could be found.']


def cleanup(paragraphs):
    cleaned = list()
    for p in paragraphs:

        if type(p) != str:
            p = p.getText()

        # Remove extraneous whitespace
        p = re.sub(r'\s+', ' ', p)
        p = re.sub(r'\n\n(\n+)', '\n\n', p)
        # Remove any leftovers from HTML
        p = re.sub(r'<.*?>', '', p)

        # Remove small annoyances
        temp = p.lower()
        if temp.find('hide caption') != -1 or temp == 'advertisement' or temp.startswith('see more'):
            continue
        else:
            cleaned.append(p)
    return cleaned


def abc_news(soup, job):
    return soup.findAll('p', {'itemprop': 'articleBody'})


def bloomberg(soup, job):
    return soup.find('div', {'class': 'article-body__content'}).findAll('p')


def cnn(soup, job):
    result = soup.findAll('p', 'zn-body__paragraph')
    # Fixing a problem where introductory (CNN) does not have a space after it, or has an unnecessary one before it.
    for i, p in enumerate(result):
        result[i] = p.getText()
        if re.search(r'\(CNN\)', result[i]):
            result[i] = re.sub(r'^ \(CNN\)', '(CNN)', result[i])
            result[i] = re.sub(r'\(CNN\)', '(CNN) ', result[i])
            break

    return result


def fox_news(soup, job):
    return soup.find('article').findAll('p')


def huffington_post(soup, job):
    return soup.find('div', {'class': 'entry-component__content'}).findAll('p')


def nbc_news(soup, job):
    return soup.find('div', {'class': 'article-body'}).findAll('p')


def new_york_times(soup, job):
    return soup.find('article', {'id': 'story'}).findAll('p')


def npr(soup, job):
    return soup.find('div', {'id': 'storytext'}).find_all('p')


def reuters(soup, job):
    return soup.find('span', {'id': 'articleText'}).findAll('p')


def time(soup, job):
    return soup.find('div', {'class': 'readingpane'}).findAll('p')


def usa_today(soup, job):
    return soup.find('div', {'itemprop': 'articleBody'}).findAll('p')


def washington_post(soup, job):
    return soup.find('article', {'itemprop': 'articleBody'}).findAll('p')


rules = {r'abcnews.go.com': abc_news,
         r'bloomberg.com': bloomberg,
         r'cnn.com': cnn,
         r'foxnews.com': fox_news,
         r'huffingtonpost.com': huffington_post,
         r'nbcnews.com': nbc_news,
         r'nytimes.com': new_york_times,
         r'npr.org': npr,
         r'reuters.com': reuters,
         r'time.com': time,
         r'usatoday.com': usa_today,
         r'washingtonpost.com': washington_post,
         }

ordered_rules = sorted(rules.items(), key=lambda x: len(x[0]))
