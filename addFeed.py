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

from gi.repository import Gtk
from collections import OrderedDict
import utilityFunctions


class AddFeed(Gtk.Dialog):
    """ A Dialog for adding a new RSS feed. """
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

    def get_response(self, feed_container):
        """
        :param feed_container: Must be a dict or Gtk.ListStore
        :return: AddFeedResponse containing the feed information, or None if the process was abandoned by the user.
        """
        # TODO: Fix this hacky function by creating a custom dialog with the OK button linked to a function that verifies info.
        return_val = None
        while True:
            response = self.run()
            if response == Gtk.ResponseType.OK:
                return_val = self.verify_entries(feed_container)
                if return_val:
                    break
            elif response == Gtk.ResponseType.CANCEL or response == Gtk.ResponseType.NONE:
                break
        self.destroy()
        return return_val

    @staticmethod
    def add_labeled_entry(text, grid, width_entry):
        label = Gtk.Label(text, xalign=0)
        entry = Gtk.Entry(hexpand=True)
        grid.add(label)
        grid.attach_next_to(entry, label, Gtk.PositionType.RIGHT, width_entry, 1)
        return entry

    def verify_entries(self, feed_container):
        """
        :param feed_container: Must be a dict or Gtk.ListStore
        :return: AddFeedResponse containing the feed information, or None if the process was abandoned by the user.
        """
        name = self.name_entry.get_text()
        uri = self.uri_entry.get_text()

        if name != "" and uri != "":

            if uri[0] != '/':  # if not a local file
                if not uri.startswith("http"):
                    uri = "http://" + uri

            content = utilityFunctions.feedparser_parse(uri)

            warning = ""
            no_items = not content
            already_exists = self.check_existence(name, feed_container)

            if no_items and already_exists:
                warning = "The feed named \"" + name + "\" already exists and " \
                          + "the URI \"" + uri + "\" returned no valid RSS items."
            elif no_items:
                warning = "The URI \"" + uri + "\" returned no valid RSS items."
            elif already_exists:
                warning = "The feed name " + name + " already exists."

            if not warning or utilityFunctions.decision_popup(self, warning + " Add the feed anyway?", ""):
                return AddFeedResponse(name, uri, already_exists)
            else:
                return None

        else:
            self.error_label.show()

        return False

    def check_existence(self, name, feed_container):
        if type(feed_container) in (dict, OrderedDict):
            return name in feed_container
        elif type(feed_container) == Gtk.ListStore:
            for row in feed_container:
                if row[0] == name:
                    return True
            return False
        else:
            raise RuntimeError("An invalid feed list container of type " + str(type(feed_container)) + " was passed to AddFeed.")

class AddFeedResponse:
    """ Organizes the response information in an easy format """
    def __init__(self, name, uri, overwrite):
        self.name = name
        self.uri = uri
        self.overwrite = overwrite
