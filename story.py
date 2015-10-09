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

from gi.repository import Gtk, Gdk, Pango

#TODO: Rename this class later to have a common terminology, story/article/item are getting mixed up
class Story:
    """ Content of an RSS entry. Possibly supplemented with scraped information. Configurable appearance. """
    def __init__(self, item, news_box):
        self.newsBox = news_box  # Parent newsBox this story belongs to
        self.gatherer = self.newsBox.gatherer
        self.item = item

        self.label = self.setup_label(item)
        self.title = self.setup_title(item)
        self.story = ""  # Will be populated once the headline is clicked

        self.headline_box = self.setup_headline_box(self.label, self.title)
        self.clickable_headline, self.reveal = self.clickable_headline(self.headline_box, self.story)

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

    # TODO: Change story from a simple label to a more complex multi-line text + pictures
    def setup_story(self, item):
        textview = Gtk.TextView()
        textview.set_margin_right(12)
        textview.set_margin_left(10)
        textview.set_editable(False)
        textview.set_cursor_visible(False)
        textview.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        textbuffer = textview.get_buffer()

        def pos():  # Convenience function for readability
            return textbuffer.get_end_iter()

        bold = textbuffer.create_tag("title", weight=Pango.Weight.BOLD)
        textbuffer.insert_with_tags(pos(), "Description: ", bold)
        textbuffer.insert(pos(), item.description)

        if not item.article and not item.attempted_scrape:
            item.article = self.gatherer.get_article(item.link)
            if item.article:
                textbuffer.insert_with_tags(pos(), "\n\nArticle: ", bold)
                paragraph = textbuffer.create_tag("paragraph", pixels_below_lines=5, pixels_above_lines=5)
                for p in item.article:
                    textbuffer.insert_with_tags(pos(), p + "\n", paragraph)

        if item.link:
            center = textbuffer.create_tag("center", justification=Gtk.Justification.CENTER, weight=Pango.Weight.BOLD)
            textbuffer.insert_with_tags(pos(), ' ', center)
            anchor = textbuffer.create_child_anchor(pos())
            link = Gtk.LinkButton.new_with_label(item.link, "Read in Browser")
            link.set_relief(Gtk.ReliefStyle.NONE)
            textview.add_child_at_anchor(link, anchor)

        return textview

    def setup_headline_box(self, label, title):
        headline = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=20)
        headline.override_background_color(Gtk.StateType.NORMAL, Gdk.RGBA(255,255,255,1))
        headline.pack_start(label, False, False, 0)
        headline.pack_start(title, False, True, 0)
        return headline

    def clickable_headline(self, headline_box, story):
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
            self.reveal.add(self.setup_story(self.item))  # Set up the article text
            self.clickable_headline.show_all()

        expansion = not self.reveal.get_reveal_child()  # Is the story going to be revealed?

        # Stylistic choice: ensures that only one story is ever expanded
        if expansion:
            lr = self.newsBox.last_reveal
            if lr is None:
                self.newsBox.last_reveal = self.reveal
            elif lr is not self.reveal and lr.get_reveal_child():
                    self.newsBox.last_reveal.set_reveal_child(False)
                    self.newsBox.last_reveal = self.reveal
            self.newsBox.last_story_position = self.newsBox.stories.index(self)  # Update last position to current pos

        else:
            self.newsBox.last_reveal = None

        self.reveal.set_reveal_child(expansion)