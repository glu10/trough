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

    The full project can be found at: https://github.com/glu10/trough
"""

from gatherer import Gatherer
from gi.repository import Gtk, Gio, Gdk
from newsView import NewsView
from clickableStory import ClickableStory
import webbrowser

class SplitNews(NewsView):
    """ GUI component where headlines and story contents are split apart """
    def __init__(self, config, gatherer):
        self.config = config
        self.gatherer = gatherer

        self.headlines = list()
        self.buffers = list()

        self.last_reveal = None
        self.last_story_position = -1
        self.top_hbox, self.headline_box, self.text_box = self.create_display()

    def create_display(self):
        top_hbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        top_hbox.margin_end = 30

        #TODO: Left list box

        scroll_window = Gtk.ScrolledWindow()
        scroll_window.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.ALWAYS)
        scroll_window.add(top_hbox)

        return top_hbox, scroll_window

    def destroy_display(self):
        for child in self.top_hbox:
            child.destroy()
        self.top_hbox.destroy()

    def change_position(self, delta):
        """ Up/Down arrow key navigation among headlines"""
        new_pos = self.last_story_position + delta

       # if 0 <= new_pos < len(self.stories):
           # self.headlines[new_pos]
           # self.last_headline

    def refresh(self):


    def scroll(self, up):
        if up:
            step = Gtk.ScrollType.STEP_BACKWARD
        else:
            step = Gtk.ScrollType.STEP_FORWARD
        self.text_box.do_scroll_child(self.text_box, step, False)

    def open_link(self):


    def populate(self, gatherer, feed):
        news_list = self.gatherer.collect(self.config.feeds)
