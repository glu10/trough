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

"""
This file contains scraping rules for fetching information that is linked to in an RSS feed.

These rules are not an all-encompassing list. There are too many possible sites to scrape, and the temporary nature of
most web designs ensures that even these provided rules will break eventually. Due to this, you shouldn't be surprised
if scraped information isn't perfect.

A heuristic is used for sites that do not have an explicit rule. To see it, see ruleResolverScraping.py

Parameters:
    soup - a BeautifulSoup
    job - a ScrapeJob, used to issue requests for more pages to scrape, if needed (usually not).
"""


def abc_news(soup, job):
    return soup.find_all('p', {'itemprop': 'articleBody'})


def bloomberg(soup, job):
    return soup.find('div', {'class': 'article-body__content'}).find_all('p')


def cnn(soup, job):
    result = soup.find_all('p', 'zn-body__paragraph')
    # Fixing a problem where introductory (CNN) does not have a space after it, or has an unnecessary one before it.
    for i, p in enumerate(result):
        result[i] = p.getText()
        if re.search(r'\(CNN\)', result[i]):
            result[i] = re.sub(r'^ \(CNN\)', '(CNN)', result[i])
            result[i] = re.sub(r'\(CNN\)', '(CNN) ', result[i])
            break
    return result


def fox_news(soup, job):
    return soup.find('article').find_all('p')


def huffington_post(soup, job):
    return soup.find('div', {'class': 'entry-component__content'}).find_all('p')


def nbc_news(soup, job):
    return soup.find('div', {'class': 'article-body'}).find_all('p')


def new_york_times(soup, job):
    return soup.find('article', {'id': 'story'}).find_all('p')


def npr(soup, job):
    return soup.find('div', {'id': 'storytext'}).find_all('p')


def reuters(soup, job):
    return soup.find('span', {'id': 'articleText'}).find_all('p')


def time(soup, job):
    return soup.find('div', {'class': 'readingpane'}).find_all('p')


def usa_today(soup, job):
    return soup.find('div', {'itemprop': 'articleBody'}).find_all('p')


def washington_post(soup, job):
    return soup.find('article', {'itemprop': 'articleBody'}).find_all('p')


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

ordered_rules = sorted(rules.items(), key=lambda x: len(x[0]))  # The object required by a RuleResolver
