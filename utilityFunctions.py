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

"""
This file contains functions that are used in multiple places within Trough that have a similar purpose.
The functions are being declared here for consistency's sake.
"""

import feedparser
from gi.repository import Gtk, Gdk, Gio
import os
import json
import errno

def feedparser_parse(uri):
    """
    This function is only necessary because of a feedparser bug that occurs in Python versions <= 3.4
    The try catch probes and attempts to mitigate the bug by switching which underlying XML parser is used.
    """
    try:
        content = feedparser.parse(uri)
    except TypeError:
        if 'drv_libxml2' in feedparser.PREFERRED_XML_PARSERS:
            feedparser.PREFERRED_XML_PARSERS.remove('drv_libxml2')
            content = feedparser.parse(uri)
    try:
        if content['entries']:
            return content
    except (TypeError, KeyError):
        return None


""" FILE OPERATIONS """


def ensure_directory_exists(directory):
    """ Checks to see if the given directory exists, and if it doesn't creates it. """
    try:
        os.makedirs(directory)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise


def load_file(containing_directory, filename, defaults):
    """ Check if the specified file exists, and if it doesn't make a file with the default configuration """

    ensure_directory_exists(containing_directory)

    file_path = os.path.join(containing_directory, filename)
    data = dict()

    # If the file doesn't exist or is empty
    if not os.path.isfile(file_path) or os.stat(file_path).st_size == 0:
        if defaults:  # If there are defaults, write them to replace the empty/nonexistent file
            write_file(containing_directory, filename, defaults)
            data = defaults
        else:
            return defaults  # Just fake as if we loaded the defaults
    else:  # If there is a file
        with open(file_path, 'r') as data_file:
            try:
                data = json.load(data_file)
            except json.decoder.JSONDecodeError:
                raise RuntimeError('Error parsing the JSON in ' + file_path + ', is it valid JSON?')
            # Make sure that the information we are getting actually corresponds to real preferences.
            if defaults and type(defaults==dict) and sorted(data.keys()) != sorted(defaults.keys()):
                raise RuntimeError('Data in ' + file_path + ' did not match expectations,' +
                                                            ' fix the problem or delete the file.')
    return data


def write_file(containing_directory, filename, data):

    ensure_directory_exists(containing_directory)

    file_path = os.path.join(containing_directory, filename)
    with open(file_path, 'w') as data_file:
        json.dump(data, data_file)

""" END FILE OPERATIONS """


""" GENERIC DIALOGS """


def warning_popup(window, first, second):
    warning = Gtk.MessageDialog(window, 0, Gtk.MessageType.WARNING, Gtk.ButtonsType.OK, first)
    warning.format_secondary_text(second)
    warning.run()
    warning.destroy()


def decision_popup(window, first, second):
    decision = Gtk.MessageDialog(window, 0, Gtk.MessageType.WARNING, Gtk.ButtonsType.OK_CANCEL, first)
    decision.format_secondary_text(second)
    response = decision.run()
    decision.destroy()

    if response == Gtk.ResponseType.OK:
        return True
    else:
        return False

""" END GENERIC DIALOGS """


def make_button(theme_icon_string=None, backup_icon_string=None, signal=None, function=None, tooltip_text=None):
    button = Gtk.Button()

    if theme_icon_string:
        if backup_icon_string and not Gtk.IconTheme.get_default().has_icon(theme_icon_string):
            icon = Gio.ThemedIcon(name=backup_icon_string)
        else:
            icon = Gio.ThemedIcon(name=theme_icon_string)

        image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
        button.add(image)

    if signal and function:
        button.connect(signal, function)

    if tooltip_text:
        button.set_tooltip_text(tooltip_text)

    return button


def string_to_RGBA(rgba_string):
            rgba = Gdk.RGBA()
            if not rgba.parse(rgba_string):
                raise RuntimeError('RGBA parsing error when parsing ' + rgba_string)
            return rgba