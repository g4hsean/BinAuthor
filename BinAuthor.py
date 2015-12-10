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
#import sark.qt
from idaapi import plugin_t
from pprint import pprint
from idaapi import PluginForm
#import numpy as np
#import matplotlib

#matplotlib.use('Qt4Agg')
#matplotlib.rcParams['backend.qt4']='PySide'

#import matplotlib.pyplot as plt
#from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
#from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
#from PySide import QtGui, QtCore
import BinAuthorPlugin.Algorithms.FunctionFliterAndColorizer as FunctionFilter
import pluginConfigurations
import BinAuthorPlugin.PluginMenuManager.BinAuthorManager as BinAuthorManager


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
            self.BinAuthor_manager = BinAuthorManager.BinAuthorManager()
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
