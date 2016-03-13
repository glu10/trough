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
import utilityFunctions


class AddFeed(Gtk.Dialog):
    """ A Dialog for adding a new RSS feed. """
    def __init__(self, parent, feed=None):
        Gtk.Dialog.__init__(self, 'Add Feed', parent, 0, (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                                          Gtk.STOCK_OK, Gtk.ResponseType.OK))
        self.feed = feed
        self.missing_information = False  # Used for error display logic.
        self.set_default_size(150, 100)

        # Make the ok button the default button so it can be triggered by the enter key.
        ok_button = self.get_widget_for_response(response_id=Gtk.ResponseType.OK)
        ok_button.set_can_default(True)
        ok_button.grab_default()

        grid = Gtk.Grid(column_spacing=3, row_spacing=3, orientation=Gtk.Orientation.VERTICAL)
        self.name_label, self.name_entry = self.add_labeled_entry('Name of Feed', grid)
        self.fake_feed_check_button = self.add_labeled_check_button('Fake Feed', '(leave unchecked if unsure)',
                                                                    self.on_fake_feed_toggled, grid)
        self.uri_label, self.uri_entry = self.add_labeled_entry('URI', grid)
        self.error_label = Gtk.Label()
        self.error_label.set_markup('<span color="red">Fill in the missing information.</span>')
        grid.attach(self.error_label, 1, 4, 4, 1)

        # When an enter key is pressed on an entry, activate the okay button.
        self.name_entry.set_activates_default(True)
        self.uri_entry.set_activates_default(True)

        if self.feed:  # If a feed was passed in
            self.fill_in_feed_information(self.feed)

        box = self.get_content_area()
        box.add(grid)
        self.show_all()
        self.error_label.hide()  # Is shown only if the information entered isn't complete.

    @staticmethod
    def add_labeled_entry(text, grid):
        label = Gtk.Label(text, xalign=0)
        entry = Gtk.Entry(hexpand=True)
        grid.add(label)
        grid.attach_next_to(entry, label, Gtk.PositionType.RIGHT, 1, 1)
        return label, entry

    @staticmethod
    def add_labeled_check_button(before_check_text, after_check_text, function, grid):
        label = Gtk.Label(before_check_text, xalign=0)
        grid.add(label)
        type_button = Gtk.CheckButton(after_check_text)
        type_button.connect('toggled', function)
        grid.attach_next_to(type_button, label, Gtk.PositionType.RIGHT, 1, 1)
        return type_button

    def fill_in_feed_information(self, feed):
        """ Used when a feed is going to be edited. Pre-existing feed information gets pre-filled here. """
        self.name_entry.set_text(feed.name)
        if feed.is_fake():
            self.fake_feed_check_button.set_active(True)  # Behaves as if the user checked the box.
        else:
            self.uri_entry.set_text(feed.uri)

    def on_fake_feed_toggled(self, button):
        """ If fake feed is checked, the URI label/entry is not needed. """
        checked = button.get_active()
        if checked:
            self.uri_entry.set_text('')
            self.uri_label.set_text(self.uri_label.get_text())  # Disables markup (workaround)
        elif self.error_label.is_visible():  # Prevents losing the 'missing' status of the URI after unchecking.
            self.switch_red_on_entry_label('', self.uri_label)

        self.uri_label.set_sensitive(not checked)
        self.uri_entry.set_sensitive(not checked)

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

    def verify_entries(self, feed_container):
        """
        :param feed_container: Must be a dict or Gtk.ListStore
        :return: AddFeedResponse containing the feed information, or None if the process was abandoned by the user.
        """
        name = self.name_entry.get_text()
        name_warning = self.verify_name(name, feed_container)
        name_already_existed = name_warning != ''

        uri = self.uri_entry.get_text()
        uri, uri_warning = self.verify_uri(uri)

        if self.missing_information:
            self.error_label.show()
            self.missing_information = False  # Reset for next check
        else:
            self.error_label.hide()
            no_warnings = name_warning == '' and uri_warning == ''

            if no_warnings:
                return AddFeedResponse(name, uri, False)

            warning_string = '\n'.join(filter(None, [name_warning, uri_warning, '\nAdd feed anyway?']))
            if utilityFunctions.decision_popup(self, 'Warning!', warning_string):
                return AddFeedResponse(name, uri, name_already_existed)  # Despite warnings, user chose to add the feed.
            else:
                return None  # User chose not to add the feed.

    def switch_red_on_entry_label(self, entry_text, label):
        if entry_text == '':
            self.missing_information = True
            label.set_markup('<span color="red">' + label.get_text() + '</span>')
        else:
            label.set_text(label.get_text())

    def verify_name(self, name, feed_container):
        self.switch_red_on_entry_label(name, self.name_label)

        if not self.feed and self.check_existence(name, feed_container):
            return 'A feed named \"' + name + '\" already exists. It will be overwritten.'
        else:
            return ''

    def verify_uri(self, uri):
        warning = ''
        if not self.fake_feed_check_button.get_active(): # The URI doesn't matter for a fake feed
            self.switch_red_on_entry_label(uri, self.uri_label)

            if not (uri.startswith('/') or uri.startswith('http://')):  # Mitigate user leaving out 'http://'
                uri = 'http://' + uri

            content = utilityFunctions.feedparser_parse(uri)  # Probe the URI
            if not content:
                warning = 'The URI ' + uri + ' returned no valid RSS items.'
        return uri, warning

    @staticmethod
    def check_existence(name, feed_container):
        if type(feed_container) == dict:
            return name in feed_container
        elif type(feed_container) == Gtk.ListStore:
            for row in feed_container:
                if row[0] == name:
                    return True
            return False
        else:
            raise RuntimeError('An invalid feed list container of type ' + str(type(feed_container)) +
                               ' was passed to AddFeed.')


# TODO Now that a feed class exists this isn't necessary, make a Feed object and return it.
class AddFeedResponse:
    """ Organizes the response information in an easy format """
    def __init__(self, name, uri, overwrite):
        self.name = name
        self.uri = uri
        self.overwrite = overwrite
