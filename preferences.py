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

import copy
import os

from gi.repository import Gio, Gtk 

from feed import Feed
from item_filter import ItemFilter
from utilityFunctions import load_file, write_file


class Preferences:
    """ Deals with configuration data that survives between sessions
        Examples are appearance settings, added feeds, filters, etc. """

    def __init__(self, load_from_file=False):
        self.preferences_directory = os.path.join(os.path.expanduser('~'), '.config', 'trough')
        self.preferences_file = 'preferences.json'
        # TODO: Make load_from_file completely independant of default_preferences.
        self.preferences = self.default_preferences()

        if load_from_file:
            self.load_preferences()

    @staticmethod
    def default_preferences():
        preferences = {
            'Appearance': Preferences.default_appearance_preferences(),
            'Feeds': Preferences.default_feeds_preferences(),
            'Filters': Preferences.default_filtration_preferences(),
            #'Categories': Preferences.default_categories_preferences(), 
        }
        return preferences

    @staticmethod
    def default_appearance_preferences():
        gs = Gio.Settings('org.gnome.desktop.interface')
        default_font = gs.get_string('font-name')
        document_font = gs.get_string('document-font-name')
        if not default_font and document_font:
            default_font = document_font
        elif not document_font and default_font:
            document_font = default_font

        p = {
            'View': 'Three-Pane',
            'Category Font': default_font,
            'Headline Font': default_font,
            'Story Font': document_font,
            'Font Color': 'rgba(0, 0, 0, 1.0)',  # solid black
            'Background Color': 'rgba(255, 255, 255, 1.0)',  # solid white
            'Selection Font Color': 'rgba(255, 255, 255, 1.0)',  # solid white
            'Selection Background Color': 'rgba(81, 126, 173, 1.0)',  # medium-dark blue
            'Read Color': 'rgba(117, 80, 123, 1.0)',  # a 'clicked-link' purple
            'Filtered Color': 'rgba(192, 47, 29, 1.0)',  # a dull uninviting red
        }
        return p

    @staticmethod
    def default_feeds_preferences():
        return dict()

    @staticmethod
    def default_filtration_preferences():
        return list()

    @staticmethod
    def default_categories_preferences():
        return Gtk.ListStore()

    def appearance_preferences(self):
        return self.preferences['Appearance']

    def feeds_preferences(self):
        return self.preferences['Feeds']

    def filtration_preferences(self):
        return self.preferences['Filters']

    def load_preferences(self):
        self.preferences = load_file(self.preferences_directory, self.preferences_file, self.preferences)

        if self.preferences['Feeds'] is None:
            self.preferences['Feeds'] = self.default_feeds_preferences()
        else:
            # Since we used JSON and not pickling, need to transform the serialized feed information into Feed objects
            feed_object_dict = dict()
            for feed_name, feed_attributes in self.preferences['Feeds'].items():
                feed_object_dict[feed_name] = Feed.from_dict(feed_attributes)
            self.preferences['Feeds'] = feed_object_dict
            #self.preferences['Categories'] = self.construct_categories()

        if self.preferences['Filters'] is None:
            self.preferences['Filters'] = self.default_filtration_preferences()
        else:
            filter_objects = list()
            for filt, case_sensitive, hide_matches in self.preferences['Filters']:
                filter_objects.append(Filter(filt, case_sensitive, hide_matches))
            self.preferences['Filters'] = filter_objects

   # def categories(self):
   #     return self.preferences['Categories']

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

   # def construct_categories(self):
   #     # Reconstruct category list from the current feeds
   #     categories = {feed.category for feed in self.feed_list()}
   #     categories.sort()
   #
   #     category_store = Gtk.ListStore()
   #     for category in categories:
   #         category_store.append(category)
   #     return category_store

    def add_feed(self, feed):
        self.preferences['Feeds'][feed.name] = feed
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
        if Gtk.get_major_version() == 3 and Gtk.get_minor_version() >= 20:  # GTK 3.20 broke previous CSS
            css = (
                '#storyview text, #labelview, #headlineview{\n'
                '   background-color: ' + ap['Background Color'] + ';\n'
                '   color: ' + ap['Font Color'] + ';\n'
                '}\n'
                '* + #labelview, * + #headlineview{\n'
                '   background-color: ' + ap['Background Color'] + ';\n'
                '}\n'
                '#storyview selection, #labelview:selected, #headlineview:selected{\n'
                '    background-color: ' + ap['Selection Background Color'] + ';\n'
                '    color: ' + ap['Selection Font Color'] + ';\n'
                '}\n'
                '#storyview {'
                '    font: ' + ap['Story Font'] + ';\n'
                '}\n'
                '#headlineview {\n'
                '    font: ' + ap['Headline Font'] + ';\n'
                '}\n'
            )
        else:
            css = (
                '#storyview, #labelview, #headlineview {\n'
                '   background-color: ' + ap['Background Color'] + ';\n'
                '   color: ' + ap['Font Color'] + ';\n'
                '}\n'
                '#storyview:selected, #labelview:selected, #headlineview:selected {\n'
                '    background-color: ' + ap['Selection Background Color'] + ';\n'
                '    color: ' + ap['Selection Font Color'] + ';\n'
                '}\n'
                '#storyview {'
                '    font: ' + ap['Story Font'] + ';\n'
                '}\n'
                '#headlineview {\n'
                '    font: ' + ap['Headline Font'] + ';\n'
                '}\n'
            )
        return css.encode()
