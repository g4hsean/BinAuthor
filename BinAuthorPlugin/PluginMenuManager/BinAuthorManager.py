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
import BinAuthorPlugin.Views.BinaryIndexingView as BinaryIndexing
import BinAuthorPlugin.Views.ResultsView as Results
import BinAuthorPlugin.Algorithms.Choices.Choice1 as Choice1
import BinAuthorPlugin.Algorithms.Choices.Choice2 as Choice2
import BinAuthorPlugin.Algorithms.Choices.Choice18 as Choice18

class BinAuthorManager():
    def __init__(self):
        self._menu = sark.qt.MenuManager()
        self.addmenu_item_ctxs = []
    
    def launchBinaryIndexing(self):
        self.indexing = BinaryIndexing.BinaryIndexing()
        self.indexing.create()
        self.indexing.show()
    def showResults(self):
        self.results = Results.Results()
        self.results.Show()
        
    def message(self,s):
        print s
    
    def del_menu_items(self):
        for addmenu_item_ctx in self.addmenu_item_ctxs:
            idaapi.del_menu_item(addmenu_item_ctx)

        self._menu.clear()
        
    def buildMenu(self,functionFilter):
        self._menu = sark.qt.MenuManager()
        self._menu.add_menu("&BinAuthor")
        choice1 = Choice1.Choice1()
        choice2 = Choice2.Choice2()
        choice18 = Choice18.Choice18()
        self.addmenu_item_ctxs.append(idaapi.add_menu_item("BinAuthor/", "Detect User Functions", "", 0, self.showResults, ()))
        self.addmenu_item_ctxs.append(idaapi.add_menu_item("BinAuthor/", "Choice 18", "", 0, choice18.choice18, ()))
        self.addmenu_item_ctxs.append(idaapi.add_menu_item("BinAuthor/", "Choice 2", "", 0, choice2.choice2, ()))
        self.addmenu_item_ctxs.append(idaapi.add_menu_item("BinAuthor/", "Choice 1", "", 0, choice1.choice1, ()))
        self.addmenu_item_ctxs.append(idaapi.add_menu_item("BinAuthor/", "Author Indexing", "", 0, self.launchBinaryIndexing, ()))
        self.addmenu_item_ctxs.append(idaapi.add_menu_item("BinAuthor/", "filtration", "", 0, functionFilter.run, ()))