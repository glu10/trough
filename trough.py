#!/usr/bin/env python3
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

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gio, Gdk, GLib
from addFeed import AddFeed
from configManager import ConfigManager
from singleNews import SingleNews
from splitNews import SplitNews

class Trough(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self, title="Trough")
        self.set_default_size(400, 600)
        self.set_window_icon()
        self.config = ConfigManager()
        self.config.load_config()
        self.header_bar = self.create_header()

        # Split headlines/news view
        split = True  # TODO: will be in settings
        if split:
            self.splitBox = SplitNews(self.config, self.gatherer)
            self.splitBox.populate()
            self.add(self.splitBox.display)
        else:
            self.newsBox = SingleNews(self.config, self.gatherer)
            self.newsBox.populate()
            self.add(self.newsBox.scroll_window)

    def set_window_icon(self):
        theme = Gtk.IconTheme.get_default()
        try:
            icon = theme.lookup_icon("rss", 32, Gtk.IconLookupFlags.GENERIC_FALLBACK).load_icon()
            self.set_icon(icon)
        except GLib.Gerror:
            pass

    def create_header(self):
        header_bar = Gtk.HeaderBar()
        header_bar.set_show_close_button(True)
        header_bar.props.title = "Trough"
        self.set_titlebar(header_bar)

        header_bar.pack_start(self.create_add_button())
        header_bar.pack_start(self.create_settings_button())
        header_bar.pack_start(self.create_refresh_button())
        return header_bar

    def create_add_button(self):
        add_button = Gtk.Button()
        add_icon = Gio.ThemedIcon(name="add")
        add_image = Gtk.Image.new_from_gicon(add_icon, Gtk.IconSize.BUTTON)
        add_button.add(add_image)
        add_button.set_tooltip_text("Quickly add a feed")
        add_button.connect("clicked", self.on_add_clicked)
        return add_button

    def create_settings_button(self):
        settings_button = Gtk.Button()
        settings_icon = Gio.ThemedIcon(name="preferences")
        settings_image = Gtk.Image.new_from_gicon(settings_icon, Gtk.IconSize.BUTTON)
        settings_button.add(settings_image)
        settings_button.set_tooltip_text("Settings")
        settings_button.connect("clicked", self.on_settings_clicked)
        return settings_button

    def create_refresh_button(self):
        refresh_button = Gtk.Button()
        refresh_icon = Gio.ThemedIcon(name="view-refresh")
        refresh_image = Gtk.Image.new_from_gicon(refresh_icon, Gtk.IconSize.BUTTON)
        refresh_button.set_focus_on_click(False)  # Don't keep it looking "pressed" after clicked
        refresh_button.set_tooltip_text("Refresh")
        refresh_button.add(refresh_image)
        refresh_button.connect("clicked", self.on_refresh_clicked)
        return refresh_button

    def on_add_clicked(self, widget):
        dialog = AddFeed(self)
        response = dialog.run()

        # TODO: This loop is hacky and most likely not the right way to do this
        while not (response == Gtk.ResponseType.CANCEL or response == Gtk.ResponseType.NONE or (
                response == Gtk.ResponseType.OK and dialog.add_entry(self.config))):
            response = dialog.run()
        dialog.destroy()

        # Do a convenience refresh?

    def on_settings_clicked(self, widget):
        return None

    def on_refresh_clicked(self, widget):
        self.newsBox.refresh()

    #TODO: Abstract newsBox calls to allow for switch between split/single
    def on_key_press(self, widget, event):
        key = Gdk.keyval_name(event.keyval)
        if key == "F5":
            self.on_refresh_clicked(widget)
        elif key == "Left":
            self.newsBox.change_position(-1)
        elif key == "Right":
            self.newsBox.change_position(1)
        elif key == "Up":
            self.newsBox.scroll(True)
        elif key == "Down":
            self.newsBox.scroll(False)
        elif key == "Return":
            if event.state & Gdk.ModifierType.CONTROL_MASK:
                self.newsBox.open_link()
            else:
                self.newsBox.change_position(0)
        else:
            pass

trough = Trough()
trough.connect("delete-event", Gtk.main_quit)
trough.connect("key_press_event", trough.on_key_press)
trough.show_all()
Gtk.main()
