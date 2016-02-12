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

class ThreePaneView(NewsView):

    def __init__(self, config, gatherer):
        self.config = config
        self.gatherer = gatherer
        self.refreshing = False

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
        self.last_item_feed_name = None

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

    def get_then_open_link(self, gatherer):
        active = gatherer.item(self.last_item_feed_name, self.last_item_index)
        if active:
            super().open_link(active.link)

    def populate(self, feed_list):
        for feed in feed_list:
            if feed.items:
                self.receive_feed(feed)

    def refresh(self):
        self.refreshing = True
        self.label_store.clear()
        self.headline_store.clear()
        self.gatherer.request_feeds()
        TextFormat.empty(self.story_view)
        self.last_item_index = -1
        self.last_item_feed_name = None
        self.refreshing = False

    def text_containing_widgets(self):
        return self.label_view, self.headline_view, self.story_view

    def top_level(self):
        return self.top_pane

    def show_new_headlines(self, selection):
        if not self.refreshing and selection:
            model, iter = selection.get_selected()
            self.last_item_feed_name = model[iter][0]
            self.refreshing = True
            self.headline_view.do_unselect_all(self.headline_view)
            self.headline_store.clear()

            feed = self.config.get_feed(self.last_item_feed_name)
            if feed:
                for pos, item in enumerate(feed.items):
                    self.headline_store.append([item.title, pos])
            self.refreshing = False

    def show_new_article(self, selection):
        if not self.refreshing and selection:
            model, iter = selection.get_selected()
            if model and iter:
                self.last_item_index = model[iter][1]
                item = self.gatherer.item(self.last_item_feed_name, self.last_item_index)
                if item.article:
                    TextFormat.full_story(item, self.story_view)
                else:
                    self.gatherer.request(item)

    def receive_feed(self, feed):
        self.label_store.append([feed.name])

    def receive_story(self, item):  # TODO: Duplicated code, change to be common in NewsView later
        current_item = self.gatherer.item(self.last_item_feed_name, self.last_item_index)
        if item == current_item:
            TextFormat.full_story(item, self.story_view)