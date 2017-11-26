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
from typing import Dict, List, Optional, Union

from gi import require_version
require_version('Gtk', '3.0')
from gi.repository import Gio, Gtk


from feed import Feed
from utilityFunctions import ensured_read_json_file, write_json_file


# FIXME: Refactor nested preferences dict to member variables
class Preferences:
    """ Deals with configuration data that survives between sessions
        Examples are appearance settings, added feeds, filters, etc. """

    def __init__(self, load_from_file: bool = False):
        self.preferences_directory = os.path.join(os.path.expanduser('~'), '.config', 'trough')
        self.preferences_file = 'preferences.json'
        # TODO: Make load_from_file completely independent of default_preferences.
        self.preferences = self.default_preferences()

        if load_from_file:
            self.load_preferences()

    @staticmethod
    def default_preferences() -> Dict[str, Dict[str, Union[str, Feed]]]:
        preferences = {
            'Appearance': Preferences.default_appearance_preferences(),
            'Feeds': Preferences.default_feeds_preferences(),
        }
        return preferences

    @staticmethod
    def default_appearance_preferences() -> Dict[str, str]:
        gs = Gio.Settings('org.gnome.desktop.interface')
        default_font = gs.get_string('font-name')
        document_font = gs.get_string('document-font-name')
        if not default_font and document_font:
            default_font = document_font
        elif not document_font and default_font:
            document_font = default_font

        return {
            'View': 'Three-Pane',
            'Category Font': '10 Sans, sans-serif',
            'Headline Font': '10 Sans, sans-serif',
            'Story Font': '10 Sans, sans-serif',
            'Font Color': '#000000',  # solid black
            'Background Color': '#ffffff',  # solid white
            'Selection Font Color': '#ffffff',  # solid white
            'Selection Background Color': '#517ead',  # medium-dark blue
            'Read Color': '#75507b',  # a 'clicked-link' purple
            'Filtered Color': '#c02f1d',  # a dull uninviting red
        }

    @staticmethod
    def default_feeds_preferences() -> Dict[str, Feed]:
        return dict()

    def appearance_preferences(self) -> Dict[str, str]:
        return self.preferences['Appearance']

    def feeds_preferences(self) -> Dict[str, Feed]:
        return self.preferences['Feeds']

    def load_preferences(self) -> None:
        self.preferences = ensured_read_json_file(
                self.preferences_directory,
                self.preferences_file,
                self.preferences)

        if 'Feeds' not in self.preferences:
            self.preferences['Feeds'] = self.default_feeds_preferences()
        else:
            feed_object_dict = dict()
            for feed_name, feed_attributes in self.preferences['Feeds'].items():
                feed_object_dict[feed_name] = Feed.from_dict(feed_attributes)
            self.preferences['Feeds'] = feed_object_dict

    def feeds(self) -> dict:
        return self.preferences['Feeds']

    def feed_list(self) -> List[Feed]:
        return list(self.feeds().values())

    def get_feed(self, name: str) -> Optional[Feed]:
        try:
            return self.feeds()[name]
        except KeyError:
            return None

    def add_feed(self, feed: Feed) -> None:
        self.preferences['Feeds'][feed.name] = feed
        self.update_preferences(self.preferences)

    def write_preferences(self) -> None:
        write_json_file(
                self.preferences_directory,
                self.preferences_file,
                self.serialize_preferences(self.preferences))

    def update_preferences(self, preferences: Dict[str, Dict[str, Union[str, Feed]]]) -> None:
        """ Convenience function """
        if preferences:
            self.preferences = preferences
            self.write_preferences()

    @staticmethod
    def serialize_preferences(preferences) -> Dict[str, dict]:  # FIXME: Serialize doesn't return a string?
        temp = copy.copy(preferences)
        temp['Feeds'] = dict()
        for feed in preferences['Feeds'].values():
            temp['Feeds'][feed.name] = feed.to_dict()
        return temp

    def get_appearance_css(self) -> bytes:
        ap = self.appearance_preferences()
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
        return css.encode()
