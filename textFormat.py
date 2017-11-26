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

from gi import require_version

require_version('Gtk', '3.0')
from gi.repository import Gtk, Pango

from item import Item


class TextFormat:
    """
    Contains the RSS Title + Description + scraped contents.
    """

    @staticmethod
    def prepare_content_display(item: Item, existing_view: Gtk.TextView = None) -> Gtk.TextView:
        if existing_view is None:
            text_view = Gtk.TextView()
        else:
            text_view = existing_view

        text_view.set_name('storyview')  # For CSS

        # Border sizes
        text_view.set_left_margin(12)
        text_view.set_right_margin(12)
        text_view.set_bottom_margin(5)
        text_view.set_top_margin(5)
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
    def headline(headline: str, text_buffer: Gtk.TextBuffer) -> None:
        if headline:
            center = text_buffer.create_tag('center', justification=Gtk.Justification.CENTER, weight=Pango.Weight.BOLD)
            text_buffer.insert_with_tags(TextFormat.__pos(text_buffer), headline, center)

    @staticmethod
    def description(description: str, text_buffer: Gtk.TextBuffer) -> None:
        if description:
            center = text_buffer.create_tag('description', justification=Gtk.Justification.CENTER)
            text_buffer.insert_with_tags(TextFormat.__pos(text_buffer), '\n\n' + description, center)

    @staticmethod
    def article(article: str, text_buffer: Gtk.TextBuffer) -> None:
        if article:
            text_buffer.insert(TextFormat.__pos(text_buffer), '\n')
            paragraph = text_buffer.create_tag('paragraph', pixels_below_lines=5, pixels_above_lines=5)
            text_buffer.insert_with_tags(TextFormat.__pos(text_buffer), article + '\n', paragraph)

    @staticmethod
    def __pos(text_buffer: Gtk.TextBuffer) -> Gtk.TextIter:
        return text_buffer.get_end_iter()
