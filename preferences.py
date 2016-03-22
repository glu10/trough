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

import os
from gi.repository import Gio
from feed import Feed
from filter import Filter
import copy
from utilityFunctions import load_file, write_file


class Preferences:
    """ Deals with configuration data that survives between sessions
        Examples are appearance settings, added feeds, filters, etc. """

    def __init__(self, load_from_file=False):
        self.preferences_directory = os.path.join(os.path.expanduser('~'), '.config', 'trough')
        self.preferences_file = 'preferences.json'
        self.preferences = self.default_preferences()

        if load_from_file:
            self.load_preferences()

    @staticmethod
    def default_preferences():
        preferences = dict()
        preferences['Appearance'] = Preferences.default_appearance_preferences()
        preferences['Feeds'] = Preferences.default_feeds_preferences()
        preferences['Filters'] = Preferences.default_filtration_preferences()
        return preferences

    @staticmethod
    def default_appearance_preferences():
        p = dict()
        p['View'] = 'Three-Pane'

        # TODO: Investigate if these font strings are reliably set among different DEs/WMs
        gs = Gio.Settings('org.gnome.desktop.interface')
        default_font = gs.get_string('font-name')
        document_font = gs.get_string('document-font-name')

        p['Category Font'] = default_font
        p['Headline Font'] = default_font
        p['Story Font'] = document_font

        p['Font Color'] = 'rgba(0, 0, 0, 1.0)'  # solid black
        p['Background Color'] = 'rgba(255, 255, 255, 1.0)'  # solid white
        p['Selection Font Color'] = 'rgba(255, 255, 255, 1.0)'  # solid white
        p['Selection Background Color'] = 'rgba(81, 126, 173, 1.0)'  # medium-dark blue
        p['Read Color'] = 'rgba(117, 80, 123, 1.0)'  # a 'clicked-link' purple.
        p['Filtered Color'] = 'rgba(192, 47, 29, 1.0)'  # a dull uninviting red
        return p

    @staticmethod
    def default_feeds_preferences():
        return dict()

    @staticmethod
    def default_filtration_preferences():
        p = list()
        return p

    def appearance_preferences(self):
        return self.preferences['Appearance']

    def feeds_preferences(self):
        return self.preferences['Feeds']

    def filtration_preferences(self):
        return self.preferences['Filters']

    def load_preferences(self):
        self.preferences = load_file(self.preferences_directory, self.preferences_file, self.preferences)

        if self.preferences['Feeds'] is None:
            self.preferences['Feeds'] = dict()
        else:
            # Since we used JSON and not pickling, need to transform the serialized feed information into Feed objects
            feed_object_dict = dict()
            for feed_name, feed_attributes in self.preferences['Feeds'].items():
                feed_object_dict[feed_name] = Feed.from_dict(feed_attributes)
            self.preferences['Feeds'] = feed_object_dict

        if self.preferences['Filters'] is None:
            self.preferences['Filters'] = list()
        else:
            filter_objects = list()
            for filt, case_sensitive, hide_matches in self.preferences['Filters']:
                filter_objects.append(Filter(filt, case_sensitive, hide_matches))
            self.preferences['Filters'] = filter_objects

    def feeds(self):
        return self.preferences['Feeds']

    def filters(self):
        return self.preferences['Filters']

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

    def write_preferences(self):
        write_file(self.preferences_directory, self.preferences_file, self.serialize_preferences(self.preferences))

    def update_preferences(self, preferences):
        """ Convenience function """
        assert(type(preferences) == dict)
        if preferences:
            self.preferences = preferences
            self.write_preferences()

    @staticmethod
    def serialize_preferences(preferences):
        temp = copy.copy(preferences)
        temp['Feeds'] = dict()
        for feed in preferences['Feeds'].values():
            temp['Feeds'][feed.name] = feed.to_dict()

        temp['Filters'] = list()
        for f in preferences['Filters']:
            temp['Filters'].append([f.filter, f.case_sensitive, f.hide_matches])
        return temp

    def get_appearance_css(self):
        ap = self.appearance_preferences()
        p = (
             'TroughWindow GtkTreeView, GtkTextView {\n'
             '   background-color: ' + ap['Background Color'] + ';\n'
             '   color: ' + ap['Font Color'] + ';\n'
             '}\n'
             'TroughWindow GtkTreeView:selected, GtkTextView:selected {\n'
             '    background-color: ' + ap['Selection Background Color'] + ';\n'
             '    color: ' + ap['Selection Font Color'] + ';\n'
             '}\n'
             'TroughWindow GtkTextView {'
             '    font: ' + ap['Story Font'] + ';\n'
             '}\n'
             'TroughWindow GtkTreeView {\n'
             '    font: ' + ap['Headline Font'] + ';\n'
             '}\n'
            )
        return p.encode()
