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

from gi.repository import Gdk, Gtk, Pango

from newsView import NewsView
from textFormat import TextFormat
from utilityFunctions import string_to_RGBA


class TwoPaneView(NewsView):
    """ Pane 1: A list of RSS items (Feed name | Headline). Pane 2: Contents of the selected item. """
    def __init__(self, preferences, gatherer):
        super().__init__(preferences, gatherer)

        # GUI components
        self.headline_store = self.create_headline_store()
        self.headline_view = self.create_headline_view(self.headline_store)
        self.headline_view.set_name('headlineview')  # For CSS
        self.headline_scroll = self.create_headline_box(self.headline_view, 400, 200)
        self.headline_changed_handler = None
        self.toggle_headline_listening()

        self.content_scroll, self.content_view = self.create_content_box()
        self.headline_content_pane = Gtk.Paned(orientation=Gtk.Orientation.HORIZONTAL)
        self.headline_content_pane.pack1(self.headline_scroll, resize=False, shrink=False)  # Left
        self.headline_content_pane.pack2(self.content_scroll, resize=True, shrink=True)  # Right

        self.update_appearance(preferences.appearance_preferences())

    @staticmethod
    def create_headline_store():
        return Gtk.ListStore(str, str, int, Gdk.RGBA)  # feed name, item title, item position, item color

    @staticmethod
    def clear_store(store, listening_toggle_func):  # TODO: Find better way to clear store
        """
        There has to be a better way to do this. Clearing the store causes the cursor-changed signal to get
        called over and over and over if we have a signal listener for it (which is horribly wasteful),
        so just toggle the listener off then back on to avoid the problem.
        """
        listening_toggle_func()
        store.clear()
        listening_toggle_func()

    @staticmethod
    def create_headline_view(headline_store):
        tree_view = Gtk.TreeView(model=headline_store)
        columns = ('Feeds', 'Headlines')
        for i in range(len(columns)):
            cell = Gtk.CellRendererText()
            if i == 0:  # Label
                cell.props.weight_set = True
                cell.props.weight = Pango.Weight.BOLD
            col = Gtk.TreeViewColumn(columns[i], cell, text=i, foreground_rgba=3)
            tree_view.append_column(col)
        return tree_view

    @staticmethod
    def create_headline_box(tree_view, width, height):
        headline_scroll = Gtk.ScrolledWindow()
        headline_scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.ALWAYS)
        headline_scroll.set_size_request(width, height)
        headline_scroll.add(tree_view)
        return headline_scroll

    @staticmethod
    def create_content_box():
        text_scroll = Gtk.ScrolledWindow()
        text_scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.ALWAYS)
        text_view = TextFormat.prepare_content_display(None, None)
        text_scroll.add(text_view)
        return text_scroll, text_view

    @staticmethod
    def toggle_tree_view_listening(tree_view, handler_id, function):
        if handler_id:  # The handler exists, stop listening
            tree_view.disconnect(handler_id)
            return None
        else:  # The handler doesn't exist, start listening
            return tree_view.connect('cursor-changed', function)

    def toggle_headline_listening(self):
        self.headline_changed_handler = self.toggle_tree_view_listening(self.headline_view,
                                                                        self.headline_changed_handler,
                                                                        self.show_new_content)

    def top_level(self):
        return self.headline_content_pane

    def change_position(self, delta):
        """ Switches keyboard focus between left and right pane """
        if delta < 0:
            self.headline_view.grab_focus()
        else:
            self.content_view.grab_focus()

    def refresh(self):
        self.clear_store(self.headline_store, self.toggle_headline_listening)
        TextFormat.empty(self.content_view)
        super().refresh()

    def receive_item(self, item):
            self.headline_store.append([item.feed_name, item.title, 0, item.get_color(self.appearance())])

    def get_info_from_headline(self, headline):
        self.last_item_feed_name = headline[0]
        self.last_item_index = headline[2]

    def color_headline(self, headline, color):
        headline[3] = color

    def show_new_content(self, tree_view):
        model, it = tree_view.get_selection().get_selected()
        if model and it:
            self.get_info_from_headline(model[it])
            self.color_headline(model[it], string_to_RGBA(self.appearance()['Read Color']))
            # TODO remove upcall, actually store the item information where we need it
            item = self.gatherer.item(self.last_item_feed_name, self.last_item_index)
            if item.article:
                TextFormat.prepare_content_display(item, self.content_view)
            else:
                self.gatherer.request(item)

    def update_appearance(self, appearance_dict):
        model = self.headline_view.get_model()
        for it in model:
            item = self.gatherer.item(it[0], it[2])
            if item:
                it[3] = item.get_color(appearance_dict)
            else:  # This feed was removed
                model.remove(it.iter)
