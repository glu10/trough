import re


class Filter:

    def __init__(self, trigger, case_sensitive):
        self.trigger = trigger
        self.case_sensitive = case_sensitive
        if not self.case_sensitive:
            self.matcher = re.compile(self.trigger, re.IGNORECASE)
        else:
            self.matcher = re.compile(self.trigger)

    def inspect_feed(self, feed):
        for item in feed.items:
            if not item.filtered:
                if self.matcher.match(item.title) or self.matcher.match(item.description):
                    item.filtered = True
