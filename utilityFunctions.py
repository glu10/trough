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
from gi.repository import Gtk

def feedparser_parse(uri):
    """
    This function is only necessary because of a feedparser bug that occurs in Python versions <= 3.4
    The try catch probes and attempts to mitigate the bug by switching which underlying XML parser is used.
    """
    try:
        content = feedparser.parse(uri)  # Should actually cache the feed, then only update if it's out of date.
    except TypeError:
        if 'drv_libxml2' in feedparser.PREFERRED_XML_PARSERS:
            feedparser.PREFERRED_XML_PARSERS.remove('drv_libxml2')
            content = feedparser.parse(uri)
    try:
        if content['entries']:
            return content
    except (TypeError, KeyError):
        return None


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