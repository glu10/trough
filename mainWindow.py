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

from gi.repository import Gtk, Gio, Gdk, GLib, GObject
from feedDialog import FeedDialog
from preferences import Preferences
from twoPaneView import TwoPaneView
from threePaneView import ThreePaneView
from gatherer import Gatherer
from preferencesWindow import PreferencesWindow
from utilityFunctions import make_button
from math import floor


class MainWindow(Gtk.Window):

    # __gsignals__ is used to register the names of custom signals
    __gsignals__ = {'item_scraped_event': (GObject.SIGNAL_RUN_FIRST, None, ()),
                    'feed_gathered_event': (GObject.SIGNAL_RUN_FIRST, None, ())}
    __gtype_name__ = 'TroughWindow'

    def __init__(self, preferences, cache, **kwargs):
        Gtk.Window.__init__(self, **kwargs)

        # Signals
        self.connect('key_press_event', self.on_key_press)
        self.connect('item_scraped_event', self.on_item_scraped)
        self.connect('feed_gathered_event', self.on_feed_gathered)

        self.set_default_size(*self.get_good_default_size())
        self.set_window_icon()
        self.preferences = preferences
        self.css_provider = self.create_css()
        self.header_bar = self.create_header()

        self.gatherer = Gatherer(self, self.preferences, cache)
        self.current_view = None
        self.switch_view()

        self.gatherer.request_feeds()

    def get_good_default_size(self):
        screen = self.get_screen()
        monitor = screen.get_monitor_at_window(screen.get_active_window())
        geometry = screen.get_monitor_geometry(monitor)
        width = floor(.60*geometry.width)
        height = floor(.75*geometry.height)

        return width, height

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
        view_key = self.preferences.appearance_preferences()['View']
        views = {'Two-Pane': TwoPaneView, 'Three-Pane': ThreePaneView}
        view_class = views[view_key]

        if type(self.current_view) != view_class:  # Will the new view actually be different from the current?
            if self.current_view:  # Do we even have a current view? (we don't if just starting up)
                self.current_view.destroy_display()

            self.current_view = view_class(self.preferences, self.gatherer)  # Make the new view
            self.current_view.populate(self.preferences.feed_list())
            self.add(self.current_view.top_level())
            self.show_all()

        return self.current_view

    def create_css(self):
        css_provider = Gtk.CssProvider()
        css_provider.load_from_data(self.preferences.get_appearance_css())
        context = Gtk.StyleContext()
        context.add_provider_for_screen(self.get_screen(), css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        return css_provider

    def update_css(self):
        self.css_provider.load_from_data(self.preferences.get_appearance_css())

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
        preferences_button = make_button(theme_icon_string='gtk-preferences', backup_icon_string='preferences-system',
                                         tooltip_text="Preferences", signal="clicked",
                                         function=self.on_preferences_clicked)
        return preferences_button

    def create_refresh_button(self):
        refresh_button = make_button(theme_icon_string="view-refresh", tooltip_text="Refresh",
                                     signal="clicked", function=self.on_refresh_clicked)
        refresh_button.set_focus_on_click(False)  # Don't keep it looking "pressed" after clicked
        return refresh_button

    def on_add_clicked(self, widget=None):
        dialog = FeedDialog(self)
        response = dialog.get_response(self.preferences.feeds())

        if response:
            self.preferences.add_feed(response.name, response.uri)
            self.on_refresh_clicked()  # Do a convenience refresh

    def on_preferences_clicked(self, widget=None):
        pw = PreferencesWindow(self, self.preferences)
        response = pw.run()
        if response == Gtk.ResponseType.OK:
            pw.apply_choices()
        pw.destroy()

    def on_refresh_clicked(self, widget=None):
        self.current_view.refresh()

    @staticmethod
    def do_scroll(widget, scroll):
        try:
            widget.do_scroll_child(widget, scroll, False)
        except AttributeError:
            pass

    # TODO: It would be better to have this be in the view class but putting it here for now
    def on_item_scraped(self, unnecessary_arg=None):
        while True:
            item = self.gatherer.grab_scrape_result()
            if item and item.article:
                self.current_view.receive_article(item)
            else:
                break

    # TODO: It would be better to have this be in the view class but putting it here for now
    def on_feed_gathered(self, unnecessary_arg=None):
        while True:
            feed = self.gatherer.grab_feed_result()
            if feed and feed.items:
                self.filter_feed(feed)
                feed.items.sort()
                self.current_view.receive_feed(feed)
            else:
                break

    def filter_feed(self, feed):
        for fil in self.preferences.filters():
            fil.inspect_feed(feed)

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
                self.current_view.get_then_open_link()
            else:
                self.current_view.change_position(0)
        else:
            pass

