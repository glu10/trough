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
from gi.repository import Gtk, Pango
from utilityFunctions import string_to_RGBA


class NewsView(metaclass=ABCMeta):

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
        Change which story is being displayed, by going up or down a list.
        """

    def open_link(self, url):
        """
        Open the provided URL in a browser.
        """
        if url:
            open_new_tab(url)

    @abstractmethod
    def get_then_open_link(self, gatherer):
        """
        Retrieves the currently active story's url, then calls open_link
        """

    @abstractmethod
    def populate(self, feeds):
        """
        Prepare already retrieved information for display
        """

    @abstractmethod
    def refresh(self):
        """
        Clear the current contents of the view and requests fresh items
        """

    @abstractmethod
    def receive_feed(self, feed):
        """
        A worker thread delivered a feed to the view, add it (including its items) to the view
        """

    @abstractmethod
    def receive_story(self, item):
        """
        A worker thread delivered a story to the view, see if it is current then display it if so
        """

    @abstractmethod
    def text_containing_widgets(self):
        """
        Return the widgets (ordered from left to right according to appearance to the user) that are directly displaying
        text to the user. Used for focusing and font updating.
        """

    def update_appearance(self, appearance_dict):
        """
        Apply the appropriate appearance preferences to the current view
        """
        fws = self.text_containing_widgets()  # Font widgets

        if not fws:
            return

        keys = ['Category Font', 'Headline Font', 'Story Font']
        keys = keys[len(keys)-len(fws):]

        for i, fw in enumerate(fws):
            fw.override_font(Pango.FontDescription(appearance_dict[keys[i]]))
            fw.override_color(Gtk.StateFlags.NORMAL, string_to_RGBA(appearance_dict['Font Color']))
            fw.override_background_color(Gtk.StateFlags.NORMAL, string_to_RGBA(appearance_dict['Background Color']))

            # When text is selected, use the following colors
            fw.override_color(Gtk.StateFlags.SELECTED, string_to_RGBA(appearance_dict['Selection Font Color']))
            fw.override_background_color(Gtk.StateFlags.SELECTED, string_to_RGBA(appearance_dict['Selection Background Color']))





