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
from gi.repository import Gtk, Gdk, Gio
from collections import OrderedDict
from addFeed import AddFeed
import utilityFunctions
from configManager import ConfigManager


class PreferencesCategory(metaclass=ABCMeta):

    def __init__(self, preferences, label):
        self.choices = OrderedDict()
        if preferences[label] is not None:
            self.choices = preferences[label].copy()  # Copying to prevent overwriting preferences until final okay.
        self.label = label

    @abstractmethod
    def create_display_area(self):
        """
        Create the GUI components that will be in the preferences page
        """

    def gather_choices(self):
        """
        From the GUI components, gather the selections and return them in a dictionary.
        """
        return self.choices

    def bold_label(self, text, left=False):
        """
        Label used in a preferences category to title a class of selections
        """
        label = Gtk.Label()
        label.set_markup('<b>' + text + '</b>')
        if left:
            label.set_alignment(0, .5)  # Left justifies (set_justify will not work)
            label.set_padding(5, 0)  # Pad from the left side

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
    Views (Two-Pane/Three-Pane)
    Fonts (Category/Headline/Story)
    Colors (Font Color/Background Color/Selection Color/Selection Background Color)
    Reset to Defaults Button
    """
    def __init__(self, parent, preferences):
        super().__init__(preferences, 'Appearance')
        self.parent = parent

        self.view_box = None

        self.font_idents = ['Category Font', 'Headline Font', 'Story Font']
        self.font_buttons = []

        self.color_idents = ['Font Color', 'Background Color', 'Selection Font Color', 'Selection Background Color']
        self.color_buttons = []


    def create_display_area(self):
        grid = Gtk.Grid(row_spacing=3, column_spacing=7, orientation=Gtk.Orientation.VERTICAL)

        # View selection
        grid.add(self.bold_label('View'))
        self.view_box = self.view_combo_box()
        grid.add(self.view_box)

        # Font selection
        grid.add(self.bold_label('Fonts'))

        for font in self.font_idents:
            label = self.descriptor_label(font)
            grid.add(label)
            fb = self.font_button(font)
            grid.attach_next_to(fb, label, Gtk.PositionType.RIGHT, 1, 1)
            self.font_buttons.append(fb)

        # Font Colors
        grid.add(self.bold_label('Colors'))

        for c in self.color_idents:
            label = self.descriptor_label(c)
            grid.add(label)
            cb = self.color_button(c, c == 'Selection Background Color')
            grid.attach_next_to(cb, label, Gtk.PositionType.RIGHT, 1, 1)
            self.color_buttons.append(cb)

        # Reset to Defaults Button
        reset_button = Gtk.Button(label="Reset to defaults")
        reset_button.connect("clicked", self.confirm_and_reset_defaults)

        # The empty labels are just space fillers for the reset to defaults button
        grid.add(Gtk.Label(""))
        grid.add(reset_button)
        grid.add(Gtk.Label(""))

        return grid

    def font_button(self, pane):
        fb = Gtk.FontButton(title=pane, font_name=self.choices[pane])
        fb.connect('font-set', self.font_switched, pane)
        return fb

    def font_switched(self, button, pane):
        self.choices[pane] = button.get_font_name()

    def view_combo_box(self):
        views = ['Two-Pane', 'Three-Pane']
        cb = Gtk.ComboBoxText()
        for view in views:
            cb.append_text(view)

        cb.set_active(views.index(self.choices['View']))
        cb.connect('changed', self.view_switched)
        return cb

    def view_switched(self, combo):
        self.choices['View'] = combo.get_active_text()

    def color_button(self, name, use_alpha):
        rgba = Gdk.RGBA()
        rgba.parse(self.choices[name])
        cb = Gtk.ColorButton.new_with_rgba(rgba)
        cb.set_use_alpha(use_alpha)
        cb.connect('color-set', self.color_switched, name)
        return cb

    def color_switched(self, cc, name):
        self.choices[name] = cc.get_rgba().to_string()

    def confirm_and_reset_defaults(self, widget):
        if utilityFunctions.decision_popup(self.parent, 'Reset Appearance to Defaults',
                          'Are you sure you want to reset your Appearance preferences to default values?'):
            self.choices = ConfigManager.default_appearance_preferences()

            # Visual Effects
            # Set the view combo box to "Double" which is the second entry
            model = self.view_box.get_model()
            self.view_box.set_active_iter(model.iter_next(model.get_iter_first()))

            # Set the font buttons to display the default font values
            for fb, fi in zip(self.font_buttons, self.font_idents):
                fb.set_font_name(self.choices[fi])
                fb.emit("font_set")

            # Set the color buttons to display the default color values
            for cb, ci in zip(self.color_buttons, self.color_idents):
                cb.set_rgba(utilityFunctions.string_to_RGBA(self.choices[ci]))




class FeedsPreferences(PreferencesCategory):
    """
    Displays feeds and allows for editing of the list and feed information.
    I'm going to have feed information be edited through a new dialog (although that is kind of annoying)
    because it simplifies how to catch/verify changes.
    """
    def __init__(self, parent, preferences):
        super().__init__(preferences, 'Feeds')
        self.parent = parent
        self.info_box, self.info_scroll = self.info_placeholder()
        self.feed_list = Gtk.ListStore(str, str)
        self.view = Gtk.TreeView(model=self.feed_list)

    def create_display_area(self):
        grid = Gtk.Grid(column_homogeneous=True, row_homogeneous=True)

        # TODO: Making a lot of buttons in nearly the same way, a general factory method would be nice
        remove_button = utilityFunctions.make_button(theme_icon_string="remove", tooltip_text="Remove selected feed",
                                                     signal="clicked", function=self.remove_selection)

        add_button = utilityFunctions.make_button(theme_icon_string="add", tooltip_text="Add a feed",
                                                  signal="clicked", function=self.add_feed)

        grid.attach(remove_button, 0, 0, 1, 1)
        grid.attach(add_button, 1, 0, 1, 1)

        # List of Feeds
        for name in self.choices:
            self.feed_list.append([name, self.choices[name]])

        column = Gtk.TreeViewColumn("Feeds", Gtk.CellRendererText(), text=0)
        column.set_alignment(.5)
        self.view.append_column(column)
        select = self.view.get_selection()
        select.connect("changed", self.feed_selected)
        scroll = Gtk.ScrolledWindow()
        scroll.add(self.view)
        scroll.set_size_request(50, 100)
        frame = Gtk.Frame()
        frame.add(scroll)

        grid.attach(frame, 0, 1, 2, 10)
        grid.attach(self.info_box, 2, 0, 3, 11)

        if len(self.feed_list) > 0:
            self.attempt_selection(self.view.get_selection(), 0)
        return grid

    def info_placeholder(self):
        """
        The GUI component that will be populated with feed information when a feed is selected.
        """
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        # Feed information label
        info_label = Gtk.Label()
        info_label.set_markup('<b>' + 'Feed Information' + '</b>')
        info_label.set_alignment(0.5, 0)  # Center it


        sw = Gtk.ScrolledWindow()
        sw.set_policy(Gtk.PolicyType.ALWAYS, Gtk.PolicyType.ALWAYS)
        sw.set_size_request(100, 100)
        vbox.pack_start(info_label, False, False, 5)
        vbox.pack_start(sw, True, True, 0)
        return vbox, sw

    def create_feed_info(self, feed_name, iter):
        """
        Display the information related to a feed.
        """
        # Information Grid
        grid = Gtk.Grid(row_spacing=3, orientation=Gtk.Orientation.VERTICAL, column_homogeneous=True)

        # Feed label
        label_desc = self.bold_label('Label', left=True)
        grid.add(label_desc)
        grid.attach_next_to(self.descriptor_label(feed_name), label_desc, Gtk.PositionType.RIGHT, 4, 1)

        # Feed URI
        uri_desc = self.bold_label('URI', left=True)
        grid.add(uri_desc)
        uri = self.feed_list[iter][1]
        grid.attach_next_to(self.descriptor_label(uri), uri_desc, Gtk.PositionType.RIGHT, 4, 1)

        return grid

    def feed_selected(self, selection):
        model, iter = selection.get_selected()
        if iter:
            feed_name = model[iter][0]

            # Remove old info
            for child in self.info_scroll:
                child.destroy()

            # Display new information
            self.info_scroll.add(self.create_feed_info(feed_name, iter))
            self.info_scroll.show_all()

    def remove_selection(self, button):
        selection = self.view.get_selection()
        model, iter = selection.get_selected()
        if iter:
            model.remove(iter)
            # Commented out the attempt to move selection because of GTK-critical error.
            # Try to move the selection to the next or previous feed.
            #if not self.attempt_selection(selection, iter):
            #  self.attempt_selection(selection, model.iter_parent(iter))

    def add_feed(self, button):
        """
        Note: This only adds the feed to the temporary feed list in the preferences window.
        """
        dialog = AddFeed(self.parent)
        response = dialog.get_response(self.feed_list)
        if response:
            if response.overwrite:
                for i, feed in enumerate(self.feed_list):
                    if response.name == feed[0]:
                        self.feed_list.remove(self.feed_list.get_iter(i))
                        break
            iter = self.feed_list.append([response.name, response.uri])
            self.view.get_selection().select_iter(iter)  # Selects the feed just added.

    def attempt_selection(self, selector, iter):
        if iter is not None:
            try:
                if type(iter) == int:
                    selector.select_path(iter)
                else:  # TreeIter
                    selector.select_iter(iter)
            except IndexError:
                return False
            return True

    def gather_choices(self):
        self.choices = OrderedDict()
        for p in self.feed_list:
            self.choices[p[0]] = p[1]
        return self.choices


class FiltrationPreferences(PreferencesCategory):
    def __init__(self, preferences):
        super().__init__(preferences, 'Filtration')

    def create_display_area(self):
        return self.bold_label("Not implemented yet.")


class RetrievalPreferences(PreferencesCategory):
    def __init__(self, config):
        super().__init__(config, 'Retrieval')

    def create_display_area(self):
        return self.bold_label("Not implemented yet.")