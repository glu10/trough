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

class SettingsCategory(metaclass=ABCMeta):

    def __init__(self, label):
        self.choices = dict()
        self.label = label

    @abstractmethod
    def create_display_area(self):

    @abstractmethod
    def gather_choices(self):


class AppearanceSettings(SettingsCategory):
    """
    Views (Single/Double/Triple)
    Fonts (Category/Headline/Story)
    """
    def __init__(self):
        super().__init__("Appearance")

    def create_display_area(self):
        grid = Gtk.Grid()
        grid.attach(self.view_radios(), 0,0,1,1)

    def fonts_buttons:
        fonts = ["Category", "Headline", "Story"]
        for font in fonts:
            fb = Gtk.FontButton()
            fb.set_title(font)
            # fb.connect

    def view_radios(self):
        views = ["Single", "Double", "Triple"]
        view_radios = list()
        for view in views:
            first = view_radios[0] if view_radios else None
            button = Gtk.RadioButton.new_with_label_from_widget(first, view)
            button.connect("toggled", lambda view: self.choices['View']=view, view)
            view_radios.append(button)
        return view_radios


    def gather_choices(self):


class FeedsSettings(SettingsCategory):
    def __init__(self):
        super().__init__("Feeds")

    def create_display_area(self):

    def gather_choices(self):

class FiltrationSettings(SettingsCategory):
    def __init__(self):
        super().__init__("Filtration")

    def create_display_area(self):

    def gather_choices(self):

class RetrievalSettings(SettingsCategory):
    def __init__(self):
        super().__init__("Retrieval")

    def create_display_area(self):

    def gather_choices(self):






