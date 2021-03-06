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

from typing import Callable, Optional

from gi import require_version

require_version('Gtk', '3.0')
require_version('Gdk', '3.0')
from gi.repository import Gtk, Pango

from newsStore import NewsStore
from newsView import NewsView
from textFormat import TextFormat


class TwoPaneView(NewsView):
    """ Pane 1: A list of RSS items (Feed name | Headline). Pane 2: Contents of the selected item. """

    def __init__(self, news_store: NewsStore, appearance_preferences):
        super().__init__(news_store, appearance_preferences)

        # GUI components
        self.headline_view = self.create_headline_view(self.news_store.model())
        self.headline_view.set_name('headlineview')  # For CSS

        self.headline_scroll = self.create_headline_box(self.headline_view, 400, 200)

        self.headline_changed_handler = None
        self.toggle_headline_listening()

        self.content_scroll, self.content_view = self.create_content_box()
        self.headline_content_pane = Gtk.Paned(orientation=Gtk.Orientation.HORIZONTAL)
        self.headline_content_pane.pack1(self.headline_scroll, resize=False, shrink=False)  # Left
        self.headline_content_pane.pack2(self.content_scroll, resize=True, shrink=True)  # Right

    @staticmethod
    def create_headline_view(model: Gtk.TreeModel) -> Gtk.TreeView:
        tree_view = Gtk.TreeView(model=model)
        labels = ('Feeds', 'Headlines')
        for i, label in enumerate(labels):
            cell = Gtk.CellRendererText()
            if i == 0:  # Label
                cell.props.weight_set = True
                cell.props.weight = Pango.Weight.BOLD
                i = i - 1
            col = Gtk.TreeViewColumn(label, cell, text=i + 1)
            tree_view.append_column(col)
        return tree_view

    @staticmethod
    def create_headline_box(tree_view: Gtk.TreeView, width: int, height: int) -> Gtk.ScrolledWindow:
        headline_scroll = Gtk.ScrolledWindow()
        headline_scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.ALWAYS)
        headline_scroll.set_size_request(width, height)
        headline_scroll.add(tree_view)
        return headline_scroll

    @staticmethod
    def create_content_box() -> (Gtk.ScrolledWindow, Gtk.TextView):
        text_scroll = Gtk.ScrolledWindow()
        text_scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.ALWAYS)
        text_view = TextFormat.prepare_content_display(None, None)
        text_scroll.add(text_view)
        return text_scroll, text_view

    @staticmethod
    def toggle_tree_view_listening(tree_view: Gtk.TreeView, handler_id: int, func: Callable) -> Optional[int]:
        if handler_id is not None:  # The handler exists, stop listening
            tree_view.disconnect(handler_id)
            return None
        else:  # The handler doesn't exist, start listening
            return tree_view.connect('cursor-changed', func)

    def toggle_headline_listening(self):
        self.headline_changed_handler = self.toggle_tree_view_listening(self.headline_view,
                                                                        self.headline_changed_handler,
                                                                        self.show_new_content)

    def top_level(self) -> Gtk.Container:
        return self.headline_content_pane

    def change_position(self, delta: int) -> None:
        """ Switches keyboard focus between left and right pane """
        if delta < 0:
            self.headline_view.grab_focus()
        else:
            self.content_view.grab_focus()

    def show_new_content(self, tree_view: Gtk.TreeView) -> None:
        model, it = tree_view.get_selection().get_selected()
        if model and it:
            item = self.news_store.row_to_item(model[it])
            TextFormat.prepare_content_display(item, self.content_view)
