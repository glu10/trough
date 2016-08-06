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


class FeedDialog(Gtk.Dialog):
    """ A Dialog for adding or editing information related to an RSS feed. """
    def __init__(self, parent, feed_container, feed=None, categories=None):
        Gtk.Dialog.__init__(self, 'Add Feed', parent, 0, (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                                          Gtk.STOCK_OK, Gtk.ResponseType.OK))
        self.feed = feed
        self.feed_container = feed_container
        self.missing_information = False  # Used for error display logic.
        self.set_default_size(150, 100)

        grid = Gtk.Grid(column_spacing=3, row_spacing=3, orientation=Gtk.Orientation.VERTICAL)

        # Widgets
        self.name_label, self.name_entry = self.add_labeled_entry('Name of Feed', grid)
        self.fake_feed_check_button = self.add_labeled_check_button('Fake Feed', '(leave unchecked if unsure)',
                                                                    self.on_fake_feed_toggled, grid)
        self.uri_label, self.uri_entry = self.add_labeled_entry('URI', grid)

        self.category_label = Gtk.Label("Category", xalign=0)
        self.category_combo = Gtk.ComboBoxText.new_with_entry()
        for category in categories:
            self.category_combo.append_text(category)
        grid.add(self.category_label)
        grid.attach_next_to(self.category_combo, self.category_label, Gtk.PositionType.RIGHT, 1, 1)

        self.error_label = Gtk.Label()
        self.error_label.set_markup('<span color="red">Fill in the missing information.</span>')
        grid.attach(self.error_label, 1, 4, 4, 1)

        # Make the ok_button the default so it can be triggered by the enter key.
        ok_button = self.get_widget_for_response(response_id=Gtk.ResponseType.OK)
        ok_button.set_can_default(True)
        ok_button.grab_default()

        # When an enter key is pressed on an entry, activate the okay button.
        self.name_entry.set_activates_default(True)
        self.uri_entry.set_activates_default(True)

        if self.feed:  # If a feed was passed in
            self.fill_in_feed_information(self.feed)

        box = self.get_content_area()
        box.add(grid)
        self.show_all()
        self.error_label.hide()  # The error label is only shown if the information entered isn't complete.

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

    def get_response(self):
        """
        :param feed_container: Must be a dict or Gtk.ListStore
        :return: AddFeedResponse containing the feed information, or None if the process was abandoned by the user.
        """
        # TODO: Fix this hacky function by creating a custom dialog with the OK button linked to a function that verifies info.
        return_val = None
        while True:
            response = self.run()
            if response == Gtk.ResponseType.OK:
                return_val = self.verify_entries()
                if return_val:
                    break
            elif response == Gtk.ResponseType.CANCEL or response == Gtk.ResponseType.NONE:
                break
        self.destroy()
        return return_val

    def verify_entries(self):
        """
        :return: AddFeedResponse containing the feed information, or None if the process was abandoned by the user.
        """
        name = self.name_entry.get_text()
        name_warning = self.verify_name(name, self.feed_container)
        name_already_existed = name_warning != ''

        uri = self.uri_entry.get_text()
        uri, uri_warning = self.verify_uri(uri)

        # if self.category_combo.has_entry()
        category = self.verify_category()

        if self.missing_information:
            self.error_label.show()
            self.missing_information = False  # Reset for next check
        else:
            self.error_label.hide()
            no_warnings = name_warning == '' and uri_warning == ''

            if no_warnings:
                return FeedDialogResponse(name, uri, False)

            warning_string = '\n'.join(filter(None, [name_warning, uri_warning, '\nAdd feed anyway?']))
            if utilityFunctions.decision_popup(self, 'Warning!', warning_string):
                return FeedDialogResponse(name, uri, name_already_existed)  # User chose to add feed despite warnings.
            else:
                return None  # User chose not to add the feed.

    def switch_red_on_entry_label(self, entry_text, label):
        if entry_text == '':  # If the information corresponding to this label is missing (blank)
            self.missing_information = True
            label.set_markup('<span color="red">' + label.get_text() + '</span>')  # Make the label red
        else:
            label.set_text(label.get_text())  # Make the label normal (non-red)

    def verify_name(self, name, feed_container):
        self.switch_red_on_entry_label(name, self.name_label)
        if not self.feed and self.check_existence(name, feed_container):
            return 'A feed named \"' + name + '\" already exists. It will be overwritten.'
        else:
            return ''

    def verify_uri(self, uri):
        warning = ''
        if not self.fake_feed_check_button.get_active():  # If not a fake feed (real feeds have URIs that matter)
            self.switch_red_on_entry_label(uri, self.uri_label)

            if not (uri.startswith('/') or uri.startswith('http://') or uri.startswith('https://')):
                uri = 'http://' + uri

            content = utilityFunctions.feedparser_parse(uri)  # Probe the URI
            if not content:
                warning = 'The URI ' + uri + ' returned no valid RSS items.'
        return uri, warning

    def verify_category(self):
        text = self.category_combo.get_active_text().strip()
        if text:
            return text
        else:
            return 'Uncategorized'

    @staticmethod
    def check_existence(name, feed_container):
        """ Prevents duplicate feeds with the same name """
        if type(feed_container) == dict:
            return name in feed_container
        elif type(feed_container) == Gtk.ListStore:
            for row in feed_container:
                if row[0] == name:
                    return True
            return False
        else:
            raise RuntimeError('An invalid feed list container of type '
                               + str(type(feed_container))
                               + ' was passed to AddFeed.')
