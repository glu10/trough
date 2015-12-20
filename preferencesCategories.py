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
from gi.repository import Gtk, Gdk

# NOT FINISHED

class PreferencesCategory(metaclass=ABCMeta):

    def __init__(self, config, label):
        self.choices = config[label].copy()  # Copying to prevent overwriting settings until final okay.
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
        """
        Label used in a preferences category to title a class of selections
        """
        label = Gtk.Label()
        label.set_markup('<b>' + text + '</b>')
        return label

    def descriptor_label(self, text):
        """
        Label used in a preferences category to label an individual item in a class of selections
        """
        label = Gtk.Label(text)
        label.set_alignment(0, .5)  # Left justifies (set_justify will not work)
        label.set_padding(5, 0)  # Pad from the left side
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
        grid.set_orientation(Gtk.Orientation.VERTICAL)
        grid.add(self.bold_label('View'))
        grid.add(self.view_combo_box())

        # Font selection
        grid.add(self.bold_label('Fonts'))
        panes = ['Category Font', 'Headline Font', 'Story Font']
        for pane in panes:
            label = self.descriptor_label(pane)
            grid.add(label)
            grid.attach_next_to(self.font_button(pane), label, Gtk.PositionType.RIGHT, 1, 1)

        # Font Colors
        grid.add(self.bold_label('Colors'))
        color_idents = ['Font Color', 'Background Color']
        for c in color_idents:
            label = self.descriptor_label(c)
            grid.add(label)
            grid.attach_next_to(self.color_button(c), label, Gtk.PositionType.RIGHT, 1, 1)

        return grid

    def font_button(self, pane):
        fb = Gtk.FontButton()
        fb.set_title(pane)
        fb.set_font_name(self.choices[pane])
        fb.connect('font-set', self.font_switched, pane)
        return fb

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

    def color_button(self, name):
        rgba = Gdk.RGBA()
        rgba.parse(self.choices[name])
        cb = Gtk.ColorButton.new_with_rgba(rgba)
        cb.connect('color-set', self.color_switched, name)
        return cb

    def color_switched(self, cc, name):
        self.choices[name] = cc.get_rgba().to_string()

    def gather_choices(self):
        pass


class FeedsPreferences(PreferencesCategory):
    def __init__(self, config):
        super().__init__(config, 'Feeds')

    def create_display_area(self):
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        feed_list = self.create_feed_list()
        feed_info = self.create_feed_info()
        hbox.pack_start(feed_list, False, False, 5)
        hbox.pack_end(feed_info, False, False, 5)
        return hbox

    def create_feed_list(self):
        """
        Displays a list of feed labels, if a feed is clicked the information and options for that feed are displayed
        Above the list are two buttons, which allow for the list to be modified through insertion/deletion
        """
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        # Buttons (used to delete or add feeds)
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        delete_button = Gtk.Button.new_with_label('-')
        add_button = Gtk.Button.new_with_label('+')
        button_box.pack_start(delete_button, False, False, 0)
        button_box.pack_start(add_button, False, False, 0)
        vbox.pack_start(button_box, False, False, 0)

        # List of Feeds
        # TODO: Should do a model here

        #vbox.pack_start(list, True, True, 0)

        return vbox

    def create_feed_info(self):
        """
        Display the information related to a feed. Allow editing of the values?
        """
        return Gtk.Frame()


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






