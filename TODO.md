## High Priority

* Separate UI feedback from network calls(!!) through signaling or threading
* Fetch RSS feeds and other batch calls with grequests (new dependency) to avoid one-after-another HTTP requests
* Filtration (filtration text color + hide completely/send-to-bottom)

## Medium Priority

* Drag and drop persistent feed ordering
* Categories for feeds (ListStore -> TreeStore)
* Persistent view widgets sizing
* Bottom status bar to communicate progress of network requests
* Icon fallbacks + get icon deprecated function fix

## Low Priority

* User Agent spoofing per feed (Reason: could make scraping certain sites easier by faking mobile)
* Refresh restriction per feed (ignore refresh of feed if last one was within x amount of time, would need caching).
* Shuffling display order option
* Ctrl+Scroll on-the-fly adjustment of font size (tricky without wasteful writing)
* Configurable give-up time for network requests
* Font color through CSS use to replace use of deprecated function.