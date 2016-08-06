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
from webbrowser import open_new_tab

from textFormat import TextFormat


class NewsView(metaclass=ABCMeta):

    def __init__(self, preferences, gatherer):
        self.preferences = preferences
        self.gatherer = gatherer
        self.received_feeds = set()  # Used to mask a feed being received multiple times due to loose coupling
        self.last_item_index = -1
        self.last_item_feed_name = None
        self.content_view = None

    def appearance(self):
        return self.preferences.appearance_preferences()

    @abstractmethod
    def top_level(self):
        """
        Return the top-level GUI container of this component
        """

    def destroy_display(self):
        """
        Destroy the widgets related to this display.
        """
        top = self.top_level()
        for child in top:
            child.destroy()
        top.destroy()

    @abstractmethod
    def change_position(self, delta):
        """
        Changes which pane within a view currently has focus (used with left/right keys).
        """

    def open_link(self, url):
        """
        Open the provided URL in a browser.
        """
        if url:
            open_new_tab(url)

    def get_then_open_link(self):
        """
        Retrieves the currently active story's url, then calls open_link
        """
        active = self.gatherer.item(self.last_item_feed_name, self.last_item_index)
        if active:
            self.open_link(active.link)

    def populate(self, feeds):
        """
        Prepare already retrieved information for display
        """
        for feed in feeds:
            if feed.items:
                self.receive_feed(feed)

    @abstractmethod
    def refresh(self):
        """
        Clear the current contents of the view and requests fresh items
        """
        self.received_feeds.clear()
        self.last_item_index = -1
        self.last_item_feed_name = None

    def mark_feed(self, feed):
        """
        Mark a feed as seen to prevent duplicate feeds.
        A duplicate can occur due to the loose coupling between the gatherer and the view. Currently, any duplicates are
        simply ignored since the time between the feed retrievals must have been short (back-to-back refreshes) and even
        if potential differences did exist, it wouldn't be worth interrupting the user with the changes.
        """
        fresh = feed.name not in self.received_feeds
        if fresh:
            self.received_feeds.add(feed.name)
        return fresh

    @abstractmethod
    def receive_feed(self, feed):
        """
        A worker thread delivered a feed to the view, add it (including its items) to the view if it is not a duplicate.
        """

    def receive_article(self, item):
        """
        A worker thread delivered an article to the view, see if it is current then display it if so
        """
        assert(self.content_view is not None)
        current_item = self.gatherer.item(self.last_item_feed_name, self.last_item_index)
        if item == current_item:
            TextFormat.prepare_content_display(item, self.content_view)

    @abstractmethod
    def show_new_content(self, selection):
        """
        Display an item's content.
        """



