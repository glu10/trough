#!/usr/bin/env python3
"""
    Trough - a GTK+ RSS news reader

    Copyright (C) 2016 Andrew Asp
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

import signal
import sys

import gi

gi.require_version('Gdk', '3.0')
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
from gi.repository import Gdk, Gio, GLib, Gtk

from cache import Cache
from mainWindow import MainWindow
from preferences import Preferences


class Trough(Gtk.Application):
    """ Beginning of the application: init -> run() -> startup signal -> activate signal """

    def __init__(self):
        super().__init__(application_id='org.glu10.trough', flags=Gio.ApplicationFlags.FLAGS_NONE)
        self.main_window = None
        self.preferences = None
        self.cache = None
        self.connect('activate', self.do_activate)

    def do_startup(self) -> None:
        Gtk.Application.do_startup(self)
        self.preferences = Preferences(load_from_file=True)
        self.cache = Cache(load_from_file=True)

    def do_activate(self, *args) -> None:
        if not self.main_window and self.preferences and self.cache:
            self.main_window = MainWindow(
                self.preferences,
                self.cache,
                application=self,
                title='Trough')
            self.main_window.connect('delete_event', self.on_quit)
            self.add_window(self.main_window)
            self.main_window.present()

    def on_quit(self, action, param):
        self.cache.write_cache()
        self.quit()


if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal.SIG_DFL)  # Respond to Ctrl+C

    # These init calls are needed because of multi-threading
    GLib.threads_init()
    Gdk.threads_init()

    # Start things up
    trough = Trough()
    trough.run(sys.argv)
