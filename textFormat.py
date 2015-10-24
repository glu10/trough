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
from gatherer import Gatherer

class TextFormat:
    """
    Used for the uniform formatting of text between views
    """

    def __init__(self, config):
        self.config = config

    def full_story(self, item):
        text_view = Gtk.TextView()
        text_view.set_margin_right(12)
        text_view.set_margin_left(10)
        text_view.set_editable(False)
        text_view.set_cursor_visible(False)
        text_view.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        text_buffer = text_view.get_buffer()
        
        self.headline(item.title, text_buffer)
        self.RSS_description(item.description, text_buffer)
        self.scraped_story(item, text_buffer)
        self.link_button(item.link, text_buffer, text_view)

        return text_view

    def headline(self, headline, text_buffer):
        bold = text_buffer.create_tag("headline", weight=Pango.Weight.BOLD)
        text_buffer.insert_with_tags(self.__pos(text_buffer), "Title: ", bold)
        text_buffer.insert(self.__pos(text_buffer), headline)

    def scraped_story(self, item, text_buffer):
        if Gatherer.get_and_set_article(item):
            text_buffer.insert_with_tags(self.__pos(text_buffer), "\n\nArticle: ", bold)
            paragraph = text_buffer.create_tag("paragraph", pixels_below_lines=5, pixels_above_lines=5)
            for p in item.article:
                text_buffer.insert_with_tags(self.__pos(text_buffer), p + "\n", paragraph)

    def RSS_description(self, description, text_buffer):
        if description:
            bold = text_buffer.create_tag("description", weight=Pango.Weight.BOLD)
            text_buffer.insert_with_tags(self.__pos(text_buffer), "\n\nDescription: ", bold)
            text_buffer.insert(self.__pos(text_buffer), description)

    def link_button(self, link, text_buffer, text_view):
        if link:
            center = text_buffer.create_tag("center", justification=Gtk.Justification.CENTER, weight=Pango.Weight.BOLD)
            text_buffer.insert_with_tags(self.__pos(text_buffer), ' ', center)
            anchor = text_buffer.create_child_anchor(self.__pos(text_buffer))
            button = Gtk.LinkButton.new_with_label(link, "Read in Browser")
            button.set_relief(Gtk.ReliefStyle.NONE)
            text_view.add_child_at_anchor(button, anchor)

    @staticmethod
    def __pos(text_buffer):  # Convenience function for readability
            return text_buffer.get_end_iter()












