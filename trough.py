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
from gi.repository import Gtk, Gio, Gdk, GLib, GObject
from addFeed import AddFeed
from configManager import ConfigManager
from twoPaneView import TwoPaneView
from threePaneView import ThreePaneView
from gatherer import Gatherer
from preferencesWindow import PreferencesWindow
from utilityFunctions import make_button

class Trough(Gtk.Window):

    __gsignals__ = {'new_story_event': (GObject.SIGNAL_RUN_FIRST, None, ())}  # for custom signal handling

    def __init__(self):
        Gtk.Window.__init__(self, title="Trough")

        # Signals
        self.connect("delete-event", Gtk.main_quit)
        self.connect("key_press_event", self.on_key_press)
        self.connect("new_story_event", self.story_retrieved)

        self.set_default_size(1000, 800)  # TODO: Is there a more intelligent way to set this according to screen size?
        self.set_window_icon()
        self.config = ConfigManager()
        self.config.load_config()
        self.header_bar = self.create_header()
        self.gatherer = Gatherer(self, self.config)
        self.current_view = None
        self.switch_view()
        self.show_all()

        self.gatherer.collect()
        self.current_view.populate(self.gatherer.collected_items)

    def set_window_icon(self):
        """
        Attempts to find a generic RSS icon in the user's GTK theme, then associates it with the program if found.
        """
        try:
            theme = Gtk.IconTheme.get_default()
            icon = theme.lookup_icon("rss", 32, Gtk.IconLookupFlags.GENERIC_FALLBACK)
            if icon:
                icon = icon.load_icon()
                self.set_icon(icon)
        except GLib.GError:  # If the icon theme doesn't have an icon for RSS it's okay, purely visual
            pass

    def switch_view(self):
        """
        Activates the view currently chosen in the preferences and returns it.
        """
        view_key = self.config.appearance_preferences()['View']
        views = {'Two-Pane': TwoPaneView, 'Three-Pane': ThreePaneView}
        view_class = views[view_key]

        if type(self.current_view) != view_class:  # Will the new view actually be different from the current?
            if self.current_view:  # Do we even have a current view? (we don't if just starting up)
                self.current_view.destroy_display()

            self.current_view = view_class(self.config, self.gatherer)  # Make the new view
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
        add_button = make_button(theme_icon_string="add", tooltip_text="Quickly add a feed",
                                 signal="clicked", function=self.on_add_clicked)
        return add_button

    def create_preferences_button(self):
        preferences_button = make_button(theme_icon_string="preferences", tooltip_text="Preferences",
                                         signal="clicked", function=self.on_preferences_clicked)
        return preferences_button

    def create_refresh_button(self):
        refresh_button = make_button(theme_icon_string="view-refresh", tooltip_text="Refresh",
                                     signal="clicked", function=self.on_refresh_clicked)
        refresh_button.set_focus_on_click(False)  # Don't keep it looking "pressed" after clicked
        return refresh_button

    def on_add_clicked(self, widget=None):
        dialog = AddFeed(self)
        response = dialog.get_response(self.config.feeds())

        if response:
            self.config.add_feed(response.name, response.uri)
            self.on_refresh_clicked()  # Do a convenience refresh

    def on_preferences_clicked(self, widget=None):
        pw = PreferencesWindow(self, self.config)
        response = pw.run()
        if response == Gtk.ResponseType.OK:
            pw.apply_choices()
        pw.destroy()

    def on_refresh_clicked(self, widget=None):
        self.current_view.refresh(self.gatherer.collect())

    @staticmethod
    def do_scroll(widget, scroll):
        try:
            widget.do_scroll_child(widget, scroll, False)
        except AttributeError:
            pass

    # TODO: I actually want this to be in the view class but putting it here for now
    def story_retrieved(self, unnecessary_arg=None):
        while True:
            item = self.gatherer.grab_scrape_result()
            if item and item.article:
                self.current_view.receive_story(item)
            else:
                break

    # TODO: Idea: have a hotkey to add links to a buffer then you can open them all at once.
    def on_key_press(self, widget, event):
        key = Gdk.keyval_name(event.keyval)
        if key == "F5":
            self.on_refresh_clicked()
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
trough.show_all()

# These init calls are necessary because worker threads emit signals
GLib.threads_init()
Gdk.threads_init()

Gtk.main()

