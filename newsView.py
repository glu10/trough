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

    def __init__(self, news_store, appearance_preferences):
        self.news_store = news_store
        self.appearance_preferences = appearance_preferences 
        self.last_item_index = -1
        self.last_item_feed_name = None
        self.content_view = None

    def appearance(self):
        return self.appearance_preferences

    @abstractmethod
    def change_position(self, delta):
        """
        Changes which pane within a view currently has focus (used with left/right keys).
        """

    def destroy_display(self):
        """
        Destroy the widgets related to this display.
        """
        top = self.top_level()
        for child in top:
            child.destroy()
        top.destroy()

    
    def open_link(self, url):
        """
        Open the provided URL in a browser.
        """
        if url:
            open_new_tab(url)

    @abstractmethod
    def show_new_content(self, selection):
        """
        Display an item's content.
        """

    @abstractmethod
    def top_level(self):
        """
        Return the top-level GUI container of this component
        """


