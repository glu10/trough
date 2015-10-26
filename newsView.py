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
    def top_level(self):
        """ Return the top-level GUI container of this component """

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

    def open_link(self, url):
        """
        Open the provided URL in a browser.
        """
        open_new_tab(url)

    @abstractmethod
    def get_then_open_link(self, gatherer):
        """ Retrieves the currently active story's url, then calls open_link """

    @abstractmethod
    def populate(self, items):
        """
        Fill this view with the information derived/provided from the RSS feeds.
        """

    @abstractmethod
    def refresh(self, items):
        """
        Clear the current contents of the view and populate them again.
        """
