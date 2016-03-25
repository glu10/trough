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

In this file I try to create useful rules that display various levels of complexity.
"""

# Import logic for both locations this file could be in. In reality the custom folder should be the only location
# this code is ever executed from, but having a missing import in an example seems like poor form.
from item import Item


def hrefs_to_items(feed_name, href_list):
    """ Convenience function, takes a list of hrefs and returns a list of Items """
    return [Item.from_href(feed_name, href) for href in href_list]

def youtube_mashup(label, job):
    """ I don't advise using this, BeautifulSoup + html.parser makes youtube HTML parsing slow """

    # Take the latest 3 videos from different channels
    num_vids_each = 3
    video_items = list()

    channels = ['testedcom', 'theneedledrop']  # last one is colbert
    for channel in channels:
        url = 'http://youtube.com/user/' + channel + '/videos'
        soup = job.get_soup(url)
        divs = soup.find_all('div', 'yt-lockup-video')[:num_vids_each]
        for div in divs:
            video_id = div.get('data-context-item-id')
            video_url = 'http://www.youtube.com/watch?v=' + video_id
            video_title = div.find('a', 'yt-uix-tile-link').get_text()
            video_upload = div.find("ul", "yt-lockup-meta-info").contents[1].get_text()
            video_items.append(Item(label, video_title, video_upload, video_url))

    return video_items


def hacker_news_stories(label, job):
    """ Items are the linked articles from the front page """
    items = list()
    soup = job.get_soup('https://news.ycombinator.com/')
    titles = soup.find('table', {'class': 'itemlist'}).findAll('td', {'class': 'title'})
    for title in titles[:-1]:
        a = title.find('a', href=True)
        if a:
            items.append(Item(label, a.get_text(), '', a['href']))
    return items


def hacker_news_comment_pages(label, job):
    """ Items are the comment pages for each link on the front page """
    items = list()
    base = 'https://news.ycombinator.com/'
    soup = job.get_soup(base)
    athings = soup.find('table', {'class': 'itemlist'}).findAll('tr', {'class': 'athing'})
    for athing in athings:
        ta = athing.find('td', {'class': 'title'}).next_sibling.next_sibling.next_sibling.find('a', href=True)
        ca = athing.next_sibling.find('td', {'class': 'subtext'}).find('span', {'class': 'age'}).find('a', href=True)
        if ta and ca:
            items.append(Item(label, ta.get_text(), '', base + ca['href']))
    return items

rules = {
          'HN': hacker_news_stories,
          'YTM': youtube_mashup,
          'HNC': hacker_news_comment_pages,
        }

