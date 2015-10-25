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

from gi.repository import Gtk, Gio, Gdk
from gi.repository import Pango
from newsView import NewsView
from textFormat import TextFormat

class SplitNews(NewsView):
    """ GUI component where headlines and story contents are split apart """
    def __init__(self, config, gatherer):
        self.config = config
        self.gatherer = gatherer
        self.headlines = list()
        self.buffers = list()
        self.headline_scroll, self.headline_store = None, None
        self.treeview = None
        self.top_pane = None
        self.text_scroll = None

    def create_display(self):
        self.top_pane = Gtk.Paned(orientation=Gtk.Orientation.HORIZONTAL)

        self.headline_scroll = Gtk.ScrolledWindow()
        self.headline_scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.ALWAYS)
        self.headline_store = Gtk.ListStore(str, str, int)
        self.headline_scroll.set_size_request(100, 100)
        self.treeview = Gtk.TreeView(model=self.headline_store)

        self.headline_scroll.add(self.treeview)

        self.text_scroll = Gtk.ScrolledWindow()
        self.text_scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.ALWAYS)
        self.text_view = Gtk.TextView()
        tb = self.text_view.get_buffer()

        self.text_view.set_size_request(200,200)
        tb.insert(tb.get_end_iter(), " "*200)
        self.text_view.set_editable(False)
        self.text_view.set_cursor_visible(False)

        self.text_scroll.add(self.text_view)

        self.top_pane.pack1(self.headline_scroll, resize=True, shrink=False)
        self.top_pane.pack2(self.text_scroll, resize=True, shrink=False)
        self.top_pane.show_all()
        return self.top_pane

    def destroy_display(self):
        for child in self.top_pane:
            child.destroy()
        self.top_pane.destroy()

    def change_position(self, delta):
        """ Switches keyboard focus between left and right pane """
        if delta < 0:
            self.treeview.grab_focus()
        else:
            self.text_view.grab_focus()

    def refresh(self):
        self.headline_store.clear()
        self.text_scroll.child.destroy()

    def open_link(self, url=""):
        if not url:
            pass
            #super.open_link(url=url)

    def populate(self, items):

        i = 0
        for item in items:
            print(item.label, item.title)
            self.headline_store.append(list([item.label, item.title, i]))
            i += 1

        columns = ('Label', 'Headline')
        for i in range(len(columns)):
            cell = Gtk.CellRendererText()
            if i == 0:
                cell.props.weight_set = True
                cell.props.weight = Pango.Weight.BOLD
            cell.set_visible(True)
            col = Gtk.TreeViewColumn(columns[i], cell, text=i)

            self.treeview.append_column(col)
        self.treeview.get_selection().connect("changed", self.show_new_article)

    def show_new_article(self, selection):
        (model, iter) = selection.get_selected()
        selected_item = self.gatherer.collected_items[model[iter][2]]
        TextFormat.full_story(selected_item, self.text_view)



