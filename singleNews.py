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

from gi.repository import Gtk, Gdk
from newsView import NewsView
from clickableStory import ClickableStory

#TODO: Factor out the stories list, it's unnecessary

class SingleNews(NewsView):
    """ GUI component where RSS headlines appear for user selection. Headlines can be expanded to reveal a story."""
    def __init__(self, config):
        self.config = config
        self.stories = list()
        self.last_reveal = None
        self.last_story_position = -1
        self.top_vbox, self.scroll_window = self.create_display_window()

    def create_display_window(self):
        top_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        top_vbox.margin_end = 30
        top_vbox.override_background_color(Gtk.StateType.NORMAL, Gdk.RGBA(255, 255, 255, 1))

        scroll_window = Gtk.ScrolledWindow()
        scroll_window.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.ALWAYS)
        scroll_window.add(top_vbox)
        return top_vbox, scroll_window

    def top_level(self):
        return self.top_vbox

    def change_position(self, delta):
        """ Up/Down arrow key navigation among headlines"""
        new_pos = self.last_story_position + delta

        if 0 <= new_pos < len(self.stories):
            self.stories[new_pos].toggle_show_story(None, None)
            self.last_story_position = new_pos

    def refresh(self, items):
        for vbox in self.top_vbox.get_children():
            vbox.destroy()  # Clean out old headlines

        self.last_story_position = -1
        self.last_reveal = None
        self.stories = list()
        self.populate(items)
        self.scroll_window.show_all()

    def get_then_open_link(self, gatherer):
        if 0 <= self.last_story_position < len(self.stories):
            super().open_link(self.stories[self.last_story_position].item.link)

    def populate(self, items):
        for item in items:
            story = ClickableStory(item, self)
            self.stories.append(story)
            self.top_vbox.pack_start(story.clickable_headline, False, True, 0)