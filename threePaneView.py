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

from gi.repository import Gtk
from newsView import NewsView
from twoPaneView import TwoPaneView
from textFormat import TextFormat
import utilityFunctions
from collections import defaultdict

class ThreePaneView(NewsView):

    def __init__(self, config, gatherer):
        self.config = config
        self.gatherer = gatherer
        self.refreshing = False

        self.label_dict = dict()

        self.label_store = Gtk.ListStore(str)
        self.label_view = self.create_view(self.label_store, 'Feed', 0, self.show_new_headlines)
        self.label_scroll = TwoPaneView.create_headline_box(self.label_view, 20, 200)

        self.headline_store = Gtk.ListStore(str, int)
        self.headline_view = self.create_view(self.headline_store, 'Headline', 0, self.show_new_article)
        self.headline_scroll = TwoPaneView.create_headline_box(self.headline_view, 300, 200)

        self.story_scroll, self.story_view = TwoPaneView.create_story_box()

        self.top_pane = Gtk.Paned(orientation=Gtk.Orientation.HORIZONTAL)
        self.inner_pane = Gtk.Paned(orientation=Gtk.Orientation.HORIZONTAL)

        self.inner_pane.pack1(self.headline_scroll, resize=False, shrink=False)
        self.inner_pane.pack2(self.story_scroll, resize=True, shrink=True)
        self.top_pane.pack1(self.label_scroll, resize=False, shrink=False)
        self.top_pane.pack2(self.inner_pane, resize=False, shrink=False)

        self.update_appearance(config.appearance_preferences())
        self.label_view.grab_focus()
        self.focused_index = 0
        self.last_item_index = -1

    @staticmethod
    def create_view(store, label, pos, change_func):
        view = Gtk.TreeView(model=store)
        if change_func:
            view.get_selection().connect("changed", change_func)
        cell = Gtk.CellRendererText()
        col = Gtk.TreeViewColumn(label, cell, text=pos)
        view.append_column(col)
        return view

    def change_position(self, delta):
        changed_pos = self.focused_index + delta
        if 0 <= changed_pos < 3:
            widgets = [self.label_view, self.headline_view, self.story_view]
            widgets[changed_pos].grab_focus()
            self.focused_index = changed_pos

    def match_label(self, model, iter, data=None):
        return model[iter][0] == data

    def refresh(self, items):
        self.refreshing = True

        self.label_store.clear()
        self.headline_store.clear()

        self.populate(items)
        self.refreshing = False

    def populate(self, items):
        self.label_dict = defaultdict(list)
        for i, item in enumerate(items):
            self.label_dict[item.label].append(i)

        for label in self.label_dict.keys():
            self.label_store.append([label])

    def get_then_open_link(self, gatherer):
        active = gatherer.item(self.last_item_index)
        if active:
            super().open_link(active.link)

    def text_containing_widgets(self):
        return self.label_view, self.headline_view, self.story_view

    def top_level(self):
        return self.top_pane

    def show_new_headlines(self, selection):
        if not self.refreshing and selection:
            model, iter = selection.get_selected()

            self.refreshing = True
            self.headline_view.do_unselect_all(self.headline_view)
            self.headline_store.clear()

            for index in self.label_dict[model[iter][0]]:
                title = utilityFunctions.shorten_title(self.gatherer.item(index).title)
                self.headline_store.append([title, index])
            self.refreshing = False

    def show_new_article(self, selection):
        if not self.refreshing and selection:
            model, iter = selection.get_selected()
            if model and iter:
                self.last_item_index = model[iter][1]
                TextFormat.full_story(self.gatherer.item(self.last_item_index), self.story_view)