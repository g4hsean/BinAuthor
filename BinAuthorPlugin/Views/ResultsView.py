import sys
import idaapi
import idautils
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
from pprint import pprint
from idaapi import PluginForm
from subprocess import Popen

from PySide import QtGui, QtCore, QtUiTools

class Results(PluginForm):
    def __init__(self):
        super(Results, self).__init__()
        
    def OnCreate(self,form):
        self.parent = self.FormToPySideWidget(form)
        #self.wid = QtGui.QWidget()
        binaryUIPath = os.path.dirname(os.path.realpath(__file__)) + "\UI\ResultsView.ui"
        loader = QtUiTools.QUiLoader()
        file = QtCore.QFile(binaryUIPath)
        file.open(QtCore.QFile.ReadOnly)
        myWidget = loader.load(file,self.parent)
        #self.wid.setWindowTitle('Binary Indexing')
        #pushButtons = self.wid.findChildren(QtGui.QPushButton)
        
        '''for button in pushButtons:
            if "selectFolder" in button.objectName():
                button.clicked.connect(self.selectFolder)
            elif "closeForm" in button.objectName():
                button.clicked.connect(self.close)
            elif "indexAuthors" in button.objectName():
                button.clicked.connect(self.indexBinaries)'''
        file.close()
    '''    
    def selectFolder(self):
        print "Selecting Folder!"
        folder = QtGui.QFileDialog.getExistingDirectory(options=0)
        self.lineEditors = self.wid.findChildren(QtGui.QLineEdit)
        
        for textbox in self.lineEditors:
            if "FolderInput" in textbox.objectName():
                textbox.setText(folder)
                self.folderInput = textbox
        
    def results(self):
        print "Indexing Binaries!"
        indexFolder = self.folderInput.text()
        locationOfScript = os.path.dirname(os.path.realpath(__file__))[:-5] + "ExternalScripts\indexFiles.py" 
        DETACHED_PROCESS = 0x00000008
        self.radioButton = self.wid.findChildren(QtGui.QRadioButton)
        multiple = 0
        
        authorName = None
        for textbox in self.lineEditors:
            if "AuthorInput" in textbox.objectName():
                if textbox.isEnabled() == True:
                    authorName = textbox.text()
        
        
        for radio in self.radioButton:
            if "multiple" in radio.objectName():
                if radio.isChecked():
                    multiple = 1
        if authorName != None:
            Popen(["python",locationOfScript,indexFolder,str(multiple),authorName],close_fds=True, creationflags=DETACHED_PROCESS)
        else:
            Popen(["python",locationOfScript,indexFolder,str(multiple)],close_fds=True, creationflags=DETACHED_PROCESS)

    def close(self):
        self.wid.close()
        print "Closed"

'''
    def Show(self):
        """Creates the form is not created or focuses it if it was"""
        return PluginForm.Show(self,"Results View", options = PluginForm.FORM_PERSIST)
