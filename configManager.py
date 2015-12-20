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
from collections import OrderedDict
from gi.repository import Gio

# Currently undergoing the transition of actually implementing the preferences

class ConfigManager:
    """ Deals with configuration data that survives between sessions
        Examples are added feeds, filters, preferences, etc. """

    def __init__(self):
        self.config_home = os.path.join(os.path.expanduser("~"), ".config", "trough")
        self.preferences_file = "preferences.json"
        self.feed_file = "feeds.json"
        self.read_file = "read.json"
        self.preferences = self.default_preferences()
        self.feeds = self.preferences['Feeds']  # TODO: Clean this up, self.feeds is assumed in other files

    def default_preferences(self):
        preferences = OrderedDict()
        preferences['Appearance'] = self.default_appearance_preferences()
        preferences['Feeds'] = self.default_feeds_preferences()
        preferences['Filtration'] = self.default_filtration_preferences()
        preferences['Retrieval'] = self.default_retrieval_preferences()
        return preferences

    def default_appearance_preferences(self):
        p = OrderedDict()
        p['View'] = 'Double'

        # TODO: Investigate if these font strings are reliably set among different DEs/WMs
        gs = Gio.Settings('org.gnome.desktop.interface')
        default_font = gs.get_string('font-name')
        # monospace_font = gs.get_string('monospace-font-name'
        document_font = gs.get_string('document-font-name')

        p['Category Font'] = default_font
        p['Headline Font'] = default_font
        p['Story Font'] = document_font

        p['Font Color'] = 'rgba(0, 0, 0, 1.0)'  # RGBA for solid black.
        p['Background Color'] = 'rgba(255, 255, 255, 1.0)'  # RGBA for solid white
        return p

    def default_feeds_preferences(self):
        return OrderedDict()

    def default_filtration_preferences(self):  # TODO: Support for user-supplied regex expressions
        p = OrderedDict()
        p['Filtered Links'] = list()
        p['Filtered Titles'] = list()
        p['Filtered Content'] = list()
        p['HideOrHighlight'] = "Highlight"
        p['FilteredHighlight'] = 'rgba(128, 128, 128, .5)'  # RGBA values (for a slightly translucent gray)
        return p

    def default_retrieval_preferences(self):  # TODO: Support for auto-refresh on a feed-by-feed basis would be nice
        p = OrderedDict()
        p['Refresh When Opened'] = True
        p['Auto-refresh'] = False
        p['Auto-refresh Interval Time'] = 30   # Non-negative value, cap at a max value
        p['Auto-refresh Unit'] = "Minute"      # Second/Hour/Minute/Day
        p['Scraping Strategy'] = 'Individual'  # By Feed/Individual/On Refresh
        return p


    def load_config(self):
        self.ensure_directory_exists()
        self.preferences = self.load_file(self.preferences_file, self.preferences)
        self.preferences['Feeds'] = self.load_file(self.feed_file, self.preferences['Feeds'])
        self.feeds = self.preferences['Feeds']

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
            self.preferences['Feeds'][name] = uri
            self.update_feeds()
            return True

    def update_feeds(self):
        self.update_file(self.feed_file, self.preferences['Feeds'])

    def update_file(self, filename, data):
        file_path = os.path.join(self.config_home, filename)
        with open(file_path, 'w') as data_file:
            json.dump(data, data_file)

    def update_preferences_file(self):
        """ Public convenience function """
        self.update_file(self.preferences_file, self.preferences)

    # Check if the specified file exists, and if it doesn't make a file with the default configuration
    def load_file(self, filename, defaults):
        file_path = os.path.join(self.config_home, filename)
        data = OrderedDict()

        # If we expect some information, and the file doesn't exist or is empty
        if defaults and (not os.path.isfile(file_path) or os.stat(file_path).st_size == 0):
            if defaults:
                self.update_file(filename, defaults)  # Write defaults to replace the empty/nonexistent file
                data = defaults
        else:
            with open(file_path, 'r') as data_file:
                try:
                    data = json.load(data_file)
                except json.decoder.JSONDecodeError:
                    raise RuntimeError("Error parsing the JSON in " + file_path + ", is it valid JSON?")
                # Make sure that the information we are getting actually corresponds to real preferences.
                if defaults and sorted(data.keys()) != sorted(defaults.keys()):
                    raise RuntimeError("Data in " + file_path + " did not match expectations," +
                                                                " fix the problem or delete the file.")
        return data