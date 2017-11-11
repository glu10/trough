"""
    Trough - a GTK+ RSS news reader

    Copyright (C) 2017 Andrew Asp
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
import gi
gi.require_version('Gtk', '3.0')

from gi.repository import Gtk

class NewsStore():
    """ A centralized data repository of all viewable fetched content. """

    def __init__(self):
        self.store = Gtk.TreeStore(
                str, # Feed Name
                str, # Item Title
                str, # Item Content 
                str) # Item URI

    def add_feed(self, feed):
        name = feed.name
        for item in feed:
            self.add_item(name, item)
            
    def add_item(self, feed_name, item):
        self.store.append(
            [feed_name,
            item.title,
            item.article,
            item.uri])

    def model(self):
        return self.store
