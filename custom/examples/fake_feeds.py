"""
This file is an example of how to write a fake feeds file.

Fake feeds are an answer to situations where an RSS feed isn't provided, but you wish there was. This is achieved by
scraping titled links, which will act as the items of the faked RSS feed. Note that the goal of the rules within this
file is NOT to scrape content (e.g. news articles), instead the goal is to scrape links that link TO content
(e.g. the links on a main page for articles of interest). Content scraping is done later by scraping rules.

Having custom rules be in a non-provided file prevents updates to Trough from erasing your hard work. Feel free to
copy this file one directory above (to the custom folder) to have these examples be the basis for your own rules.

A fake feeds file NEEDS:
    To be named fake_feeds.py
    To be in the trough/custom folder
    A dictionary named rules, at the top level.
        -   The dictionary's keys are strings
        -   The dictionary's values are functions that accept one argument and return a list of Items

Further Explanation:
    Each key in the dictionary is a string that represents the name of the feed. Examples: 'HN', 'Coolest fake feed'

    Each value of the dictionary is a function that accepts one argument, which is a ScrapeJob. A ScrapeJob is a part of
    Trough, and lets you ask for the soup of links. You can use requests directly if you'd prefer, but it is not
    advisable since a ScrapeJob protects you from cyclic links. Cyclic links are really bad if left unhandled, they
    happen when you follow links to get more links and accidentally get caught in an infinite loop.

If you feel as if you don't completely understand, don't worry. Look over this file and the pattern should become clear.
If the scraping logic is confusing you, the Beautiful Soup documentation is a great resource and is located
here: http://www.crummy.com/software/BeautifulSoup/bs4/doc/

Have fun! In this file I try to create useful rules that display various levels of complexity.
"""
from ..item import Item


def hrefs_to_items(feed_name, href_list):
    """ Convenience function, takes a list of hrefs and returns a list of Items """
    return [Item.from_href(feed_name, href) for href in href_list]


