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

from typing import Any

from gi import require_version

require_version('Gtk', '3.0')
from gi.repository import Gtk

from cache import Cache
from preferences import Preferences
from preferencesCategories import AppearancePreferences, FeedsPreferences


class PreferencesWindow(Gtk.Dialog):
    # TODO: Refactor this, why Preferences.preferences?
    def __init__(self, parent: Any, config: Preferences, cache: Cache):
        Gtk.Dialog.__init__(
            self,
            'Preferences',
            parent,
            0,
            (Gtk.STOCK_CANCEL,
             Gtk.ResponseType.CANCEL,
             'Save Changes',
             Gtk.ResponseType.OK))
        self.config = config
        self.preferences = config.preferences
        self.parent = parent
        self.set_default_size(300, 300)

        self.preferences_categories = [
            AppearancePreferences(self, self.preferences),
            FeedsPreferences(self, self.preferences, cache),
        ]

        self.notebook = Gtk.Notebook()
        for category in self.preferences_categories:
            self.notebook.append_page(category.create_display_area(), Gtk.Label(category.label))

        content = Gtk.Dialog.get_content_area(self)
        content.pack_start(self.notebook, True, True, 0)
        self.show_all()

    def apply_choices(self) -> None:
        """
        Apply the selected preferences to the current session, and make the selections persistent.
        """
        for category in self.preferences_categories:
            self.preferences[category.label] = category.gather_choices()
        self.config.update_preferences(self.preferences)

        self.parent.update_css()
        self.parent.switch_view(self.parent.news_store, self.config)
