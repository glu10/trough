"""
This file is an example of how to write a custom scraping rules file. A custom scraping rules file correlates URIs to
their respective content scraping logic. When an item of an RSS feed is clicked, the URI of that item is checked for a
match to figure out how to scrape it. Note that this scraping only provides content, not the RSS title/description.
For scraping custom RSS titles/descriptions, see the fake_feeds file.

Having custom rules be in a non-provided file prevents updates to Trough from erasing your hard work. Feel free to
copy this file one directory above (to the custom folder) to have these examples be the basis for your own rules.

A custom scraping rules file NEEDS:
    To be named custom_scraping_rules.py
    To be in the trough/custom folder
    A list of lists named ordered_rules, at the top level.
        -   Each sub-list represents a singular rule, and is of length 2. A rule needs two things: a way to match to it,
            and knowledge of what to do when you match with it. To achieve this, each sub-list looks like this:
            [a raw string (representing a regular expression), a function]
        -   Each function contained within a sub-list should accept two arguments and return a list of strings
            or HTML elements containing text, like from findAll('p').

Further Explanation:
    Each raw string would match a URI with a regular expression search. For example, r'example.com/article/[0-9]+'
    for scraping the page 'example.com/article/1'

    Once a match is found, no other rules are checked.

    The ordered_rules list is checked by Trough in order, so you have the power to have regular expressions that match
    the same URI and know exactly which rule should be used (the rule that is earlier in the list).

    Each function contained within a sub-list MUST take two arguments, a BeautifulSoup and a ScrapeJob. A BeautifulSoup
    is just an HTML page that has been pre-parsed and is ready for easier traversal, this is given to you. A ScrapeJob
    is a part of Trough, and lets you request more page be scraped to satisfy the current rule. Each function then MUST
    return a list of strings or text-containing HTML elements, which represent the paragraphs that should be scraped
    from the page. Essentially, each function's job is to separate what you want out of the BeautifulSoup.

If you feel as if you don't completely understand, don't worry. Look over this file and the pattern should become clear.
If the scraping logic is confusing you, the Beautiful Soup documentation is a great resource and is located
here: http://www.crummy.com/software/BeautifulSoup/bs4/doc/

In this file I try to create useful rules that display various levels of complexity. If you'd like to see more
examples in the same format, see default_scraping_rules.py in Trough's source code.
"""

# Easy, but no section headers
def wikipedia_page(soup, job):
    return soup.findAll('p')


# Slightly more difficult
def youtube_video(soup, job):
    """ Scrape the video description """
    return [soup.find('div', {'id': 'watch-description-content'}).getText()]


# Difficult
def hacker_news_comment_page(soup, job):
    """ Scrape the linked article and the first 10 comments """
    link = soup.find('tr', {'class': 'athing'}).findAll('td', {'class': 'title'})[1].a['href']
    linked_article = job.get_contents(link)
    result = linked_article

    result.append('---------------- Comments ----------------')
    for comment in soup.findAll('span', {'class': 'comment'})[:10]:
        result.append(comment.getText())

    return result


# Have to be careful to escape special characters like '.' in the URL regex.
custom_scraping_rules = {
    r'wikipedia\.org/.+': wikipedia_page,
    r'youtube\.com/.*v=([^&]*)': youtube_video,
    r'news\.ycombinator\.com\/item\?id=.+': hacker_news_comment_page,
}

# Transforms the dictionary into a key/value list and sorts it by regular expression length (longest to shortest)
ordered_rules = sorted(custom_scraping_rules.items(), key=lambda x: len(x[0]))