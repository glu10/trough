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
from gi.repository import Gdk, Gtk, Pango


class TextFormat:
    """
    Contains the RSS Title + Description + scraped contents.
    """

    @staticmethod
    def empty(text_view):
        if text_view:
            return text_view.set_buffer(Gtk.TextBuffer())

    @staticmethod
    def prepare_content_display(item, textview=None):
        if textview is None:
            text_view = Gtk.TextView()
        else:
            text_view = textview

        text_view.set_name('storyview') # For CSS

        # Border sizes
        if Gtk.get_major_version() == 3 and Gtk.get_minor_version() >= 20:
            text_view.set_left_margin(12)
            text_view.set_right_margin(12)
            text_view.set_bottom_margin(5)
            text_view.set_top_margin(5)
        else:
            text_view.set_border_window_size(Gtk.TextWindowType.LEFT, 10)
            text_view.set_border_window_size(Gtk.TextWindowType.RIGHT, 12)  # Slightly more than left due to scroll bar
            text_view.set_border_window_size(Gtk.TextWindowType.TOP, 5)
            text_view.set_border_window_size(Gtk.TextWindowType.TOP, 5)

        text_view.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        text_view.set_editable(False)
        text_view.set_cursor_visible(False)

        text_buffer = Gtk.TextBuffer()
        text_view.set_buffer(text_buffer)

        if item:
            TextFormat.headline(item.title, text_buffer)
            TextFormat.description(item.description, text_buffer)
            TextFormat.article(item.article, text_buffer)
        return text_view

    @staticmethod
    def headline(headline, text_buffer):
        if headline:
            center = text_buffer.create_tag("center", justification=Gtk.Justification.CENTER, weight=Pango.Weight.BOLD)
            text_buffer.insert_with_tags(TextFormat.__pos(text_buffer), headline, center)

    @staticmethod
    def description(description, text_buffer):
        if description:
            center = text_buffer.create_tag("description", justification=Gtk.Justification.CENTER)
            text_buffer.insert_with_tags(TextFormat.__pos(text_buffer), "\n\n" + description, center)

    @staticmethod
    def article(article, text_buffer):
        if article:
            text_buffer.insert(TextFormat.__pos(text_buffer), "\n\n")
            paragraph = text_buffer.create_tag("paragraph", pixels_below_lines=5, pixels_above_lines=5)
            for p in article:
                text_buffer.insert_with_tags(TextFormat.__pos(text_buffer), p + "\n", paragraph)

    @staticmethod
    def __pos(text_buffer):  # Convenience function for readability
            return text_buffer.get_end_iter()
