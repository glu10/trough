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
    Trough homepage: https://github.com/glu10/trough
"""

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gio, Gdk, GLib
from addFeed import AddFeed
from configManager import ConfigManager
from singleNews import SingleNews
from splitNews import SplitNews
from tripleNews import TripleNews
from gatherer import Gatherer
from preferencesWindow import PreferencesWindow

class Trough(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self, title="Trough")
        self.set_default_size(1000, 800)
        self.set_window_icon()
        self.config = ConfigManager()
        self.config.load_config()
        self.header_bar = self.create_header()
        self.gatherer = Gatherer(self.config)
        self.current_view = None
        self.switch_view()
        self.show_all()

        self.gatherer.collect()
        self.current_view.populate(self.gatherer.collected_items)

    def set_window_icon(self):
        try:
            theme = Gtk.IconTheme.get_default()
            icon = theme.lookup_icon("rss", 32, Gtk.IconLookupFlags.GENERIC_FALLBACK)
            if icon:
                icon = icon.load_icon()
                self.set_icon(icon)
        except GLib.GError:  # If the icon theme doesn't have an icon for RSS it's okay, purely visual
            pass

    def switch_view(self):
        view_key = self.config.appearance_preferences()['View']
        views = {'Single': SingleNews, 'Double': SplitNews, 'Triple': TripleNews}
        view = views[view_key]

        if type(self.current_view) != view:
            if self.current_view:
                self.current_view.destroy_display()

            self.current_view = view(self.config, self.gatherer)
            self.add(self.current_view.top_level())
            if self.gatherer.collected_items:
                self.current_view.populate(self.gatherer.collected_items)

            self.show_all()

        return self.current_view

    def create_header(self):
        header_bar = Gtk.HeaderBar(title="Trough", show_close_button=True)
        header_bar.pack_start(self.create_add_button())
        header_bar.pack_start(self.create_preferences_button())
        header_bar.pack_start(self.create_refresh_button())
        self.set_titlebar(header_bar)
        return header_bar

    def create_add_button(self):
        add_button = Gtk.Button()
        add_icon = Gio.ThemedIcon(name="add")
        add_image = Gtk.Image.new_from_gicon(add_icon, Gtk.IconSize.BUTTON)
        add_button.add(add_image)
        add_button.set_tooltip_text("Quickly add a feed")
        add_button.connect("clicked", self.on_add_clicked)
        return add_button

    def create_preferences_button(self):
        preferences_button = Gtk.Button()
        preferences_icon = Gio.ThemedIcon(name="preferences")
        preferences_image = Gtk.Image.new_from_gicon(preferences_icon, Gtk.IconSize.BUTTON)
        preferences_button.add(preferences_image)
        preferences_button.set_tooltip_text("Preferences")
        preferences_button.connect("clicked", self.on_preferences_clicked)
        return preferences_button

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
        response = dialog.get_response(self.config.feeds())
        # TODO: When the feeds are changed to an actual model the overwrite case has to be handled here.
        if response:
            self.config.add_feed(response.name, response.uri)
            self.on_refresh_clicked(None)  # Do a convenience refresh

    def on_preferences_clicked(self, widget):
        pw = PreferencesWindow(self, self.config)
        response = pw.run()
        if response == Gtk.ResponseType.OK:
            pw.apply_choices()
        pw.destroy()

    def on_refresh_clicked(self, widget):
        self.current_view.refresh(self.gatherer.collect())

    @staticmethod
    def do_scroll(widget, scroll):
        try:
            widget.do_scroll_child(widget, scroll, False)
        except AttributeError:
            pass

    # TODO: Idea: have a hotkey to add links to a buffer then you can open them all at once.
    def on_key_press(self, widget, event):
        key = Gdk.keyval_name(event.keyval)
        if key == "F5":
            self.on_refresh_clicked(None)
        elif key == "Left":
            self.current_view.change_position(-1)
        elif key == "Right":
            self.current_view.change_position(1)
        elif key == "Up":
            self.do_scroll(widget, Gtk.ScrollType.STEP_BACKWARD)
        elif key == "Down":
            self.do_scroll(widget, Gtk.ScrollType.STEP_FORWARD)
        elif key == "Return":
            if event.state & Gdk.ModifierType.CONTROL_MASK:
                self.current_view.get_then_open_link(self.gatherer)
            else:
                self.current_view.change_position(0)
        else:
            pass

trough = Trough()
trough.connect("delete-event", Gtk.main_quit)
trough.connect("key_press_event", trough.on_key_press)
trough.show_all()
Gtk.main()
