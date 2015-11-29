import sys
from idautils import *
from idaapi import *
import os
from os import listdir
from os.path import isfile
import copy
from pymongo import MongoClient
from datetime import datetime
import hashlib
import idc
import sark.qt
from idaapi import plugin_t
from pprint import pprint
from idaapi import PluginForm
import numpy as np
import matplotlib

matplotlib.use('Qt4Agg')
matplotlib.rcParams['backend.qt4']='PySide'

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
from PySide import QtGui, QtCore
import BinAuthorPlugin.Algorithms.FunctionFliterAndColorizer as FunctionFilter
import pluginConfigurations


    
class BinAuthorManager():
    def __init__(self):
        self._menu = sark.qt.MenuManager()
        self.addmenu_item_ctxs = []

    def message(self,s):
        print s
    
    def del_menu_items(self):
        for addmenu_item_ctx in self.addmenu_item_ctxs:
            idaapi.del_menu_item(addmenu_item_ctx)

        self._menu.clear()
        
    def buildMenu(self,functionFilter):
        self._menu = sark.qt.MenuManager()
        self._menu.add_menu("&BinAuthor")
        self.addmenu_item_ctxs.append(idaapi.add_menu_item("BinAuthor/", "Detect User Functions", "", 0, self.message, ("User function detection",)))
        self.addmenu_item_ctxs.append(idaapi.add_menu_item("BinAuthor/", "Choice 18", "", 0, self.message, ("Choice 18",)))
        self.addmenu_item_ctxs.append(idaapi.add_menu_item("BinAuthor/", "Choice 2", "", 0, self.message, ("Choice 2",)))
        self.addmenu_item_ctxs.append(idaapi.add_menu_item("BinAuthor/", "Choice 1", "", 0, self.message, ("Choice 1",)))
        self.addmenu_item_ctxs.append(idaapi.add_menu_item("BinAuthor/", "Author Indexing", "", 0, self.message, ("Author Indexing",)))
        self.addmenu_item_ctxs.append(idaapi.add_menu_item("BinAuthor/", "filtration", "", 0, functionFilter.run, ()))

class ParserView(PluginForm):
    """
    DIE Value View
    """
    def __init__(self):

        super(ParserView, self).__init__()
        self.data_parser = None
        self.ptable_widget = None

    def Show(self):

        return PluginForm.Show(self,
                               "Function Class View",
                               options=PluginForm.FORM_PERSIST)
    def OnCreate(self, form):
        """
        Called when the view is created
        """
        self.data_parser = DataParser.getParser()
        self.ptable_widget = QtGui.QTreeWidget()

        # Get parent widget
        self.parent = self.FormToPySideWidget(form)

        self._add_parser_data()

        layout = QtGui.QGridLayout()
        layout.addWidget(self.ptable_widget)

        self.parent.setLayout(layout)

    def _add_parser_data(self):
        """
        Add parser data to the parser widget model
        @return:
        """
        row = 0
        parser_list = self.data_parser.get_parser_list()
        if not "headers" in parser_list:
            return

        header_list = parser_list["headers"]
        header_list.insert(0, "Plugin Name")

        del parser_list["headers"]  # Remove headers item

        self.ptable_widget.setHeaderLabels(header_list)

        self.ptable_widget.setColumnWidth(0, 200)
        self.ptable_widget.setColumnWidth(1, 500)
        self.ptable_widget.setColumnWidth(2, 80)
        self.ptable_widget.setColumnWidth(3, 80)
        self.ptable_widget.setColumnWidth(4, 200)

        root_item = self.ptable_widget.invisibleRootItem()

        for parser in parser_list:
            current_row_item = QtGui.QTreeWidgetItem()
            current_row_item.setFlags(QtCore.Qt.ItemIsEnabled)
            current_row_item.setText(0, parser)

            num_columns = len(parser_list[parser])
            for column in xrange(0, num_columns):
                currext_text = str(parser_list[parser][column])
                current_row_item.setText(column+1, currext_text)
            b = QtGui.QPushButton('Test',)
            root_item.setItemWidget(current_row_item,2, b)
            print "hello"

            root_item.insertChild(row, current_row_item)
            row +=1

_parser_view = None
def initialize():
    global _parser_view
    _parser_view = ParserView()

def get_view():
    return _parser_view

class BinAuthor_plugin_t(plugin_t):
    flags = idaapi.PLUGIN_PROC
    comment = "Author Identification using Novel Techniques"
    help = "Help if a matter of trust."
    wanted_name = "BinAuthor"
    wanted_hotkey = ""

    def init(self):
        try:
            self.BinAuthorFunctionFilter = FunctionFilter.FunctionFilter()
        except:
            idaapi.msg("Failed to initialize Function Filter.\n")
            idaapi.msg("Failed to initialize BinAuthor.\n")
            del self.BinAuthorFeatureExtractor
            idaapi.msg("Errors and fun!\n")
            return idaapi.PLUGIN_SKIP
            
        try:
            self.BinAuthor_manager = BinAuthorManager()
            self.BinAuthor_manager.buildMenu(self.BinAuthorFunctionFilter)
            return idaapi.PLUGIN_KEEP
        except:
            idaapi.msg("Failed to initialize BinAuthor.\n")
            del self.BinAuthor_manager
            idaapi.msg("Errors and fun!\n")
            return idaapi.PLUGIN_SKIP
        
    def term(self):
        self.BinAuthor_manager.del_menu_items()

    def run(self, arg):
        pass


def PLUGIN_ENTRY():
    return BinAuthor_plugin_t()
