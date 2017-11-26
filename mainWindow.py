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

from math import floor

from gi import require_version

require_version('Gtk', '3.0')
from gi.repository import Gdk, GLib, Gtk

from cache import Cache
from feedDialog import FeedDialog
from newsStore import NewsStore
from newsView import NewsView
from preferences import Preferences
from preferencesWindow import PreferencesWindow
from stubGatherer import StubGatherer
from threePaneView import ThreePaneView
from twoPaneView import TwoPaneView
from utilityFunctions import make_button


class MainWindow(Gtk.Window):
    __gtype_name__ = 'TroughWindow'

    def __init__(self, preferences: Preferences, cache: Cache, **kwargs):
        Gtk.Window.__init__(self, **kwargs)

        self.preferences = preferences
        self.cache = cache

        self.news_store = NewsStore()
        self.gatherer = StubGatherer(self.news_store)
        # self.gatherer = Gatherer(self.news_store)

        self.connect_signals()
        self.prepare_appearance()

        self.css_provider = self.create_css()
        self.current_view = None
        self.switch_view(self.news_store, self.preferences)

    def connect_signals(self) -> None:
        self.connect('key_press_event', self.on_key_press)

    def prepare_appearance(self) -> None:
        self.set_good_default_size()
        self.set_window_icon()
        self.create_header()

    def set_good_default_size(self) -> None:
        screen = self.get_screen()
        active_window = screen.get_active_window()
        if active_window:
            monitor = screen.get_monitor_at_window(active_window)
            geometry = screen.get_monitor_geometry(monitor)
            width = floor(.60 * geometry.width)
            height = floor(.75 * geometry.height)
            self.set_default_size(width, height)
        else:
            # Guess a reasonable size
            self.set_default_size(600, 800)
        self.set_size_request(100, 100)  # Minimum size

    def set_window_icon(self) -> None:
        """ 
        Attempts to find a generic RSS icon in the user's GTK theme
        and associates it with the program if found.
        """
        try:
            theme = Gtk.IconTheme.get_default()
            icon = theme.lookup_icon(
                'rss',
                32,
                Gtk.IconLookupFlags.GENERIC_FALLBACK)
            if icon:
                icon = icon.load_icon()
                self.set_icon(icon)
        except GLib.GError:  # No RSS icon found
            pass

    def switch_view(self, news_store: NewsStore, preferences: Preferences) -> NewsView:
        """ 
        Activates the view currently chosen in the preferences and returns it.
        """
        appearance_prefs = preferences.appearance_preferences()
        view_key = appearance_prefs['View']
        views = {'Two-Pane': TwoPaneView, 'Three-Pane': ThreePaneView}
        view_class = TwoPaneView  # views[view_key] # FIXME: Hardcoded for development

        if type(self.current_view) != view_class:  # Ensure not switching to same view.
            if self.current_view:
                self.current_view.destroy_display()

            self.current_view = view_class(news_store, appearance_prefs)
            self.add(self.current_view.top_level())
            self.show_all()

            self.get_preferred_size()  # TODO: Investigate if still needed.

        return self.current_view

    def create_css(self) -> Gtk.CssProvider:
        css_provider = Gtk.CssProvider()
        css_provider.load_from_data(self.preferences.get_appearance_css())
        context = Gtk.StyleContext()
        context.add_provider_for_screen(
            self.get_screen(),
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        return css_provider

    def update_css(self) -> None:
        self.css_provider.load_from_data(self.preferences.get_appearance_css())

    def create_header(self) -> Gtk.HeaderBar:
        header_bar = Gtk.HeaderBar(title='Trough', show_close_button=True)
        header_bar.pack_start(self.create_add_button())
        header_bar.pack_start(self.create_preferences_button())
        header_bar.pack_start(self.create_refresh_button())
        self.set_titlebar(header_bar)
        return header_bar

    def create_add_button(self) -> Gtk.Button:
        add_button = make_button(
            theme_icon_string='add',
            tooltip='Quickly add a feed',
            signal='clicked',
            signal_func=self.on_add_clicked)
        return add_button

    def create_preferences_button(self) -> Gtk.Button:
        preferences_button = make_button(
            theme_icon_string='gtk-preferences',
            backup_icon_string='preferences-system',
            tooltip='Preferences',
            signal='clicked',
            signal_func=self.on_preferences_clicked)
        return preferences_button

    def create_refresh_button(self) -> Gtk.Button:
        refresh_button = make_button(
            theme_icon_string='view-refresh',
            tooltip='Refresh',
            signal='clicked',
            signal_func=self.on_refresh_clicked)
        refresh_button.set_focus_on_click(False)
        return refresh_button

    def on_add_clicked(self, widget: Gtk.Widget = None) -> None:
        dialog = FeedDialog(self, self.preferences.feeds())
        feed = dialog.get_response()

        if feed:
            self.preferences.add_feed(feed)
            self.on_refresh_clicked()  # Do a convenience refresh

    def on_preferences_clicked(self, widget: Gtk.Widget = None) -> None:
        pw = PreferencesWindow(self, self.preferences, self.cache)
        response = pw.run()
        if response == Gtk.ResponseType.OK:
            pw.apply_choices()
        pw.destroy()

    def on_refresh_clicked(self, widget: Gtk.Widget = None) -> None:
        """ 
        Goal: 
            1. Take each feed URI and look for current items.
            2. Only scrape item URIs not in cache.
        """
        self.news_store.clear()
        self.gatherer.request(None)
        '''
        for feed in self.preferences.feeds().values():
            self.gatherer.request(feed)
        '''

    @staticmethod
    def do_scroll(widget: Gtk.Widget, scroll: Gtk.ScrollType) -> None:
        try:
            widget.do_scroll_child(widget, scroll, False)
        except AttributeError:
            pass

    def on_key_press(self, widget: Gtk.Widget, event: Gdk.EventKey) -> None:
        key = Gdk.keyval_name(event.keyval)
        if key == 'F5':
            self.on_refresh_clicked()
        elif key == 'Left':
            self.current_view.change_position(-1)
        elif key == 'Right':
            self.current_view.change_position(1)
        elif key == 'Up':
            self.do_scroll(widget, Gtk.ScrollType.STEP_BACKWARD)
        elif key == 'Down':
            self.do_scroll(widget, Gtk.ScrollType.STEP_FORWARD)
        elif key == 'Return':
            if event.state & Gdk.ModifierType.CONTROL_MASK:
                self.current_view.get_then_open_link()
            else:
                self.current_view.change_position(0)
        else:
            pass
