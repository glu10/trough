"""
    Trough - a GTK+ RSS news reader

    Copyright (C) 2016 Andrew Asp
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see {http://www.gnu.org/licenses/}.

    Trough homepage: https://github.com/glu10/trough
"""

import re


class Filter:

    def __init__(self, filt, case_sensitive, hide_matches):
        self.filter = filt
        self.case_sensitive = case_sensitive
        self.hide_matches = hide_matches
        if self.case_sensitive:
            self.searcher = re.compile(self.filter)
        else:
            self.searcher = re.compile(self.filter, re.IGNORECASE)

    def inspect_feed(self, feed):
        matched_any = False  # Makes the common case of no matches faster

        for item in feed.items:
            if not item.filtered:
                if self.searcher.search(item.title) or self.searcher.search(item.description):
                    item.filtered = True
                    matched_any = True

        if self.hide_matches and matched_any:
            new_items = list()
            for item in feed.items:
                if not item.filtered:
                    new_items.append(item)
            feed.items = new_items
