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

from gi.repository import Gtk, Gdk
from gi.repository import Pango
from newsView import NewsView
from textFormat import TextFormat
from utilityFunctions import string_to_RGBA

class SplitNews(NewsView):
    """ GUI component where headlines and story contents are split apart """
    def __init__(self, config, gatherer):
        self.config = config
        self.gatherer = gatherer
        self.last_item_index = -1
        self.refreshing = False  # Set to true while refreshing to ignore selection changes

        # GUI components
        self.top_pane = Gtk.Paned(orientation=Gtk.Orientation.HORIZONTAL)
        self.headline_store = Gtk.ListStore(str, str, int)
        self.tree_view = self.create_tree_view(self.headline_store)
        self.headline_scroll = self.create_headline_box(self.tree_view)
        self.text_scroll, self.text_view = self.create_text_box()
        self.update_appearance(config.appearance_preferences())

        self.top_pane.pack1(self.headline_scroll, resize=True, shrink=False)  # Left
        self.top_pane.pack2(self.text_scroll, resize=True, shrink=False)  # Right

    def create_tree_view(self, headline_store):
        tree_view = Gtk.TreeView(model=headline_store)
        tree_view.get_selection().connect("changed", self.show_new_article)

        columns = ('Label', 'Headline')
        for i in range(len(columns)):
            cell = Gtk.CellRendererText()
            if i == 0:  # Label
                cell.props.weight_set = True
                cell.props.weight = Pango.Weight.BOLD
            col = Gtk.TreeViewColumn(columns[i], cell, text=i)
            tree_view.append_column(col)
        return tree_view

    @staticmethod
    def create_headline_box(tree_view):
        headline_scroll = Gtk.ScrolledWindow()
        headline_scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.ALWAYS)
        headline_scroll.set_size_request(100, 100)
        headline_scroll.add(tree_view)
        return headline_scroll

    @staticmethod
    def create_text_box():
        text_scroll = Gtk.ScrolledWindow()
        text_scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.ALWAYS)
        text_view = Gtk.TextView()
        text_view.set_size_request(200, 200)
        text_view.set_editable(False)
        text_view.set_cursor_visible(False)
        tb = text_view.get_buffer()
        tb.insert(tb.get_end_iter(), " "*200)  # Placeholder
        text_scroll.add(text_view)
        return text_scroll, text_view

    def destroy_display(self):
        for child in self.top_pane:
            child.destroy()
        self.top_pane.destroy()

    def top_level(self):
        return self.top_pane

    def change_position(self, delta):
        """ Switches keyboard focus between left and right pane """
        if delta < 0:
            self.tree_view.grab_focus()
        else:
            self.text_view.grab_focus()

    def refresh(self, items):
        self.refreshing = True  # Toggling boolean as a hack to cover up the selection changed signal during the clear
        self.headline_store.clear()
        self.populate(items)
        self.refreshing = False

    def get_then_open_link(self, gatherer):
        active = gatherer.item(self.last_item_index)
        if active:
            super().open_link(active.link)

    def populate(self, items):
        for x, item in enumerate(items):
            title = item.title
            threshold = 100
            if len(item.title) > threshold: #TODO: Hardcoding this is poor form, make a more dynamic solution
                title = item.title[:threshold-3] + "..."

            self.headline_store.append(list([item.label, title, x]))

    def update_appearance(self, appearance_dict):

        # TODO: Deprecated override functions should be replaced with Gtk.CssProvider, but not sure how to do that yet.

        def font(font_string):
            return Pango.FontDescription(font_string)

        self.text_view.override_font(font(appearance_dict['Story Font']))
        self.tree_view.override_font(font(appearance_dict['Headline Font']))

        for v in (self.text_view, self.tree_view):
            v.override_color(Gtk.StateFlags.NORMAL, string_to_RGBA(appearance_dict['Font Color']))
            v.override_background_color(Gtk.StateFlags.NORMAL, string_to_RGBA(appearance_dict['Background Color']))

            # When text is selected, make it white text with a blue background.
            v.override_color(Gtk.StateFlags.SELECTED, string_to_RGBA(appearance_dict['Selection Font Color']))
            v.override_background_color(Gtk.StateFlags.SELECTED, string_to_RGBA(appearance_dict['Selection Background Color']))


    def show_new_article(self, selection):
        if not self.refreshing and selection:
            model, iter = selection.get_selected()
            if model:
                self.last_item_index = model[iter][2]
                TextFormat.full_story(self.gatherer.item(self.last_item_index), self.text_view)


