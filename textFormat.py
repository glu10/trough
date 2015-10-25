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
from gatherer import Gatherer

class TextFormat:
    """
    Used for the uniform formatting of text between views
    """

    @staticmethod
    def full_story(item, textview=None): # TODO: double check default value gotcha
        if textview is None:
            text_view = Gtk.TextView()
        else:
            text_view = textview

        text_view.set_margin_right(12)
        text_view.set_margin_left(10)
        text_view.set_editable(False)
        text_view.set_cursor_visible(False)
        text_view.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        text_buffer = Gtk.TextBuffer()
        TextFormat.headline(item.title, text_buffer)
        TextFormat.rss_description(item.description, text_buffer)
        TextFormat.scraped_story(item, text_buffer)
        TextFormat.link_button(item.link, text_buffer, text_view)
        text_view.set_buffer(text_buffer)

        return text_view

    @staticmethod
    def headline(headline, text_buffer):
        center = text_buffer.create_tag("center", justification=Gtk.Justification.CENTER, weight=Pango.Weight.BOLD)
        text_buffer.insert_with_tags(TextFormat.__pos(text_buffer), headline, center)
        #text_buffer.insert(TextFormat.__pos(text_buffer), headline)

    @staticmethod
    def scraped_story(item, text_buffer):
        text_buffer.insert(TextFormat.__pos(text_buffer), "\n\n")
        if Gatherer.get_and_set_article(item):
            paragraph = text_buffer.create_tag("paragraph", pixels_below_lines=5, pixels_above_lines=5)
            for p in item.article:
                text_buffer.insert_with_tags(TextFormat.__pos(text_buffer), p + "\n", paragraph)

    @staticmethod
    def rss_description(description, text_buffer):
        if description:
            center = text_buffer.create_tag("description", justification=Gtk.Justification.CENTER)
            text_buffer.insert_with_tags(TextFormat.__pos(text_buffer), "\n\n" + description, center)

    @staticmethod
    def link_button(link, text_buffer, text_view):
        if link:
            centerbold = text_buffer.create_tag("linkbutton", justification=Gtk.Justification.CENTER, weight=Pango.Weight.BOLD)
            text_buffer.insert_with_tags(TextFormat.__pos(text_buffer), ' ', centerbold)
            anchor = text_buffer.create_child_anchor(TextFormat.__pos(text_buffer))
            button = Gtk.LinkButton.new_with_label(link, "Read in Browser")
            button.set_relief(Gtk.ReliefStyle.NONE)
            text_view.add_child_at_anchor(button, anchor)

    @staticmethod
    def __pos(text_buffer):  # Convenience function for readability
            return text_buffer.get_end_iter()












