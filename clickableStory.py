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

from gi.repository import Gtk, Gdk, Pango
from textFormat import TextFormat

#TODO: Rename this class later to have a common terminology, story/article/item are getting mixed up
class ClickableStory:
    """ Content of an RSS entry. Possibly supplemented with scraped information. Configurable appearance. """
    def __init__(self, item, parent):
        self.parent = parent  # Parent news view this story belongs to
        self.item = item

        self.label = self.setup_label(item)
        self.title = self.setup_title(item)

        self.headline_box = self.setup_headline_box(self.label, self.title)
        self.clickable_headline, self.reveal = self.clickable_headline(self.headline_box)

    def setup_label(self, item):
        label = Gtk.Label()
        label.set_justify(Gtk.Justification.LEFT)
        label.set_markup("<span size=\"xx-small\">" + item.label + "</span>")
        return label

    def setup_title(self, item):
        title = Gtk.Label()
        title.set_justify(Gtk.Justification.LEFT)
        title.set_markup("<span size=\"larger\" weight=\"bold\" background=\"#FFFFFF\" >" + item.title + "</span>")
        return title

    def setup_headline_box(self, label, title):
        headline = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=20)
        headline.override_background_color(Gtk.StateType.NORMAL, Gdk.RGBA(255,255,255,1))
        headline.pack_start(label, False, False, 0)
        headline.pack_start(title, False, True, 0)
        return headline

    def clickable_headline(self, headline_box):
        event = Gtk.EventBox()
        event.add(headline_box)
        event.set_events(Gdk.EventMask.BUTTON_PRESS_MASK)
        event.connect("button_press_event", self.toggle_show_story)
        event.set_visible_window(True)

        reveal = Gtk.Revealer()
        reveal.set_transition_type(Gtk.RevealerTransitionType.SLIDE_DOWN)
        reveal.set_transition_duration(100)

        clickable_headline = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        clickable_headline.pack_start(event, True, True, 0)
        clickable_headline.pack_start(reveal, True, True, 0)
        return clickable_headline, reveal

    def toggle_show_story(self, widget, event):

        if self.reveal.get_child() is None:  # Is this the first time this news item has been clicked?
            self.reveal.add(TextFormat.full_story(self.item))  # Set up the article text
            self.clickable_headline.show_all()

        expansion = not self.reveal.get_reveal_child()  # Is the story going to be revealed?

        # Stylistic choice: ensures that only one story is ever expanded
        if expansion:
            lr = self.parent.last_reveal
            if lr is None:
                self.parent.last_reveal = self.reveal
            elif lr is not self.reveal and lr.get_reveal_child():
                    self.parent.last_reveal.set_reveal_child(False)
                    self.parent.last_reveal = self.reveal
            self.parent.last_story_position = self.parent.stories.index(self)  # Update last position to current pos

        else:
            self.parent.last_reveal = None

        self.reveal.set_reveal_child(expansion)