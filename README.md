Trough
======

A GTK+ RSS news reader (currently in the early stages of development)

## Dependencies
* Python 3.3+ (3.x < 3.3 may work but is untested)
* [Feedparser](https://pypi.python.org/pypi/feedparser)
* [BeautifulSoup 4](http://www.crummy.com/software/BeautifulSoup/)
* [PyGObject](https://wiki.gnome.org/action/show/Projects/PyGObject)
* [Requests](http://docs.python-requests.org/en/latest/)

## Planned Features
* Simple, customizable interface.
* Content scraping, allowing users to provide custom scraping rules to complement or override default rules.
* "Fake feeds", set up a scrape rule for titled links and pretend it was an RSS feed.
* Read story tracking (entirely local, auto-clears with cache or program exit if no caching is used)
* Category support
* Filtration based on item title/description (not content for consistency reasons and less false positives)
* Per-feed time-based caching strategies (never/minutes/hours/days)

## Avoiding
* Bookmark management (browsers can do that).
* Podcast/Torrent/any other non-text integration (feature creep).
* Being cross-platform (simplifies testing).
* Third-party service integration (feature creep/privacy concerns).

## FAQ

#### Why build another RSS reader?

**Short answer:** Because I couldn't find an RSS reader that was focused solely around reading news articles.

**Long answer:** Current RSS readers that display linked content often do so through embedded browsers. While 
convenient, this approach brings with it all of the heaviness of a browser, as well as all of the visual noise of web 
pages. Trough takes a different approach by being based entirely around textual scraping. This is lightweight and 
allows users to decide exactly what they want to see, which is ideal for rapid news reading. Scraping has its own 
downsides, since scraping rules break when web designs inevitably change, and no collection of scraping rules could 
possibly be comprehensive. Due to this, Trough is primarily aimed towards advanced users who are willing to tweak and 
create scraping rules.

#### But what about sounds/pictures/videos?
These elements are commonly fluff in news reading and it is by design that Trough does not attempt to scrape or support
them. Emulating browser functionality is not a goal of this project, since the omission of multimedia and varying page 
design is where Trough gains all of its advantages over browsers and other RSS readers. When an article actually has you 
interested enough to want to see more, Trough allows you to quickly open the current link in an external browser session
using a keyboard shortcut (currently Ctrl+Enter) to see a page in its entirety.

#### When will Trough be usable?
Core functionality is already present, but no hard date has been set for feature completion. But don't worry, I'll be 
steadily working towards it. The feature set is frozen and a majority of the code has already been written, so the path 
forward is pretty clear. See the TODO file for task selection if you are seeking to contribute and feel free to message 
me if you have any questions.

#### When will Trough be stable?
Let's get to feature complete first.

## Installing/Running

#### Dependency Installation
You can use pip or your distribution's repositories. Here are instructions for some distributions:

**Arch:** `sudo pacman -S python-gobject python-feedparser python-beautifulsoup4 python-requests`

**Debian/Ubuntu:** `sudo apt-get install python3-gi python3-feedparser python3-bs4 python3-requests`

**Fedora:** `sudo yum install pygobject3 python3-feedparser python3-beautifulsoup4 python3-requests`

Trough itself has to be downloaded from GitHub.

#### Running
`cd` to the directory where you stored Trough's source files and run `python3 trough.py`. Note that the
program stores a preferences file at ~/.config/trough/preferences.json and a cache file at 
~/.cache/trough/cache.json

If the program fails to start then you are likely just missing a dependency. If it used to work but a git pull broke it,
I probably changed something with the preferences (sorry) and you need to delete your old preferences file.

Open an issue for any other problems encountered and I'll do my best to help you out.