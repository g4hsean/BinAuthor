import sys
from idautils import *
from idaapi import *
import os
from os import listdir
from os.path import isfile
import copy
import idc
import sark.qt
from idaapi import plugin_t
from pprint import pprint
from idaapi import PluginForm

from PySide import QtGui, QtCore

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