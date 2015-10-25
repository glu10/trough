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

import os, errno, json


class ConfigManager:
    """ Deals with configuration data that survives between sessions
        Examples are added feeds, filters, settings, etc. """
    feed_default = {}
    read_default = {}
    settings_default = { 'auto_refresh_mins': 10,  # <= 0 never refresh, pos # of mins.
                         'refresh_when_opened': True,
                         'remember_read_mins': 1440,  # neg never remember, 0 always, pos # of mins.
                         'hide_read': False}  #

    def __init__(self):
        self.config_home = os.path.join(os.path.expanduser("~"), ".config", "trough")
        self.settings_file = "settings.json"
        self.feed_file = "feeds.json"
        self.read_file = "read.json"
        self.feeds = {}
        self.read = {}
        self.settings = {}

    def load_config(self):
        self.ensure_directory_exists()
        self.settings = self.load_file(self.settings_file, self.settings_default)
        self.feeds = self.load_file(self.feed_file, self.feed_default)
        self.read = self.load_file(self.read_file, self.read_default)

    # If the configuration directory doesn't exist, try to make it.
    # TODO: Handle permission error? Not sure if necessary
    def ensure_directory_exists(self):
        try:
            os.makedirs(self.config_home)
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise

    def add_feed(self, name, uri, overwrite=False):
        if name in self.feeds and not overwrite:
            return False
        else:
            self.feeds[name] = uri
            self.update_feeds()
            return True

    def update_feeds(self):
        self.update_file(self.feed_file, self.feeds)

    def update_file(self, filename, data):
        file_path = os.path.join(self.config_home, filename)
        with open(file_path, 'w') as data_file:
            json.dump(data, data_file)

    # Check if the specified file exists, and if it doesn't make it with the default configuration
    def load_file(self, filename, defaults):
        file_path = os.path.join(self.config_home, filename)

        if not os.path.isfile(file_path):
            self.update_file(filename, defaults)
            data = defaults
        else:
            with open(file_path, 'r') as data_file:
                data = json.load(data_file)
                if defaults and not set(data.keys()).issubset(set(defaults.keys())):
                    raise RuntimeError("Incomplete data in " + file_path + ", fix the problem or delete the file.")
        return data