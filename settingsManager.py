## Settings window goes here

from gi.repository import Gtk

## TODO: Design is still being fleshed out

class SettingsManager(Gtk.Dialog):
    def __init__(self, parent):
        Gtk.Dialog.__init__(self, "Settings", parent, 0, (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                                          Gtk.STOCK_OK, Gtk.ResponseType.OK))
        self.set_default_size(200, 200)
        self.currently_displayed = None

        self.settings_categories = ['Appearance', 'Feeds', 'Filtration', 'Retrieval']
        # self.content_creation_functions = [Appearance, Feeds, filtration, retrieval]

        box = Gtk.Dialog.get_content_area()

        box.pack_start(self.create_category_list(self.settings_categories))

        self.frame = Gtk.Frame()
        box.pack_end(self.frame)

    def create_category_list(self, settings_categories):
        cat_store = Gtk.ListStore(str, int)
        tree_view = Gtk.TreeView(model=cat_store)
        tree_view.get_selection().connect("changed", self.display_category)

    def display_new_category(self, selection):
        if selection:
            model, iter = selection.get_selected()
            # Grab the settings dictionary returned by
            self.currently_displayed.destroy()
            #content_creation_functions[model[iter][1]
            self.box.pack_end()

    def create_settings_box(self, category, content_creation_function):
        frame = Gtk.Frame(category)

        frame.add(content_creation_function())



