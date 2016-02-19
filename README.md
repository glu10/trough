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
* "Fake feeds", set up a scrape rule for titled links and pretend it was an RSS feed.

## Avoiding
* Bookmark management (browsers can do that).
* Being cross-platform (simplifies testing).
* Podcast/Torrent/any other non-text integration (feature creep).

## FAQ

#### Why build another RSS reader?

**Short answer:** Because I couldn't find an RSS reader that fit the niche I was looking for.

**Long answer:** Current RSS readers that display linked content often do so through embedded browsers. While 
convenient, this approach brings with it all of the heaviness of a browser, as well as all of the visual noise of web 
pages. Trough takes a different approach by being based entirely around textual scraping. This is lightweight and 
allows users to decide exactly what they want to see. Scraping has its own downsides, since scraping rules break when 
web designs inevitably change, and no collection of scraping rules could possibly be comprehensive. Due to this, Trough 
is primarily aimed towards advanced users who are willing to tweak and create scraping rules.

#### Isn't just using a browser easier?
For one or two stories absolutely, but habitually checking sites becomes tiresome.

#### When will Trough be usable?
"Certainly eventually." I'm going to see this project to fruition because this is a program I have been wishing for
personally, but I don't want to set hard dates anymore because my schedule has been in flux. Core functionality
is present, but filtration, batch fetch, and fake feeds are still missing. Beyond that, there are still some rough 
spots that need fixing. I added a TODO file to keep track of things I have noticed to make task selection easier for 
anyone wanting to contribute.

#### When will Trough be stable?
Let's get to usable first.

## Installing/Running

#### Dependency Installation
You can use pip or your distribution's repositories. Here are instructions for some distributions:

**Arch:** `sudo pacman -S python-gobject python-feedparser python-beautifulsoup4 python-requests`

**Debian/Ubuntu:** `sudo apt-get install python3-gi python3-feedparser python3-bs4 python3-requests`

**Fedora:** `sudo yum install pygobject3 python3-feedparser python3-beautifulsoup4 python3-requests`

Trough itself has to be downloaded or pulled from GitHub.

#### Running
`cd` to the directory where you stored Trough's source files and run `python3 trough.py`. Note that the
program stores a preferences file at ~/.config/trough/preferences.json.

If the program fails to start then you are likely just missing a dependency. If it used to work but a git pull broke it,
I probably changed something with the preferences (sorry) and you need to delete your old preferences file.

If you encounter a different problem feel free to open an issue and I'll do my best to help you out.