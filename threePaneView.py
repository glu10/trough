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

from typing import Dict

from gi import require_version

require_version('Gtk', '3.0')
require_version('Gdk', '3.0')
from gi.repository import Gtk

from newsStore import NewsStore
from twoPaneView import TwoPaneView


class ThreePaneView(TwoPaneView):  # TODO: Composition over inheritance
    """
    Pane 1: Feed names.
    Pane 2: Items of selected feed name.
    Pane 3: Contents of the selected item.
    """

    def __init__(self, news_store: NewsStore, appearance_preferences: Dict[str, str]):
        self.news_store = news_store
        self.label_view = self.create_view(self.news_store.model(), 'Feeds', text=0)
        self.label_view.set_name('labelview')  # For CSS
        self.label_scroll = self.create_headline_box(self.label_view, 20, 200)
        self.label_changed_handler = None
        self.toggle_label_listening()
        self.label_view.grab_focus()
        self.focused_index = 0

        super().__init__(news_store, appearance_preferences)

        self.top_pane = Gtk.Paned(orientation=Gtk.Orientation.HORIZONTAL)
        self.top_pane.pack1(self.label_scroll, resize=False, shrink=False)
        self.top_pane.pack2(self.headline_content_pane, resize=False, shrink=False)  # essentially packs in a Two-Pane

    @staticmethod
    def create_view(model: Gtk.TreeModel, label: str, **kwargs) -> Gtk.TreeView:
        view = Gtk.TreeView(model=model)
        cell = Gtk.CellRendererText()
        col = Gtk.TreeViewColumn(label, cell, **kwargs)
        view.append_column(col)
        return view

    @staticmethod
    def create_headline_view(store: NewsStore) -> Gtk.TreeView:
        return ThreePaneView.create_view(store, 'Headlines', text=1)

    def toggle_label_listening(self) -> None:
        self.label_changed_handler = self.toggle_tree_view_listening(self.label_view,
                                                                     self.label_changed_handler,
                                                                     self.show_new_headlines)

    def change_position(self, delta: int) -> None:
        changed_pos = self.focused_index + delta
        if 0 <= changed_pos < 3:
            widgets = [self.label_view, self.headline_view, self.content_view]
            widgets[changed_pos].grab_focus()
            self.focused_index = changed_pos

    def top_level(self) -> Gtk.Container:
        return self.top_pane

    def show_new_content(self, tree_view: Gtk.TreeView) -> None:
        self.focused_index = 1  # Correctly anchors left/right keyboard shortcut if the mouse was used.
        super().show_new_content(tree_view)

    def show_new_headlines(self, tree_view: Gtk.TreeView) -> None:
        self.focused_index = 0  # Correctly anchors left/right keyboard shortcut if the mouse was used.
        model, it = tree_view.get_selection().get_selected()
        if model and it:
            self.last_item_feed_name = model[it][0]
            self.headline_view.do_unselect_all(self.headline_view)
