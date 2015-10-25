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

class NewsView(metaclass=ABCMeta):

    @abstractmethod
    def create_display(self):
        """
        Create the widgets related to this display and returns the top-level container.
        """

    @abstractmethod
    def destroy_display(self):
        """
        Destroy the widgets related to this display.
        """

    @abstractmethod
    def change_position(self, delta):
        """
        Change which story is being displayed, by going up or down a list.
        """

    @abstractmethod
    def open_link(self, url=""):
        """
        Open the currently active story URL, if one exists, in a browser.
        """
        open_new_tab(url)

    @abstractmethod
    def populate(self, items):
        """
        Fill this view with the information derived/provided from the RSS feeds.
        """

    @abstractmethod
    def refresh(self):
        """
        Clear the current contents of the view and populate them again.
        """
