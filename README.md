Trough
======

A GTK+ RSS news reader (moved to a private GitLab repo, will update if status changes)

For now, do not attempt to run this.

## Dependencies
* Python 3.3+ (3.x < 3.3 may work but is untested)
* [Feedparser](https://pypi.python.org/pypi/feedparser)
* [BeautifulSoup 4](http://www.crummy.com/software/BeautifulSoup/)
* [PyGObject](https://wiki.gnome.org/action/show/Projects/PyGObject)
* [Requests](http://docs.python-requests.org/en/latest/)

## FAQ

#### Why build another RSS reader?

**Short answer:** Because I couldn't find an RSS reader that was focused solely around reading news articles.

**Long answer:** Current RSS readers that display linked content often do so through embedded browsers. While 
convenient, this approach brings with it all of the heaviness of a browser, as well as all of the visual noise of web 
pages. Trough takes a different approach by being based entirely around textual scraping. 

#### But what about sounds/pictures/videos?
These elements are commonly fluff in news reading and it is by design that Trough does not attempt to scrape or support
them. Emulating browser functionality is not a goal of this project, since the omission of multimedia and varying page 
design is where Trough gains all of its advantages over browsers and other RSS readers. When an article actually has you 
interested enough to want to see more, Trough allows you to quickly open the current link in an external browser session
using a keyboard shortcut (currently Ctrl+Enter) to see a page in its entirety.

## Installing/Running

#### Dependency Installation
You can use pip or your distribution's repositories. Here are instructions for some distributions:

**Arch:** `sudo pacman -S python-gobject python-feedparser python-beautifulsoup4 python-requests`

**Debian/Ubuntu:** `sudo apt-get install python3-gi python3-feedparser python3-bs4 python3-requests`

**Fedora:** `sudo yum install pygobject3 python3-feedparser python3-beautifulsoup4 python3-requests`

Trough itself has to be downloaded from GitHub.

#### Running
`python3 trough.py`

Note that the program stores a preferences file at ~/.config/trough/preferences.json and a cache file at 
~/.cache/trough/cache.json
