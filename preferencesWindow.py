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
from preferencesCategories import *

class PreferencesWindow(Gtk.Dialog):
    def __init__(self, parent, config):
        Gtk.Dialog.__init__(self, 'Preferences', parent, 0, (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                                          Gtk.STOCK_OK, Gtk.ResponseType.OK))
        self.config = config
        self.preferences = config.preferences
        self.set_default_size(300, 300)
        self.notebook = Gtk.Notebook()

        self.preferences_categories = [
                                       AppearancePreferences(self.preferences),
                                       FeedsPreferences(self.preferences),
                                       FiltrationPreferences(self.preferences),
                                       RetrievalPreferences(self.preferences)
                                      ]

        for category in self.preferences_categories:
            self.notebook.append_page(category.create_display_area(), Gtk.Label(category.label))

        content = Gtk.Dialog.get_content_area(self)
        content.pack_start(self.notebook, True, True, 0)
        self.show_all()

    def apply_choices(self):
        """
        Make the selected preferences the actual preferences.
        Signal for changes?
        """
        for category in self.preferences_categories:
            self.preferences[category.label] = category.gather_choices()
        self.config.update_preferences_file()

        



