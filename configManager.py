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
from feed import Feed
from copy import deepcopy

class ConfigManager:
    """ Deals with configuration data that survives between sessions
        Examples are added feeds, filters, preferences, etc. """

    def __init__(self):
        self.config_home = os.path.join(os.path.expanduser("~"), ".config", "trough")
        self.preferences_file = "preferences.json"
        self.preferences = self.default_preferences()

    @staticmethod
    def default_preferences():
        preferences = OrderedDict() # Ordered dict for readability
        preferences['Appearance'] = ConfigManager.default_appearance_preferences()
        preferences['Feeds'] = ConfigManager.default_feeds_preferences()
        preferences['Filtration'] = ConfigManager.default_filtration_preferences()
        preferences['Retrieval'] = ConfigManager.default_retrieval_preferences()
        return preferences

    @staticmethod
    def default_appearance_preferences():
        p = dict()
        p['View'] = 'Two-Pane'

        # TODO: Investigate if these font strings are reliably set among different DEs/WMs
        gs = Gio.Settings('org.gnome.desktop.interface')
        default_font = gs.get_string('font-name')
        document_font = gs.get_string('document-font-name')

        p['Category Font'] = default_font
        p['Headline Font'] = default_font
        p['Story Font'] = document_font

        p['Font Color'] = 'rgba(0, 0, 0, 1.0)'  # RGBA for solid black.
        p['Background Color'] = 'rgba(255, 255, 255, 1.0)'  # RGBA for solid white
        p['Selection Font Color'] = 'rgba(255, 255, 255, 1.0)'  # RGBA for solid white
        p['Selection Background Color'] = 'rgba(81, 126, 173, 1.0)'  # RGBA for medium-dark blue
        return p

    @staticmethod
    def default_feeds_preferences():
        return dict()

    @staticmethod
    def default_filtration_preferences():  # TODO: Support for user-supplied regex expressions
        p = dict()
        p['Filtered Links'] = list()
        p['Filtered Titles'] = list()
        p['Filtered Content'] = list()
        p['HideOrHighlight'] = "Highlight"
        p['FilteredHighlight'] = 'rgba(128, 128, 128, .5)'  # RGBA values (for a slightly translucent gray)
        return p

    @staticmethod
    def default_retrieval_preferences():  # TODO: Support for auto-refresh on a feed-by-feed basis would be nice
        p = dict()
        p['Refresh When Opened'] = True
        p['Auto-refresh'] = False
        p['Auto-refresh Interval Time'] = 30   # Non-negative value, cap at a max value
        p['Auto-refresh Unit'] = "Minute"      # Second/Hour/Minute/Day
        p['Scraping Strategy'] = 'Individual'  # By Feed/Individual/On Refresh
        return p

    def appearance_preferences(self):
        return self.preferences['Appearance']

    def feeds_preferences(self):
        return self.preferences['Feeds']

    def filtration_preferences(self):
        return self.preferences['Filtration']

    def retrieval_preferences(self):
        return self.preferences['Retrieval']

    def load_config(self):
        self.ensure_directory_exists()
        self.preferences = self.load_file(self.preferences_file, self.preferences)

        if not self.preferences['Feeds']:  # If there were no feeds listed in the preferences file
            self.preferences['Feeds'] = dict()  # Replace None with an empty dictionary
        else:
            # Since we used JSON and not pickling, need to transform the serialized feed information into Feed objects
            feed_object_dict = dict()
            for feed_name, feed_attributes in self.preferences['Feeds'].items():
                feed_object_dict[feed_name] = Feed.from_dict(feed_attributes)
            self.preferences['Feeds'] = feed_object_dict

    def ensure_directory_exists(self):
        """ Checks to see if the preference file's directory exists, and if it doesn't creates it. """
        try:
            os.makedirs(self.config_home)
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise

    def feeds(self):
        return self.preferences['Feeds']

    def feed_list(self):
        return self.feeds().values()

    def get_feed(self, name):
        if name in self.feeds():
            return self.feeds()[name]
        else:
            return None

    def add_feed(self, name, uri):
        self.preferences['Feeds'][name] = Feed(name, uri)
        self.update_preferences(self.preferences)

    def update_file(self, filename, data):
        file_path = os.path.join(self.config_home, filename)
        with open(file_path, 'w') as data_file:
            json.dump(data, data_file)

    def update_preferences(self, preferences):
        """ Convenience function """
        self.update_file(self.preferences_file, self.serialize_preferences(preferences))
        self.preferences = preferences

    @staticmethod
    def serialize_preferences(preferences): # TODO: Optimize this, deep copying is wasteful
        temp = deepcopy(preferences)
        for feed in preferences['Feeds'].values():
            temp['Feeds'][feed.name] = feed.to_dict()
        return temp

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