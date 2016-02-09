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
                                                             'Save Changes', Gtk.ResponseType.OK))
        self.config = config
        self.preferences = config.preferences
        self.parent = parent
        self.set_default_size(300, 300)

        self.preferences_categories = [
                                       AppearancePreferences(self, self.preferences),
                                       FeedsPreferences(self, self.preferences),
                                       FiltrationPreferences(self.preferences),
                                       RetrievalPreferences(self.preferences),
                                      ]

        self.notebook = Gtk.Notebook()
        for category in self.preferences_categories:
            self.notebook.append_page(category.create_display_area(), Gtk.Label(category.label))

        content = Gtk.Dialog.get_content_area(self)
        content.pack_start(self.notebook, True, True, 0)
        self.show_all()

    def apply_choices(self):
        """
        Apply the selected preferences to the current session, and make the selections persistent.
        """
        for category in self.preferences_categories:
            self.preferences[category.label] = category.gather_choices()
        self.config.update_preferences(self.preferences)

        # TODO: Once each is implemented, iterate over preferences_categories instead of hardcoding each
        view = self.parent.switch_view()
        view.update_appearance(self.preferences['Appearance'])


        



