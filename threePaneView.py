"""
    Trough - a GTK+ RSS news reader

    Copyright (C) 2016 Andrew Asp
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
from gi.repository import Gtk, Gdk
from twoPaneView import TwoPaneView


class ThreePaneView(TwoPaneView):
    """ Pane 1: Feed names. Pane 2: Items of selected feed name. Pane 3: Contents of the selected item.
        Panes 2-3 are TwoPaneView, slightly modified through overridden functions. """
    def __init__(self, preferences, gatherer):
        self.label_store = Gtk.ListStore(str)
        self.label_view = self.create_view(self.label_store, 'Feed', text=0)
        self.label_scroll = self.create_headline_box(self.label_view, 20, 200)
        self.label_changed_handler = None
        self.toggle_label_listening()
        self.label_view.grab_focus()
        self.focused_index = 0

        super().__init__(preferences, gatherer)  # calling after creating label_view because of update_appearance()

        self.top_pane = Gtk.Paned(orientation=Gtk.Orientation.HORIZONTAL)
        self.top_pane.pack1(self.label_scroll, resize=False, shrink=False)
        self.top_pane.pack2(self.headline_content_pane, resize=False, shrink=False)  # essentially packs in a Two-Pane

    @staticmethod
    def create_view(store, label, **kwargs):
        view = Gtk.TreeView(model=store)
        cell = Gtk.CellRendererText()
        col = Gtk.TreeViewColumn(label, cell, **kwargs)
        view.append_column(col)
        return view

    @staticmethod
    def create_headline_view(store):
        return ThreePaneView.create_view(store, 'Headline', text=0, foreground_rgba=2)

    @staticmethod
    def create_headline_store():
        return Gtk.ListStore(str, int, Gdk.RGBA)

    def toggle_label_listening(self):
        self.label_changed_handler = self.toggle_tree_view_listening(self.label_view,
                                                                     self.label_changed_handler,
                                                                     self.show_new_headlines)

    def change_position(self, delta):
        changed_pos = self.focused_index + delta
        if 0 <= changed_pos < 3:
            widgets = [self.label_view, self.headline_view, self.content_view]
            widgets[changed_pos].grab_focus()
            self.focused_index = changed_pos

    def refresh(self):
        self.clear_store(self.label_store, self.toggle_label_listening)
        super().refresh()

    def top_level(self):
        return self.top_pane

    def get_info_from_headline(self, headline):
        self.last_item_index = headline[1]

    def color_headline(self, headline, color):
        headline[2] = color

    def show_new_content(self, tree_view):
        self.focused_index = 1  # Correctly anchors left/right keyboard shortcut if the mouse was used.
        super().show_new_content(tree_view)

    def show_new_headlines(self, tree_view):
        self.focused_index = 0  # Correctly anchors left/right keyboard shortcut if the mouse was used.
        model, it = tree_view.get_selection().get_selected()
        if model and it:
            self.last_item_feed_name = model[it][0]
            self.headline_view.do_unselect_all(self.headline_view)
            self.clear_store(self.headline_store, self.toggle_headline_listening)
            feed = self.preferences.get_feed(self.last_item_feed_name)
            feed.sort_items()  # drives read stories to the bottom of the list
            if feed:
                ap = self.appearance()
                for pos, item in enumerate(feed.items):
                    self.headline_store.append([item.title, pos, item.get_color(ap)])

    def receive_feed(self, feed):
        if self.mark_feed(feed):
            self.label_store.append([feed.name])

    def update_appearance(self, appearance_dict):
        model = self.headline_view.get_model()
        feed = self.preferences.get_feed(self.last_item_feed_name)
        for it in model:
            item = feed.items[it[1]]
            self.color_headline(it, item.get_color(appearance_dict))


