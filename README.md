Trough
======

A GTK+ RSS news reader (currently in the early stages of development)

## Dependencies
* Python 3.x+
* [Feedparser](https://pypi.python.org/pypi/feedparser)
* [BeautifulSoup 4](http://www.crummy.com/software/BeautifulSoup/)
* [PyGObject](https://wiki.gnome.org/action/show/Projects/PyGObject)
* [Requests](http://docs.python-requests.org/en/latest/)

## Goals
* Simple, customizable interface.
* News story scraping, allowing users to provide custom scraping rules to complement or override default rules.
* Timed filtration (based on content/title). "I'm so tired of X, I don't want to see it again until Y."
* Multiple fetching/caching strategies (Prefetch all stories? Fetch on headline click?)

## Avoiding
* Bookmark management (browsers can do that).
* Being cross-platform (simplifies testing).


## FAQ

#### Why build another RSS reader?

Current RSS readers only display the content given directly in an RSS feed, which is entirely sensible.
Trough aims to take on the unmaintainable task of displaying both RSS content and linked content.
Displaying linked content can be done through scraping, but scraping rules break and can't possibly be comprehensive.
What's an RSS reader to do? Assume an advanced user and cede control.


#### Isn't just using a browser easier?
For one or two stories absolutely, but habitually checking sites becomes tiresome.


#### When will Trough be usable?
Hopefully by the end of ~~December 2015~~ January 2016. This prediction will be updated if things change.

**Update:** Apologies for the delay of the prediction, my busy November set things back and I want to take the time to
 program things correctly. Core functionality is already present, but it is a little rough around the edges. If you want
 to run things yourself, place all the python files in a single directory and run trough.py. Note that the program
 stores a preferences file at ~/.config/trough/preferences.json


#### When will Trough be stable?
Let's get to usable first.