#!/usr/bin/env python

"""
Explorer window for BrowseNodes. Simply double-click on an entry to load the
corresponding node from the web service.
"""
import sys
import os

sys.path.append("/usr/lib/python2.7/dist-packages")
sys.path.append("/usr/lib/python2.7/dist-packages/gtk-2.0")

import gtk
from amazonproduct.api import API

AWS_ACCESS_KEY_ID = os.environ.get('AWS_PRODUCT_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_PRODUCT_SECRET_ACCESS_KEY')
AWS_ASSOCIATE_TAG = os.environ.get('AWS_ASSOCIATE_TAG')
AWS_LOCALE = os.environ.get('AWS_LOCALE')

#: a list of root nodes retrieved from
#: http://docs.amazonwebservices.com/AWSECommerceService/2009-11-01/DG/index.html?BrowseNodeIDs.html
NODE_IDS = {
    'ca': {
        'Books': 927726,
        'Classical': 962454,
        'DVD': 14113311,
        'Electronics': 677211011,
        'ForeignBooks': 927726,
        'Kitchen': 2206275011,
        'Music': 962454,
        'Software': 3234171,
        'SoftwareVideoGames': 3323751,
        'VHS': 962072,
        'Video': 962454,
        'VideoGames': 110218011,
    },
    'de': {
        'Apparel': 78689031,
        'Automotive': 78194031,
        'Baby': 357577011,
        'Beauty': 64257031,
        'Books': 541686,
        'Classical': 542676,
        'DVD': 547664,
        'Electronics': 569604,
        'ForeignBooks': 54071011,
        'HealthPersonalCare': 64257031,
        'HomeGarden': 10925241,
        'Jewelry': 327473011,
        'Kitchen': 3169011,
        'Lighting': 213083031,
        'Magazines': 1198526,
        'MP3Downloads': 77256031,
        'Music': 542676,
        'OfficeProducts': 16291311,
        'OutdoorLiving': 10925051,
        'PCHardware': 569604,
        'Photo': 569604,
        'Software': 542064,
        'SoftwareVideoGames': 541708,
        'SportingGoods': 16435121,
        'Toys': 12950661,
        'VHS': 547082,
        'Video': 547664,
        'VideoGames': 541708,
        'Watches': 193708031,
    },
    'fr': {
        'Baby': 206617031,
        'Beauty': 197858031,
        'Books': 468256,
        'Classical': 537366,
        'DVD': 578608,
        'Electronics': 1058082,
        'ForeignBooks': 69633011,
        'HealthPersonalCare': 197861031,
        'Jewelry': 193711031,
        'Kitchen': 57686031,
        'Lighting': 213080031,
        'MP3Downloads': 206442031,
        'Music': 537366,
        'OfficeProducts': 192420031,
        'Shoes': 215934031,
        'Software': 548012,
        'SoftwareVideoGames': 548014,
        'Toys': 548014,
        'VHS': 578610,
        'Video': 578608,
        'VideoGames': 548014,
        'Watches': 60937031,
    },
    'jp': {
        'Apparel': 361299011,
        'Automotive': 2017304051,
        'Baby': 13331821,
        'Beauty': 52391051,
        'Books': 465610,
        'Classical': 562032,
        'DVD': 562002,
        'Electronics': 3210991,
        'ForeignBooks': 388316011,
        'Grocery': 57240051,
        'HealthPersonalCare': 161669011,
        'Hobbies': 13331821,
        'HomeImprovement': 2016929051,
        'Jewelry': 85896051,
        'Kitchen': 3839151,
        'Music': 562032,
        'Shoes': 2016926051,
        'Software': 637630,
        'SportingGoods': 14315361,
        'Toys': 13331821,
        'VHS': 561972,
        'Video': 561972,
        'VideoGames': 637872,
        'Watches': 14315361,
    },
    'uk': {
        'Apparel': 83451031,
        'Automotive': 248877031,
        'Baby': 60032031,
        'Beauty': 66280031,
        'Books': 1025612,
        'Classical': 505510,
        'DVD': 283926,
        'Electronics': 560800,
        'HealthPersonalCare': 66280031,
        'HomeGarden': 11052591,
        'Jewelry': 193717031,
        'Kitchen': 11052591,
        'Lighting': 213077031,
        'MP3Downloads': 77198031,
        'Music': 505510,
        'OfficeProducts': 560800,
        'OutdoorLiving': 11052591,
        'Software': 1025614,
        'SoftwareVideoGames': 1025616,
        'SportingGoods': 319530011,
        'Tools': 11052591,
        'Toys': 712832,
        'VHS': 283926,
        'Video': 283926,
        'VideoGames': 1025616,
        'Watches': 595312,
    },
    'us': {
        'Apparel': 1036682,
        'Automotive': 15690151,
        'Baby': 1036682,
        'Beauty': 11055981,
        'Books': 1000,
        'Classical': 301668,
        'DigitalMusic': 195208011,
        'DVD': 130,
        'Electronics': 493964,
        'GourmetFood': 3580501,
        'Grocery': 3760931,
        'HealthPersonalCare': 3760931,
        'HomeGarden': 285080,
        'Industrial': 228239,
        'Jewelry': 3880591,
        'Kitchen': 1063498,
        'Magazines': 599872,
        'Merchants': 493964,
        'Miscellaneous': 10304191,
        'MP3Downloads': 195211011,
        'Music': 301668,
        'MusicalInstruments': 11965861,
        'OfficeProducts': 1084128,
        'OutdoorLiving': 1063498,
        'PCHardware': 493964,
        'PetSupplies': 1063498,
        'Photo': 493964,
        'Software': 409488,
        'SportingGoods': 1079730,
        'Tools': 468240,
        'Toys': 493964,
        'VHS': 404272,
        'Video': 130,
        'VideoGames': 493964,
        'Watches': 1079730,
        'Wireless': 508494,
        'WirelessAccessories': 13900851,
    },
}


class BrowseNodeExplorer(gtk.Window):

    """
    Gtk explorer for Amazon BrowseNodes.
    """

    def on_delete(self, widget, event, data=None):
        # closes the window and quits.
        gtk.main_quit()
        return False

    def on_tree_click(self, widget, event, data=None):
        # if double click
        if event.type == gtk.gdk._2BUTTON_PRESS:

            # get data from highlighted selection
            treeselection = self.treeview.get_selection()
            model, iter = treeselection.get_selected()
            name_of_data = self.treestore.get_value(iter, 0)

            # and fetch selected node
            self.fetch_nodes(name_of_data)

    def __init__(self, locale='fr'):

        gtk.Window.__init__(self, gtk.WINDOW_TOPLEVEL)

        self.set_title("BrowseNode Explorer")
        self.set_size_request(800, 600)
        self.connect("delete_event", self.on_delete)

        self.locale = locale

        self.api = API(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, self.locale)

        # create a TreeStore with one string column to use as the model
        self.treestore = gtk.TreeStore(int, str)

        # create the TreeView using treestore
        self.treeview = gtk.TreeView(self.treestore)

        # add column id
        renderer = gtk.CellRendererText()
        column = gtk.TreeViewColumn('id', renderer, text=0)
        self.treeview.append_column(column)

        # add column name
        renderer = gtk.CellRendererText()
        column = gtk.TreeViewColumn('name', renderer, text=1)
        column.set_sort_column_id(1)  # Allow sorting on the column
        self.treeview.append_column(column)

        # make it clickable
        self.treeview.add_events(gtk.gdk.BUTTON_PRESS_MASK)
        self.treeview.connect('button_press_event', self.on_tree_click)

        scrolled = gtk.ScrolledWindow()
        scrolled.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scrolled.add(self.treeview)

        self.add(scrolled)
        self.show_all()

        # populate with root nodes
        # but avoid duplicated node ids
        node_ids = set(NODE_IDS[self.locale].values())
        for name, id in NODE_IDS[self.locale].items():
            if id in node_ids:
                self.treestore.append(None, [id, name])
                node_ids.remove(id)

    def _find_row(self, node_id):
        def match_func(row, data):
            # data is a tuple containing column number, key
            column, key = data
            return row[column] == key

        def search(rows, func, data):
            if not rows:
                return None
            for row in rows:
                if func(row, data):
                    return row
                result = search(row.iterchildren(), func, data)
                if result:
                    return result
            return None
        return search(self.treestore, match_func, (0, node_id))

    def fetch_nodes(self, node_id):
        """
        Fetches a BrowseNode from Amazon.
        """
        # fetch matching row from treestore
        row = self._find_row(node_id)

        # fetch Amazon data
        node = self.api.browse_node_lookup(node_id, AssociateTag=AWS_ASSOCIATE_TAG).BrowseNodes.BrowseNode
        id = node.BrowseNodeId.pyval
        name = node.Name.pyval
        is_root = hasattr(node, 'IsCategoryRoot') and \
                                    node.IsCategoryRoot.pyval == 1

        # replace node name
        if is_root:
            row[1] = node.Ancestors.BrowseNode.Name.text
        else:
            row[1] = name

        try:
            children = dict((child.BrowseNodeId.pyval, child.Name.pyval)
                        for child in node.Children.BrowseNode)
        except AttributeError:
            children = {}

        for child_id, child_name in children.items():
            self.treestore.append(row.iter, [child_id, child_name])

        # expand nodes of just added
        self.treeview.expand_row(tuple(row.path), True)

    def main(self):
        gtk.main()

if __name__ == "__main__":
    explorer = BrowseNodeExplorer(locale=AWS_LOCALE)
    explorer.main()
