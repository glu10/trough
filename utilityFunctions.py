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

import errno
import json
import os
from typing import Any, Callable

from gi import require_version

require_version('Gtk', '3.0')
require_version('Gdk', '3.0')
from gi.repository import Gdk, Gio, Gtk

""" FILE OPERATIONS """


def ensure_directory_exists(directory: str):
    """ Checks to see if the given directory exists, and if it doesn't creates it. """
    try:
        os.makedirs(directory)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise


def ensured_read_json_file(containing_directory: str, filename: str, defaults: Any):
    """ Read a JSON file or pass back the defaults if the file doesn't exist. """
    file_path = os.path.join(containing_directory, filename)
    if not os.path.isfile(file_path):
        return defaults

    with open(file_path, 'r') as data_file:
        try:
            return json.load(data_file)
        except json.decoder.JSONDecodeError as e:
            raise RuntimeError('Error parsing the JSON in ' + file_path + ', is it valid JSON?') from e


def write_json_file(containing_directory: str, filename: str, data):
    ensure_directory_exists(containing_directory)
    file_path = os.path.join(containing_directory, filename)
    with open(file_path, 'w') as data_file:
        json.dump(data, data_file)


""" END FILE OPERATIONS """

""" GENERIC DIALOGS """


def warning_popup(window: Gtk.Window, first: str, second: str) -> None:
    warning = Gtk.MessageDialog(window, 0, Gtk.MessageType.WARNING, Gtk.ButtonsType.OK, first)
    warning.format_secondary_text(second)
    warning.run()
    warning.destroy()


def decision_popup(window: Gtk.Window, first: str, second: str) -> bool:
    decision = Gtk.MessageDialog(window, 0, Gtk.MessageType.WARNING, Gtk.ButtonsType.OK_CANCEL, first)
    decision.format_secondary_text(second)
    response = decision.run()
    decision.destroy()
    return response == Gtk.ResponseType.OK


""" END GENERIC DIALOGS """


def make_button(
        theme_icon_string: str = None,
        backup_icon_string: str = None,
        signal: str = None,
        signal_func: Callable = None,
        tooltip: str = None) -> Gtk.Button:
    button = Gtk.Button()

    if theme_icon_string:
        if backup_icon_string and not Gtk.IconTheme.get_default().has_icon(theme_icon_string):
            icon = Gio.ThemedIcon(name=backup_icon_string)
        else:
            icon = Gio.ThemedIcon(name=theme_icon_string)

        image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
        button.add(image)

    if signal and signal_func:
        button.connect(signal, signal_func)

    if tooltip:
        button.set_tooltip_text(tooltip)

    return button


def string_to_RGBA(color_text: str) -> Gdk.RGBA:
    rgba = Gdk.RGBA()
    if not rgba.parse(color_text):
        raise RuntimeError('RGBA parsing error when parsing ' + color_text)
    return rgba
