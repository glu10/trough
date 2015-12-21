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

# NOT FINISHED

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
    Views (Single/Double/Triple)
    Fonts (Category/Headline/Story)
    Colors (Font Color/Background Color)
    """
    def __init__(self, preferences):
        super().__init__(preferences, 'Appearance')

    def create_display_area(self):
        grid = Gtk.Grid(row_spacing=3, column_spacing=7, orientation=Gtk.Orientation.VERTICAL)

        # View selection
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
        fb = Gtk.FontButton(title=pane, font_name=self.choices[pane])
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

class FeedsPreferences(PreferencesCategory):
    """
    Displays feeds and allows for editing of the list and feed information.
    I'm going to have feed information be edited through a new dialog (although that is kind of annoying)
    because it simplifies how to catch/verify changes.
    """
    def __init__(self, preferences, config):
        super().__init__(preferences, 'Feeds')
        self.info_box = self.info_placeholder()
        self.feed_list = Gtk.ListStore(str, str)
        self.view = Gtk.TreeView(model=self.feed_list)
        self.config = config

    def create_display_area(self):
        grid = Gtk.Grid(column_homogeneous=True, row_homogeneous=True)

        # TODO: Making a lot of buttons in nearly the same way, a general factory method would be nice
        remove_button = Gtk.Button(tooltip_text="Remove selected feed")
        remove_icon = Gio.ThemedIcon(name="remove")
        remove_image = Gtk.Image.new_from_gicon(remove_icon, Gtk.IconSize.BUTTON)
        remove_button.add(remove_image)
        remove_button.connect("clicked", self.remove_selection)

        add_button = Gtk.Button(tooltip_text="Add a feed")
        add_icon = Gio.ThemedIcon(name="add")
        add_image = Gtk.Image.new_from_gicon(add_icon, Gtk.IconSize.BUTTON)
        add_button.add(add_image)
        add_button.connect("clicked", self.add_feed)

        grid.attach(remove_button, 0, 0, 1, 1)
        grid.attach(add_button, 1, 0, 1, 1)

        # List of Feeds # TODO: really need to just have a shared model throughout the entire program for feeds/items, will do shortly
        for name in self.choices:
            self.feed_list.append([name, self.choices[name]])

        column = Gtk.TreeViewColumn("Feeds", Gtk.CellRendererText(), text=0)
        column.set_alignment(.5)
        self.view.append_column(column)
        select = self.view.get_selection()
        select.connect("changed", self.feed_selected)
        scroll = Gtk.ScrolledWindow()
        scroll.add(self.view)
        scroll.set_size_request(50,100)
        frame = Gtk.Frame()
        frame.add(scroll)

        grid.attach(frame, 0, 1, 2, 10)
        grid.attach(self.info_box, 2, 0, 3, 11)

        if len(self.feed_list) > 0:
            self.attempt_selection(self.view.get_selection(), 0)
        return grid

    def info_placeholder(self):
        """
        If there are no feeds, or no feed is selected, just have the empty frame
        """
        label = self.bold_label('Feed Information')
        frame = Gtk.Frame(label_widget=label)
        frame.set_label_align(.5, 0)  # Centers the frame label
        return frame

    def create_feed_info(self, feed_name):
        """
        Display the information related to a feed, as well as a button to edit information.
        """
        grid = Gtk.Grid(row_spacing=3, orientation=Gtk.Orientation.VERTICAL, column_homogeneous=True)

        # Feed label
        label_desc = self.bold_label('Label', left=True)
        grid.add(label_desc)
        grid.attach_next_to(self.descriptor_label(feed_name), label_desc, Gtk.PositionType.RIGHT, 5, 1)

        # Feed URI
        uri_desc = self.bold_label('URI', left=True)
        grid.add(uri_desc)
        uri = self.choices[feed_name]  # this will change probably to self.choices[feed_name]['URI'] later
        grid.attach_next_to(self.descriptor_label(uri), uri_desc, Gtk.PositionType.RIGHT, 5, 1)
        return grid

    def feed_selected(self, selection):
        model, iter = selection.get_selected()
        if iter:
            feed_name = model[iter][0]

            # Remove old info
            for child in self.info_box:
                if type(child) == Gtk.Grid: # Type check is to avoid removing the frame label
                    child.destroy()

            # Display new information
            self.info_box.add(self.create_feed_info(feed_name))
            self.info_box.show_all()

    def remove_selection(self, button):
        selection = self.view.get_selection()
        model, iter = selection.get_selected()
        if iter:
            model.remove(iter)
            # Try to move the selection to the next or previous feed.
            #if not self.attempt_selection(selection, iter):
            #    self.attempt_selection(selection, model.iter_parent(iter))

    def add_feed(self, button):  # TODO: Redesign addFeed to allow for it to be reused here.
        pass

    def attempt_selection(self, selector, iter):
        # TODO: This is emitting a GTK-Critical error when it goes wrong, think of another way to probe?
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