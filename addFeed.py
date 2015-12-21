"""
    Trough - a GTK+ RSS news reader

    Copyright (C) 2015 Andrew Asp
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

import feedparser

from gi.repository import Gtk
import dialogs

class AddFeed(Gtk.Dialog):

    def __init__(self, parent):
        Gtk.Dialog.__init__(self, "Add Feed", parent, 0, (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                                          Gtk.STOCK_OK, Gtk.ResponseType.OK))

        self.set_default_size(150, 100)
        box = self.get_content_area()

        grid = Gtk.Grid(column_spacing=3, row_spacing=3, orientation=Gtk.Orientation.VERTICAL)

        self.name_entry = self.add_labeled_entry("Name of Feed", grid, 4)
        self.uri_entry = self.add_labeled_entry("URI", grid, 4)

        self.error_label = Gtk.Label()
        self.error_label.set_markup('<span color="red">Please fill in all of the information.</span>')
        grid.attach(self.error_label, 1, 3, 3, 1)

        box.add(grid)
        self.show_all()
        self.error_label.hide()  # Is shown only if the information entered isn't complete.

    @staticmethod
    def add_labeled_entry(text, grid, width_entry):
        label = Gtk.Label(text, xalign=0)
        entry = Gtk.Entry(hexpand=True)
        grid.add(label)
        grid.attach_next_to(entry, label, Gtk.PositionType.RIGHT, width_entry, 1)
        return entry

    def add_entry(self, config):
        name = self.name_entry.get_text()
        uri = self.uri_entry.get_text()

        if name != "" and uri != "":

            if uri[0] != '/':  # if not a local file
                if not uri.startswith("http"):
                    uri = "http://" + uri

            try:
                feedparser.parse(uri)  # This call is purely to try to catch problems before the feed is added.
            except TypeError:
                if 'drv_libxml2' in feedparser.PREFERRED_XML_PARSERS:
                    feedparser.PREFERRED_XML_PARSERS.remove('drv_libxml2')
                feedparser.parse(uri)

            if config.add_feed(name, uri):
                return True
            elif dialogs.decision_popup(self, "Name of feed already exists, overwrite?", ""):
                    config.add_feed(name, uri, overwrite=True)
                    return True
            else:
                return False

        else:
            self.error_label.show()

        return False
