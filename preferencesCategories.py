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
from typing import Any, Dict, Iterable, Union

from gi import require_version

require_version('Gtk', '3.0')
from gi.repository import Gdk, Gtk

from cache import Cache
from feed import Feed
from feedDialog import FeedDialog
from preferences import Preferences
import utilityFunctions


class PreferencesCategory(metaclass=ABCMeta):
    padding = 10

    def __init__(self, preferences: Dict[str, Any], label: str):
        self.choices = dict()
        if label in preferences:
            self.choices = preferences[label].copy()  # Work on copy
        self.label = label

    @abstractmethod
    def create_display_area(self) -> Gtk.Container:
        """
        Create the GUI components that will be in the preferences page
        """

    def create_section(self, label_text: str, child: Gtk.Widget) -> Gtk.Box:
        label = Gtk.Label()
        label.set_markup('<b>' + label_text + '</b>')
        label.set_alignment(0, .2)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        vbox.add(label)
        vbox.add(child)
        return vbox

    def create_section_options(self, label_texts: Iterable[str], actionables: Iterable[Gtk.Widget]) -> Gtk.Box:
        labels_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        actionables_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        for label_text in label_texts:
            labels_vbox.pack_start(
                self.descriptor_label(label_text),
                True,
                False,
                0)

        for actionable in actionables:
            actionables_vbox.pack_start(actionable, True, False, 0)

        hbox = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            homogeneous=True)
        hbox.add(labels_vbox)
        hbox.add(actionables_vbox)
        return hbox

    def surround_with_padding(self, to_be_padded: Gtk.Widget) -> Gtk.Alignment:
        alignment = Gtk.Alignment()
        alignment.set_padding(
            self.padding,
            self.padding,
            self.padding,
            self.padding)
        alignment.add(to_be_padded)
        return alignment

    def gather_choices(self):
        return self.choices

    def bold_label(self, text: str, left: bool = False) -> Gtk.Label:
        """
        Label used in a preferences category to title a class of selections
        """
        label = Gtk.Label()
        label.set_markup('<b>' + text + '</b>')
        if left:
            label.set_alignment(0, .5)
            label.set_padding(5, 0)

        return label

    def descriptor_label(self, text: str) -> Gtk.Label:
        """
        Label used in a preferences category
        to label an individual item in a class of selections
        """
        label = Gtk.Label(text)
        label.set_halign(Gtk.Align.END)
        label.set_margin_end(20)
        return label


class AppearancePreferences(PreferencesCategory):
    """
    Views
     - Two-Pane
     - Three-Pane
    Fonts
     - Category
     - Headline
     - Story
    Colors
     - Font Color
     - Background Color
     - Selection Font Color
     - Selection Background Color
     - Read Color
    Reset to Defaults Button
    """

    def __init__(self, parent: Any, preferences: Dict[str, Any]):
        super().__init__(preferences, 'Appearance')
        self.parent = parent

        self.view_box = None

        self.font_idents = ['Category Font', 'Headline Font', 'Story Font']
        self.font_buttons = [self.font_button(i) for i in self.font_idents]

        self.color_idents = [
            'Font Color',
            'Background Color',
            'Selection Font Color',
            'Selection Background Color',
            'Read Color',
        ]
        self.color_buttons = [self.color_button(i) for i in self.color_idents]

    def create_display_area(self) -> Gtk.Alignment:
        top_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)

        # View selection
        self.view_box = self.view_combo_box()
        view_vbox = self.create_section(
            'View',
            self.create_section_options([''], [self.view_box]))
        top_vbox.add(view_vbox)

        # Font selection
        font_section = self.create_section(
            'Fonts',
            self.create_section_options(self.font_idents, self.font_buttons))
        top_vbox.add(font_section)

        # Font Colors
        color_section = self.create_section(
            'Colors',
            self.create_section_options(
                self.color_idents,
                self.color_buttons))
        top_vbox.add(color_section)

        # Reset to Defaults Button
        reset_button = Gtk.Button(label='Reset to defaults')
        reset_button.connect('clicked', self.confirm_and_reset_defaults)
        top_vbox.add(reset_button)

        return self.surround_with_padding(top_vbox)

    def font_button(self, font_title: str) -> Gtk.FontButton:
        fb = Gtk.FontButton(title=font_title, font_name=self.css_to_font_name(self.choices[font_title]))
        fb.set_font_name(self.css_to_font_name(self.choices[font_title]))
        fb.connect('font-set', self.font_switched)
        return fb

    def font_switched(self, button: Gtk.FontButton) -> None:
        self.choices[button.get_title()] = self.font_name_to_css(button.get_font_name())

    def font_name_to_css(self, font_name: str) -> str:
        font_title, font_size = font_name.replace(',', '').rsplit(maxsplit=1)
        return '{}px {}'.format(font_size, font_title)

    def css_to_font_name(self, font_css: str) -> str:
        font_size, remaining = font_css.split(maxsplit=1)
        font_size = ''.join(filter(str.isdigit, font_size))  # remove units
        font_title = remaining.split(', ', maxsplit=1)[0]  # Ignore a font family, if provided
        return '{} {}'.format(font_title, font_size)

    def view_combo_box(self) -> Gtk.ComboBoxText:
        views = ['Two-Pane', 'Three-Pane']
        cb = Gtk.ComboBoxText()
        for view in views:
            cb.append_text(view)

        cb.set_active(views.index(self.choices['View']))
        cb.connect('changed', self.view_switched)
        return cb

    def view_switched(self, combo: Gtk.ComboBoxText) -> None:
        self.choices['View'] = combo.get_active_text()

    def color_button(self, name) -> Gtk.ColorButton:
        rgba = Gdk.RGBA()
        rgba.parse(self.choices[name])
        cb = Gtk.ColorButton.new_with_rgba(rgba)
        cb.set_use_alpha(True)
        cb.connect('color-set', self.color_switched, name)
        return cb

    def color_switched(self, cc: Gtk.ColorChooser, name: str) -> None:
        self.choices[name] = cc.get_rgba().to_string()

    def confirm_and_reset_defaults(self, widget: Gtk.Widget) -> None:
        if utilityFunctions.decision_popup(
                self.parent,
                'Reset appearance to defaults?',
                'Are you sure you want to reset your appearance preferences to default values?'):
            self.choices = Preferences.default_appearance_preferences()

            # Visual Effects
            # Set the view combo box to "Double" which is the second entry
            model = self.view_box.get_model()
            self.view_box.set_active_iter(
                model.iter_next(
                    model.get_iter_first()))

            # Set the font buttons to display the default font values
            for fb, fi in zip(self.font_buttons, self.font_idents):
                fb.set_font_name(self.css_to_font_name(self.choices[fi]))

            # Set the color buttons to display the default color values
            for cb, ci in zip(self.color_buttons, self.color_idents):
                cb.set_rgba(utilityFunctions.string_to_RGBA(self.choices[ci]))


class FeedsPreferences(PreferencesCategory):
    """
    Displays feeds and allows for editing of the list and feed information.
    Feed information will be edited through a new dialog because it simplifies
    how to catch/verify changes.
    """

    def __init__(self, parent, preferences: Dict[str, Any], cache: Cache):
        super().__init__(preferences, 'Feeds')
        self.parent = parent
        self.preferences = preferences
        self.info_box, self.info_scroll = self.info_placeholder()
        self.feed_list = Gtk.ListStore(str, str)
        self.view = Gtk.TreeView(model=self.feed_list)
        self.cache = cache  # only used for being cleared

    def create_display_area(self) -> Gtk.Alignment:
        remove_button = utilityFunctions.make_button(
            theme_icon_string='remove',
            tooltip='Remove selected feed',
            signal='clicked',
            signal_func=self.remove_selection)

        add_button = utilityFunctions.make_button(
            theme_icon_string='add',
            tooltip='Add a feed',
            signal='clicked',
            signal_func=self.add_feed)

        edit_button = utilityFunctions.make_button(
            theme_icon_string='gtk-edit',
            tooltip='Edit selected feed',
            signal='clicked',
            signal_func=self.edit_feed)

        clear_cache_button = utilityFunctions.make_button(
            tooltip='Clears all scraped articles and read history information',
            signal='clicked',
            signal_func=self.clear_cache)
        clear_cache_button.set_label('Clear cache')

        button_hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        button_hbox.pack_start(remove_button, False, False, 0)
        button_hbox.pack_start(add_button, False, False, 0)
        button_hbox.pack_start(edit_button, False, False, 0)
        button_hbox.pack_end(clear_cache_button, False, False, 0)

        # List of Feeds
        for feed in self.choices.values():
            self.feed_list.append([feed.name, feed.uri])

        column = Gtk.TreeViewColumn('', Gtk.CellRendererText(), text=0)
        self.view.append_column(column)
        self.view.set_headers_visible(False)
        column_title = Gtk.Label()
        column_title.set_markup('<b> Feeds </b>')
        select = self.view.get_selection()
        select.connect('changed', self.feed_selected)
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

        helpful_label = Gtk.Label('New feeds appear on the next refresh.')
        helpful_label.set_line_wrap(True)
        helpful_align = Gtk.Alignment()
        helpful_align.set_padding(0, self.padding, 0, 0)
        helpful_align.add(helpful_label)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        vbox.add(helpful_align)
        vbox.add(button_hbox)
        vbox.pack_end(feed_hbox, True, True, 0)

        if len(self.feed_list) > 0:
            self.attempt_selection(self.view.get_selection(), 0)

        return self.surround_with_padding(vbox)

    @staticmethod
    def info_placeholder() -> (Gtk.Box, Gtk.ScrolledWindow):
        """
        Will be populated with feed information when a feed is selected.
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

    def create_feed_info(self, feed_name: str, it: Gtk.TreeIter) -> Gtk.Box:
        """
        Display the information related to a feed.
        """
        name_desc = self.bold_label('Name', left=True)
        name_display = self.descriptor_label(feed_name)
        name_display.set_selectable(True)

        uri_desc = self.bold_label('URI', left=True)
        uri = self.feed_list[it][1]
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

    def feed_selected(self, selection: Gtk.TreeSelection) -> None:
        model, it = selection.get_selected()
        if it:
            feed_name = model[it][0]

            # Remove old info
            for child in self.info_scroll:
                child.destroy()

            # Display new information
            self.info_scroll.add(self.create_feed_info(feed_name, it))
            self.info_scroll.show_all()

    def remove_selection(self, button: Gtk.Button) -> None:
        selection = self.view.get_selection()
        model, it = selection.get_selected()
        if it:
            model.remove(it)

    def add_feed(self, button: Gtk.Button) -> None:
        """
        Note: Change only appears when preferences are saved.
        """
        dialog = FeedDialog(self.parent, feed_container=self.feed_list)
        feed = dialog.get_response()
        if feed:
            self.find_and_remove_feed(feed)  # Prevents duplicate names
            it = self.feed_list.append(feed.to_value_list())
            self.view.get_selection().select_iter(it)  # Selects the feed just added.

    def edit_feed(self, widget: Gtk.Widget) -> None:
        selection = self.view.get_selection()
        model, it = selection.get_selected()
        if it:
            """ Spawn a feed dialog, but with the current feed values pre-filled. """
            name = model[it][0]
            uri = model[it][1]

            dialog = FeedDialog(self.parent, feed_container=self.feed_list, feed=Feed(name, uri))
            feed = dialog.get_response()
            if feed:
                model[it][0] = feed.name
                model[it][1] = feed.uri
                self.feed_selected(selection)

    def find_and_remove_feed(self, feed: Feed) -> None:
        for i, row in enumerate(self.feed_list):
            if feed.name == row[0]:
                self.feed_list.remove(self.feed_list.get_iter(i))
                break

    @staticmethod
    def attempt_selection(selector, it: Union[int, Gtk.TreeIter]) -> bool:
        if it is None:
            return False
        try:
            t = type(it)
            if t == int:
                selector.select_path(it)
            elif t == Gtk.TreeIter:
                selector.select_iter(it)
            else:
                return False
        except IndexError:
            return False
        return True

    def gather_choices(self) -> Dict[str, Feed]:
        feeds = dict()

        for feed in self.feed_list:  # For each feed in our temporary ListStore
            name = feed[0]
            feeds[name] = Feed(name=name, uri=feed[1])
        return feeds

    def clear_cache(self, button: Gtk.Button) -> None:
        first = 'Clear the cache?'
        second = ('All previously scraped articles will be lost when you refresh or exit, '
                  'as well as any information regarding what articles you have read.')

        if utilityFunctions.decision_popup(self.parent, first, second):
            self.cache.clear()
