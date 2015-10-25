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
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        box.add(vbox)

        name_hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=50)
        name_label = Gtk.Label("Name of Feed", xalign=0)
        self.name_entry = Gtk.Entry()
        name_hbox.pack_start(name_label, True, True, 0)
        name_hbox.pack_start(self.name_entry, True, True, 0)

        url_hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=50)
        url_label = Gtk.Label("URL of Feed   ", xalign=0)
        self.url_entry = Gtk.Entry()
        url_hbox.pack_start(url_label, True, True, 0)
        url_hbox.pack_start(self.url_entry, True, True, 0)

        self.error_label = Gtk.Label("", xalign=0)

        vbox.pack_start(name_hbox, True, True, 0)
        vbox.pack_start(url_hbox, True, True, 0)
        vbox.pack_start(self.error_label, True, True, 0)
        self.show_all()

    def add_entry(self, config):
        name = self.name_entry.get_text()
        uri = self.url_entry.get_text().strip("http://")

        if name != "" and uri != "":
            try:
                feedparser.parse(uri)
                if config.add_feed(name, uri) or \
                        dialogs.decision_popup(self, "Name of feed already exists, overwrite?", ""):
                    config.add_feed(name, uri, overwrite=True)
                    return True
            except:
                raise
                #self.error_label.set_markup('<span color="red">URI could not be reached. Is it valid?</span>')
        else:
            self.error_label.set_markup('<span color="red">Please fill in all of the information.</span>')

        return False
