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

from PySide import QtGui, QtCore, QtUiTools

class BinaryIndexing():
   
    def create(self):
        self.wid = QtGui.QWidget()
        binaryUIPath = os.path.dirname(os.path.realpath(__file__)) + "\UI\BinaryIndexing.ui"
        loader = QtUiTools.QUiLoader()
        file = QtCore.QFile(binaryUIPath)
        file.open(QtCore.QFile.ReadOnly)
        myWidget = loader.load(file,self.wid)
        self.wid.setWindowTitle('Binary Indexing')
        pushButtons = self.wid.findChildren(QtGui.QPushButton)
        
        for button in pushButtons:
            buttonText = button.text()
            if "Select Folder" in buttonText:
                button.clicked.connect(self.selectFolder)
            elif "Close" in buttonText:
                button.clicked.connect(self.close)
            elif "Index Binaries" in buttonText:
                button.clicked.connect(self.indexBinaries)
        file.close()
        
    def selectFolder(self):
        print "Selecting Folder!"
        folder = QtGui.QFileDialog.getExistingDirectory()
        self.lineEditor = self.wid.findChildren(QtGui.QLineEdit)[0]
        self.lineEditor.setText(folder)
        
    def indexBinaries(self):
        print "Indexing Binaries!"
        print self.lineEditor.text()
    def close(self):
        """
        Called when the plugin form is closed
        """
        #global ImpExpForm
        #del ImpExpForm
        self.wid.close()
        print "Closed"


    def show(self):
        """Creates the form is not created or focuses it if it was"""
        self.wid.show()
