from idautils import *
from idaapi import *
from idaapi import PluginForm
from pymongo import MongoClient

import numpy as np
import matplotlib

matplotlib.use('Qt4Agg')
matplotlib.rcParams['backend.qt4']='PySide'

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
from PySide import QtGui, QtCore
class StatsView(PluginForm):
    def setDetails(self,funcName):
        self.client = MongoClient('localhost', 27017)
        self.db = self.client.BinAuthor
        self.collection = self.db.Functions
        self.legendItems = self.collection.find({"function":funcName,"MD5":str(GetInputFileMD5()), "group": { "$exists": "true"}},{"group": 1, "groupCount":1,"_id":0, "mean": 1,"variance": 1})
        self.legend = {}
        self.groupStats = {}
        self.maxFreq = 0
        self.minFreq = sys.maxint
		
		
        for item in self.legendItems:
            if item["group"] not in self.legend.keys():
                self.legend[item["group"]] = item["groupCount"]
                self.groupStats[item["group"]] = {"mean":item["mean"],"variance":item["variance"]}	
                if int(item["groupCount"]) > self.maxFreq:
                    self.maxFreq = int(item["groupCount"])
                if int(item["groupCount"]) > self.minFreq:
                    self.minFreq = int(item["groupCount"])
    def createBoxPlot(self):
	    # basic plot
        f1 = plt.figure(figsize=(1.5625,0.2))
        #f1.set_facecolor(None)
        #f1.patch.set_alpha(0.0)
        temp = f1.add_subplot(111)
	
	    # fake up some more data
        
        self.groupStats
		
        spread = np.random.rand(50) * 100
        center = np.ones(25) * 40
        flier_high = [self.maxFreq] * 100 + 100
        flier_low = [self.minFreq] * -100
        d2 = np.concatenate((spread, center, flier_high, flier_low), 0)
        data.shape = (-1, 1)
        d2.shape = (-1, 1)
	    # data = concatenate( (data, d2), 1 )
	    # Making a 2-D array only works if all the columns are the
	    # same length.  If they are not, then use a list instead.
	    # This is actually more efficient because boxplot converts
	    # a 2-D array into a list of vectors internally anyway.
        data = np.concatenate((spread, center, flier_high, flier_low), 0)
        temp.boxplot(data)
	    # multiple box plots on one figure
        canvas2 = FigureCanvas(f1)
        canvas2.setMinimumWidth(150)
        canvas2.setMinimumHeight(150)
        return canvas2
	
    def createBarChart(self):
        
        D = {u'Label0':26, u'Label1': 17, u'Label2':30}
        
        f1 = plt.figure(figsize=(1.5625,0.2))
        #f1.set_facecolor(None)
        #f1.patch.set_alpha(0.0)
        temp = f1.add_subplot(111)
        
        temp.bar(range(len(D)), D.values(), align='center', width=0.2)

        canvas2 = FigureCanvas(f1)
        canvas2.setMinimumWidth(150)
        canvas2.setMinimumHeight(150)
        return canvas2
        
           
    def createPieChart(self):
        # The slices will be ordered and plotted counter-clockwise.
        labels = 'User', 'Compiler', 'Other'
        sizes = [15, 55, 30]
        colors = ['blue', '#FA8500' , '#80390A']
        explode = (0, 0.1, 0)  # only "explode" the 2nd slice (i.e. 'Hogs')

        figure = plt.figure(figsize=(1.5625,0.2))
        #figure.set_facecolor(None)
        #figure.patch.set_alpha(0.0)
        canvas = FigureCanvas(figure)
        axes = figure.add_subplot(111)
        axes.pie(sizes, explode=explode, labels=labels, colors=colors,autopct='%1.1f%%', shadow=True, startangle=90)
        
        canvas.setMinimumWidth(150)
        canvas.setMinimumHeight(150)
        return canvas
                
    def OnCreate(self, Form):
        self.parent = self.FormToPySideWidget(Form)
        
        
        self.widget1 = QtGui.QWidget()
        self.widget2 = QtGui.QWidget()
        
        self.listView = QtGui.QTableWidget(len(self.legend.keys()),2)
        self.listView.setMaximumSize(QtCore.QSize(217, 55*len(self.legend.keys())))
        
        newItem = QtGui.QTableWidgetItem("Group Name")
        self.listView.setHorizontalHeaderItem(0, newItem)
        
        newItem = QtGui.QTableWidgetItem("Title Frequency")
        self.listView.setHorizontalHeaderItem(1, newItem)
        counter = 0
        for group in self.legend.keys():
            newItem = QtGui.QTableWidgetItem(group)
            self.listView.setItem(counter, 0, newItem)
            newItem = QtGui.QTableWidgetItem(str(self.legend[group]))
            self.listView.setItem(counter, 1, newItem)
            counter += 1
        
        
        
        self.column1 = QtGui.QVBoxLayout()
        self.column1.addWidget(self.listView,QtCore.Qt.AlignRight|QtCore.Qt.AlignTop)
         
        self.column2 = QtGui.QVBoxLayout()
        self.column2.addWidget(self.createBarChart())
        self.column2.addWidget(self.createBarChart())
        self.column2.addWidget(self.createBarChart())
        
        self.widget1.setLayout(self.column2)
        
        self.column3 = QtGui.QVBoxLayout()
        self.column3.addWidget(self.createBarChart())
        self.column3.addWidget(self.createBarChart())
        self.column3.addWidget(self.createBarChart())
        
        self.button1Widget = QtGui.QWidget()
        QtGui.QPushButton("&Save Figures", self.button1Widget)
        self.button2Widget = QtGui.QWidget()
        QtGui.QPushButton("&Save Report", self.button2Widget)
        
        self.buttonsWidget = QtGui.QWidget()
        self.buttonsLayout = QtGui.QGridLayout()
        self.buttonsLayout.addWidget(self.button1Widget,0,0)
        self.buttonsLayout.addWidget(self.button2Widget,0,1)        
        self.buttonsWidget.setLayout(self.buttonsLayout)
        
        #self.column3.addWidget(self.buttonsWidget)
        self.buttonsWidget.setFixedWidth(200)
        
        self.widget2.setLayout(self.column3)
        
        self.row = QtGui.QGridLayout()
        #self.row.addLayout(self.column1,0,0)
        self.row.addWidget(self.widget1,0,1)
        self.row.addWidget(self.widget2,0,2)
        
        
        self.mainWindow = QtGui.QWidget()
        self.mainWindow.setLayout(self.row)
        #self.mainWindow.setMinimumHeight(850)
        #self.mainWindow.setMinimumWidth(700)
        self.testLayout = QtGui.QVBoxLayout()
        self.testLayout.addWidget(self.mainWindow)
        
        
        self.finalWindow = QtGui.QGridLayout()
        self.finalWindow.addWidget(self.listView,0,0,QtCore.Qt.AlignRight|QtCore.Qt.AlignTop)
        self.finalWindow.addLayout(self.testLayout,0,1,QtCore.Qt.AlignTop)
        self.finalWindow.addWidget(self.buttonsWidget,1,1,QtCore.Qt.AlignRight)
        self.parent.setLayout(self.finalWindow)
        
    
    def Show(self):
        """Creates the form is not created or focuses it if it was"""
        try:
            tform = idaapi.find_tform("IDA View-A")
            w = idaapi.PluginForm.FormToPySideWidget(tform)
            w.setFocus()
        except:
            print 'Failed to set focus.'
        return PluginForm.Show(self,
                               "Function Statistics",
                               options = PluginForm.FORM_PERSIST)
