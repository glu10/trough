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


from gi.repository import Gtk

from feed import Feed
import utilityFunctions


class FeedDialog(Gtk.Dialog):
    """ A Dialog for adding or editing information related to an RSS feed. """

    def __init__(self, parent, feed_container, feed=None):
        Gtk.Dialog.__init__(self, 'Add Feed', parent, 0, (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                            Gtk.STOCK_OK, Gtk.ResponseType.OK))
        self.set_default_size(150, 100)
        ok_button = self.get_widget_for_response(response_id=Gtk.ResponseType.OK)
        ok_button.set_can_default(True)
        ok_button.grab_default()

        self.connect('response', self.on_dialog_response)
        num_columns = 3
        grid = Gtk.Grid(orientation=Gtk.Orientation.VERTICAL, column_spacing=num_columns)
        feed_row = FeedDialogRow(grid, 'Name of Feed', Gtk.Entry(hexpand=True))
        feed_row.set_preexisting_feeds(feed_container)
        uri_row = UriDialogRow(grid, 'URI', Gtk.Entry(hexpand=True))
        self.rows = [feed_row, uri_row]

        if feed is not None:  # A feed was passed in, populate the rows with the feed information.
            self.set_title('Edit Feed')
            for row in self.rows:
                row.fill_in(feed)

        self.error_label = Gtk.Label('')
        self.error_label.set_markup('<span color="red">Fill in the missing information.</span>')
        grid.attach(self.error_label, 0, len(self.rows)+1, num_columns , 1)

        box = self.get_content_area()
        box.add(grid)
        box.show_all()
        self.error_label.hide() # hidden initially, only shown if information is incomplete

    def get_response(self):
        """ Primary external call. Returns a valid Feed object upon success or None otherwise. """
        ret = None
        if self.run() == Gtk.ResponseType.OK:
            ret = Feed(*(row.retrieve() for row in self.rows)) # Construct a feed object.
        self.destroy()
        return ret

    def on_dialog_response(self, parent, response):
        if response == Gtk.ResponseType.OK and not self.verify():
            self.emit_stop_by_name('response') # stops the signal from  exiting the run() loop

    def verify(self):
        """ Checks each row for correctness. Issues a warning to the user if correctness is conditional. """
        correct = True
        warning_list = list()
        for row in self.rows:
            if row.verify(warning_list):
                row.mark_red(False)
            else:
                row.mark_red(True)
                correct = False

        if not correct:
            self.error_label.show()
        elif warning_list:  # The information may be valid depending on the user's wishes, prompt them.
            self.error_label.hide()
            return self.warn(warning_list)
        return correct

    def warn(self, warning_list):
        warning_list.append('Add feed anyway?')
        decision = utilityFunctions.decision_popup(self, 'Warning!', '\n'.join(warning_list))
        warning_list.clear()
        return decision



class DialogRow:
    def __init__(self, grid, label_text, interactive_element):
        self.label = Gtk.Label(label_text, xalign=0)
        self.interactive = interactive_element
        self.interactive.set_activates_default(True)
        grid.add(self.label)
        grid.attach_next_to(self.interactive, self.label, Gtk.PositionType.RIGHT, 1, 1)

    def fill_in(self, feed):
        """ Set known information for the interactive element. """
        pass

    def mark_red(self, b):
        """ Color/uncolor the label of this row to be red for error indication. """
        if b:
            self.label.set_markup('<span color="red">' + self.label.get_text() + '</span>')
        else:
            self.label.set_text(self.label.get_text())  # Make label text normal (non-red)

    def retrieve(self):
        """ Get the relevant information from the interactive element. """
        pass

    def verify(self, warning_list):
        """ Is the information in the interactive element correct? If conditional, append a warning. """
        return True  # vacuously true

class FeedDialogRow(DialogRow):
    """ GUI element for naming an RSS feed. """

    def __init__(self, *args):
        super().__init__(*args)
        self.preexisting = None  # Feeds that already exist (for enforcing uniqueness)
        self.filled_in_name = None  # If a feed name was filled in, it has to be remembered to prevent erroneously flagging it as not unique.

    def fill_in(self, feed):
        self.filled_in_name = feed.name
        self.interactive.set_text(self.filled_in_name)

    def retrieve(self):
        return self.interactive.get_text()

    def set_preexisting_feeds(self, container):
        """If container is not a set/dictionary, make it one for O(1) existance checking. """
        if isinstance(container, Gtk.ListStore):
            container = {row[0] for row in container}
        self.preexisting = container
        return self

    def verify(self, warning_list):
       feed_name = self.retrieve()
       if not feed_name:
           return False  # A blank feed name is always incorrect
       elif feed_name != self.filled_in_name and feed_name in self.preexisting:
            warning.append('The feed name ' + feed_name + ' already exists and will be overwritten.')
       return True


class UriDialogRow(DialogRow):
    """ GUI element for entering an RSS feed's URI. """

    def fill_in(self, feed):
        self.interactive.set_text(feed.uri)

    def retrieve(self):
        return self.interactive.get_text()

    def verify(self, warning_list):
        uri = self.retrieve()
        if not uri:
            return False  # A blank URI is always incorrect
        elif not (uri.startswith('/') or uri.startswith('http://') or uri.startswith('https://')):
                uri = 'http://' + uri  # Attempt to complete the URI #TODO: Instead of preemptively trying to fix it, probe it as is first.
        content = utilityFunctions.feedparser_parse(uri)  # Probe the URI
        if not content:
            warning_list.append('The URI ' + uri + ' did not contain a valid RSS feed.')
        return True

