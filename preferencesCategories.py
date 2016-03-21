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
from feedDialog import FeedDialog
import utilityFunctions
from preferences import Preferences
from feed import Feed
from filter import Filter


class PreferencesCategory(metaclass=ABCMeta):

    def __init__(self, preferences, label):
        self.choices = dict()
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

        self.color_idents = ['Font Color', 'Background Color', 'Selection Font Color', 'Selection Background Color',
                             'Read Color', 'Filtered Color']

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
            cb = self.color_button(c)
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

    def color_button(self, name):
        rgba = Gdk.RGBA()
        rgba.parse(self.choices[name])
        cb = Gtk.ColorButton.new_with_rgba(rgba)
        cb.set_use_alpha(True)
        cb.connect('color-set', self.color_switched, name)
        return cb

    def color_switched(self, cc, name):
        self.choices[name] = cc.get_rgba().to_string()

    def confirm_and_reset_defaults(self, widget):
        if utilityFunctions.decision_popup(self.parent, 'Reset Appearance to Defaults',
                          'Are you sure you want to reset your Appearance preferences to default values?'):
            self.choices = Preferences.default_appearance_preferences()

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
        remove_button = utilityFunctions.make_button(theme_icon_string="remove", tooltip_text="Remove selected feed",
                                                     signal="clicked", function=self.remove_selection)

        add_button = utilityFunctions.make_button(theme_icon_string="add", tooltip_text="Add a feed",
                                                  signal="clicked", function=self.add_feed)

        edit_button = utilityFunctions.make_button(theme_icon_string="gtk-edit", tooltip_text="Edit selected feed",
                                                   signal="clicked", function=self.edit_feed)

        button_hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        button_hbox.pack_start(remove_button, False, False, 0)
        button_hbox.pack_start(add_button, False, False, 0)
        button_hbox.pack_start(edit_button, False, False, 0)

        # List of Feeds
        for feed in self.choices.values():
            self.feed_list.append([feed.name, feed.uri])

        column = Gtk.TreeViewColumn('', Gtk.CellRendererText(), text=0)
        self.view.append_column(column)
        self.view.set_headers_visible(False)
        column_title = Gtk.Label()
        column_title.set_markup('<b> Feeds </b>')
        select = self.view.get_selection()
        select.connect("changed", self.feed_selected)
        scroll = Gtk.ScrolledWindow()
        scroll.add(self.view)
        feed_frame = Gtk.Frame()

        feed_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        feed_vbox.pack_start(column_title, False, False, 5)
        feed_vbox.pack_start(scroll, True, True, 0)
        feed_frame.add(feed_vbox)

        info_frame = Gtk.Frame()
        info_frame.add(self.info_box)

        feed_hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        feed_hbox.pack_start(feed_frame, True, True, 0)
        feed_hbox.pack_end(info_frame, True, True, 1)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        vbox.pack_start(button_hbox, False, False, 0)
        vbox.pack_end(feed_hbox, True, True, 0)

        if len(self.feed_list) > 0:
            self.attempt_selection(self.view.get_selection(), 0)

        return vbox

    @staticmethod
    def info_placeholder():
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
        vbox.pack_start(info_label, False, False, 5)
        vbox.pack_start(sw, True, True, 0)
        return vbox, sw

    def create_feed_info(self, feed_name, iter):
        """
        Display the information related to a feed.
        """
        name_desc = self.bold_label('Name', left=True)
        name_display = self.descriptor_label(feed_name)
        name_display.set_selectable(True)

        uri_desc = self.bold_label('URI', left=True)
        uri = self.feed_list[iter][1]
        uri_display = self.descriptor_label(uri)
        uri_display.set_selectable(True)

        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        label_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        value_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        label_vbox.add(name_desc)
        value_vbox.add(name_display)

        label_vbox.add(uri_desc)
        value_vbox.add(uri_display)

        hbox.pack_start(label_vbox, False, False, 3)
        hbox.pack_start(value_vbox, True, True, 0)
        return hbox

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
        dialog = FeedDialog(self.parent)
        response = dialog.get_response(self.feed_list)
        if response:
            if response.overwrite:  # Are we replacing a different feed with this one because conflicting name/URI?
                for i, feed in enumerate(self.feed_list):
                    if response.name == feed[0]:
                        self.feed_list.remove(self.feed_list.get_iter(i))
                        break
            iter = self.feed_list.append([response.name, response.uri])
            self.view.get_selection().select_iter(iter)  # Selects the feed just added.

    def edit_feed(self, widget):
        selection = self.view.get_selection()
        model, iter = selection.get_selected()
        if iter:
            """ Going to spawn an Add feed dialog, but with the current feed values pre-filled. """
            name = model[iter][0]
            uri = model[iter][1]

            dialog = FeedDialog(self.parent, feed=Feed(name, uri))
            dialog.set_title('Edit Feed')
            response = dialog.get_response(self.feed_list)
            if response:
                model[iter][0] = response.name
                model[iter][1] = response.uri
                self.feed_selected(selection)
            return None

    @staticmethod
    def attempt_selection(selector, iter):
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
        temp = dict()

        # Create a new feed object dict from the possibly changed information
        for feed in self.feed_list:  # For each feed in our temporary ListStore
            feed_name = feed[0]
            feed_uri = feed[1]
            temp[feed_name] = Feed(feed_name, feed_uri)

            if feed_name in self.choices:
                if self.choices[feed_name].uri == feed_uri:
                    temp[feed_name].items = self.choices[feed_name].items
        return temp


class FiltrationPreferences(PreferencesCategory):
    def __init__(self, parent, preferences):
        super().__init__(preferences, 'Filtration')
        self.parent = parent
        self.filter_list = Gtk.ListStore(str, bool)
        self.view = Gtk.TreeView(model=self.filter_list)

    def create_display_area(self):
        filter_column = Gtk.TreeViewColumn('Trigger', Gtk.CellRendererText(), text=0)
        filter_column.set_alignment(.5)
        self.view.append_column(filter_column)

        capitalization_column = Gtk.TreeViewColumn('Case sensitive', Gtk.CellRendererText(), text=1)
        self.view.append_column(capitalization_column)

        for f in self.choices:
            self.filter_list.append([f.trigger, f.case_sensitive])

        view_title = Gtk.Label()
        view_title.set_markup('<b>Filters</b>')

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)

        remove_button = utilityFunctions.make_button(theme_icon_string="remove", tooltip_text="Remove selected filter",
                                                     signal="clicked", function=self.remove_filter)
        add_button = utilityFunctions.make_button(theme_icon_string="add", tooltip_text="Add a filter",
                                                  signal="clicked", function=self.add_filter)
        edit_button = utilityFunctions.make_button(theme_icon_string="gtk-edit", tooltip_text="Edit selected filter",
                                                   signal="clicked", function=self.edit_filter)
        hbox.add(remove_button)
        hbox.add(add_button)
        hbox.add(edit_button)

        scroll = Gtk.ScrolledWindow()
        scroll.add(self.view)
        scroll_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        scroll_vbox.pack_start(view_title, False, False, 5)
        scroll_vbox.pack_start(scroll, True, True, 0)
        frame = Gtk.Frame()
        frame.add(scroll_vbox)

        vbox.pack_start(hbox, False, False, 0)
        vbox.pack_end(frame, True, True, 0)
        return vbox

    def add_filter(self, button):
        fd = FilterDialog('Add a filter', self.parent, self.filter_list)
        r = fd.get_response()
        if r:
            self.filter_list.append(r)

    def edit_filter(self, button):
        selection = self.view.get_selection()
        model, iter = selection.get_selected()
        if iter:
            fd = FilterDialog('Edit filter', self.parent, self.filter_list)
            r = fd.get_response(model[iter])
            if r:
                model[iter] = r

    def remove_filter(self, button):
        selection = self.view.get_selection()
        model, iter = selection.get_selected()
        if iter:
            model.remove(iter)

    def gather_choices(self):
        return [Filter(row[0], row[1]) for row in self.filter_list]


# TODO: FilterDialog shares a lot of functionality with FeedDialog. Prevent duplication by making a common parent class?
class FilterDialog(Gtk.Dialog):
    def __init__(self, title, parent, filter_list):
        Gtk.Dialog.__init__(self, title, parent, 0, (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                                     Gtk.STOCK_OK, Gtk.ResponseType.OK))

        self.filter_list = filter_list  # used for checking uniqueness
        self.label = Gtk.Label('Filter  ', xalign=0)
        self.entry = Gtk.Entry(hexpand=True)
        self.check = Gtk.CheckButton(label='Capitalization matters')
        self.error_label = Gtk.Label()
        self.error_label.set_markup('<span color="red">Fill in the missing information.</span>')

        # Make the ok button the default button so it can be triggered by the enter key.
        ok_button = self.get_widget_for_response(response_id=Gtk.ResponseType.OK)
        ok_button.set_can_default(True)
        ok_button.grab_default()
        self.entry.set_activates_default(True)

        box = self.get_content_area()
        hbox = Gtk.Box(Gtk.Orientation.HORIZONTAL)
        hbox.add(self.label)
        hbox.add(self.entry)
        box.pack_start(hbox, True, True, 10)
        box.add(self.check)
        box.add(self.error_label)
        box.show_all()
        self.error_label.set_visible(False)

    def get_response(self, previous=None):
        previous_text = None
        if previous:
            previous_text = previous[0]
            previous_capitalization = previous[1]
            self.entry.set_text(previous_text)
            self.check.set_active(previous_capitalization)

        return_val = None
        while True:
            response = self.run()
            text = self.entry.get_text().strip()
            if response == Gtk.ResponseType.OK:
                if text == '':
                    self.toggle_error(True)
                elif text == previous_text:
                    break  # No change occurred, so nothing needs to be done.
                elif previous or self.is_unique(text):
                    return_val = [text, self.check.get_active()]
                    break
                else:
                    utilityFunctions.warning_popup(self, 'Error', 'The trigger ' + text + ' already exists.')
                    self.toggle_error(False)

            elif response == Gtk.ResponseType.CANCEL or response == Gtk.ResponseType.NONE:
                break

        self.destroy()
        return return_val

    def toggle_error(self, show):
        if show:
            self.label.set_markup('<span color="red">Filter  </span>')
            self.error_label.set_visible(True)
        else:
            self.label.set_markup('Filter  ')
            self.error_label.set_visible(False)

    def is_unique(self, word):
        for row in self.filter_list:
            if row[0] == word:
                return False
        return True
