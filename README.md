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
"Certainly eventually." I'm going to see this project to fruition because this is a program I have been wishing for
personally and use, but I don't want to set hard dates anymore because my schedule has been in flux. Core functionality
is present, but filtration and batch fetch are still missing. Beyond that, there are still some rough spots that need 
fixing. I added a TODO file to keep track of things I have noticed to make task selection easier for anyone wanting to
contribute.

#### When will Trough be stable?
Let's get to usable first.

## Installing/Running

#### Dependency Installation
You can use pip or your distribution's repositories.

Here are instructions for some distributions:

**Arch:** `sudo pacman -S python-gobject python-feedparser python-beautifulsoup4 python-requests`

**Debian/Ubuntu:** `sudo apt-get install python3-gi python3-feedparser python3-bs4 python3-requests`

**Fedora:** `sudo yum install pygobject3 python3-feedparser python3-beautifulsoup4 python3-requests`

Trough itself has to be downloaded or pulled from GitHub.

#### Running
`cd` to the directory where you stored Trough's source files and run `python3 trough.py`. Note that the
program stores a preferences file at ~/.config/trough/preferences.json.

If the program fails to start then you are likely just missing a dependency. If it used to work but git pull broke it,
I probably changed something with the preferences (sorry) and you need to delete your old preferences file.

If you encounter a different problem feel free to open an issue and I'll do my best to help you out.
