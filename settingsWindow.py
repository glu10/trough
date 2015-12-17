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
from settingsCategories import *

class SettingsWindow(Gtk.Dialog):
    def __init__(self, parent, config):
        Gtk.Dialog.__init__(self, "Settings", parent, 0, (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                                          Gtk.STOCK_OK, Gtk.ResponseType.OK))
        self.set_default_size(200, 200)
        self.notebook = Gtk.Notebook()

        settings_categories = [AppearanceSettings(), FeedsSettings(), FiltrationSettings(), RetrievalSettings()]
        for category in settings_categories:
            category.choices = config[category.label] # Initialize settings
            self.notebook.addpage(category.create_display(), category.label)

        content = Gtk.Dialog.get_content_area()
        content.pack_start(self.notebook)

        



