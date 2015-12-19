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

from abc import ABCMeta, abstractmethod
from gi.repository import Gtk

class PreferencesCategory(metaclass=ABCMeta):

    def __init__(self, config, label):
        self.choices = config[label]
        self.label = label

    @abstractmethod
    def create_display_area(self):
        """
        Create the GUI components that will be in the preferences page
        """

    @abstractmethod
    def gather_choices(self):  # TODO: Unnecessary since signals can catch the changes?
        """
        From the GUI components, gather the selections and return them in a dictionary.
        """

    def bold_label(self, text):
        label = Gtk.Label()
        label.set_markup('<b>' + text + '</b>')
        return label


class AppearancePreferences(PreferencesCategory):
    """
    Views (Single/Double/Triple)
    Fonts (Category/Headline/Story)
    """
    def __init__(self, config):
        super().__init__(config, 'Appearance')

    def create_display_area(self):
        grid = Gtk.Grid()
        grid.set_row_spacing(3)
        grid.set_column_spacing(7)

        # View selection
        grid.attach(self.bold_label('View'), 0, 0, 1, 1)
        grid.attach(self.view_combo_box(), 0, 1, 1, 1)

        # Font selection
        grid.attach(self.bold_label('Fonts'), 0, 6, 1, 2)
        panes = ['Category Font', 'Headline Font', 'Story Font']
        for i, fb in enumerate(self.font_buttons(panes)):
            grid.attach(Gtk.Label(panes[i]), 0, i+8, 1, 1)
            grid.attach(fb, 1, i+8, 1, 1)

        return grid

    def font_buttons(self, panes):
        fbs = list()
        for pane in panes:
            fb = Gtk.FontButton()
            fb.set_title(pane + " Font")
            fb.set_font_name(self.choices[pane])
            fb.connect('font-set', self.font_switched, pane)
            fbs.append(fb)
        return fbs

    def font_switched(self, button, pane):
        self.choices[pane] = button.get_font_name()

    def view_combo_box(self):
        views = ['Single', 'Double', 'Triple']

        cb = Gtk.ComboBoxText()
        for view in views:
            cb.append_text(view)
        cb.set_active(views.index(self.choices['View']))
        cb.connect('changed', self.view_switched)
        return cb

    def view_switched(self, combo):  # button needed?
        self.choices['View'] = combo.get_active_text()

    def gather_choices(self):
        pass


class FeedsPreferences(PreferencesCategory):
    def __init__(self, config):
        super().__init__(config, 'Feeds')

    def create_display_area(self):
        return Gtk.Grid()

    def gather_choices(self):
        pass


class FiltrationPreferences(PreferencesCategory):
    def __init__(self, config):
        super().__init__(config, 'Filtration')

    def create_display_area(self):
        return Gtk.Grid()

    def gather_choices(self):
        pass


class RetrievalPreferences(PreferencesCategory):
    def __init__(self, config):
        super().__init__(config, 'Retrieval')

    def create_display_area(self):
        return Gtk.Grid()

    def gather_choices(self):
        pass






