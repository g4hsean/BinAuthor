from idautils import *
from idaapi import *
from idaapi import PluginForm
from pymongo import MongoClient
import random
from itertools import cycle, islice

import numpy as np
import matplotlib

matplotlib.use('Qt4Agg')
matplotlib.rcParams['backend.qt4']='PySide'

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
from PySide import QtGui, QtCore
import BinAuthorPlugin.Algorithms.FunctionStatistics as InstructionGroupStatistics

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
        self.FunctionName = funcName
        self.CurrentMD5 = str(GetInputFileMD5())
		
        for item in self.legendItems:
            if item["group"] not in self.legend.keys():
                self.legend[item["group"]] = item["groupCount"]
                self.groupStats[item["group"]] = {"mean":item["mean"],"variance":item["variance"]}	
                if int(item["groupCount"]) > self.maxFreq:
                    self.maxFreq = int(item["groupCount"])
                if int(item["groupCount"]) > self.minFreq:
                    self.minFreq = int(item["groupCount"])
    def createBoxPlot(self,dataDict):
	    # basic plot
        f1 = plt.figure(figsize=(1.5625,0.2))
        #f1.set_facecolor(None)
        #f1.patch.set_alpha(0.0)
        temp = f1.add_subplot(111)
        
        ## Create data
        np.random.seed(10)
        collectn_1 = dataDict.values()
        collectn_2 = np.random.normal(80, 30, 200)
        collectn_3 = np.random.normal(90, 20, 200)
        collectn_4 = np.random.normal(70, 25, 200)

        ## combine these different collections into a list    
        data_to_plot = [collectn_1, collectn_2, collectn_3, collectn_4]
        
	    # fake up some more data
        temp.boxplot(data_to_plot)
	    # multiple box plots on one figure
        canvas2 = FigureCanvas(f1)
        canvas2.setMinimumWidth(150)
        canvas2.setMinimumHeight(220)
        return canvas2
	
    def createBarChart(self):
        
        D = {u'Label0':26, u'Label1': 17, u'Label2':30}
        
        f1 = plt.figure(figsize=(1.5625,0.2))
        #f1.set_facecolor(None)
        #f1.patch.set_alpha(0.0)
        temp = f1.add_subplot(111)
        my_colors = list(islice(cycle(['b', 'r', 'g', 'y', 'k']), None, len(D)))
        temp.bar(range(len(D)), D.values(), align='center', width=0.2,color=my_colors)

        canvas2 = FigureCanvas(f1)
        canvas2.setMinimumWidth(150)
        canvas2.setMinimumHeight(220)
        return canvas2
        
    def createBarChartA(self,dataDict):
               
        f1 = plt.figure(figsize=(1.5625,1.5))
        #f1.set_facecolor(None)
        #f1.patch.set_alpha(0.0)
        temp = f1.add_subplot(111)
        
        my_colors = list(islice(cycle(['b', 'r', 'g', 'y', 'k']), None, len(dataDict)))
        
        temp.bar(range(len(dataDict)), dataDict.values(), align='center', width=0.2,color=my_colors)
        temp.set_xticks(range(len(dataDict)))
        temp.set_xticklabels(dataDict.keys())
        plt.setp(temp.get_xticklabels(), rotation=30, horizontalalignment='right')
        canvas2 = FigureCanvas(f1)
        plt.gcf().subplots_adjust(bottom=0.5)
        canvas2.setMinimumWidth(150)
        canvas2.setMinimumHeight(220)
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
        canvas.setMinimumHeight(220)
        return canvas
                
    def OnCreate(self, Form):
        self.parent = self.FormToPySideWidget(Form)
        
        self.FunctionStats = InstructionGroupStatistics.InstructionGroupStatistics(self.CurrentMD5,self.FunctionName)
        
        skewness = self.FunctionStats.getSkewness()
        kurtosis = self.FunctionStats.getKurtosis()
        
        mean = self.FunctionStats.getInstructionGroupMeans()
        variance = self.FunctionStats.getInstructionGroupVariance()
        
        max = self.FunctionStats.getMaxInstructionFromGroup()
        min = self.FunctionStats.getMinInstructionFromGroup()
        
        print mean
        print variance
        self.widget1 = QtGui.QWidget()
        self.widget1.setMinimumWidth((self.parent.frameGeometry().width()-217)/2)
        self.widget2 = QtGui.QWidget()
        self.widget2.setMinimumWidth((self.parent.frameGeometry().width()-217)/2)
        
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
        self.column2.addWidget(self.createBarChartA({u'Skewness':skewness, u'Kurtosis': kurtosis}))
        self.column2.addWidget(self.createBarChartA(variance))
        self.column2.addWidget(self.createBarChartA(max))
        
        self.widget1.setLayout(self.column2)
        
        self.column3 = QtGui.QVBoxLayout()
        self.column3.addWidget(self.createBarChartA(mean))
        self.column3.addWidget(self.createBarChartA(min))
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
        
        self.finalWindowWidget = QtGui.QWidget()
        
        scrollArea = QtGui.QScrollArea()
        scrollArea.setWidget(self.finalWindowWidget)
        scrollArea.setGeometry(QtCore.QRect(0, 0, (self.parent.frameGeometry().width()-217), self.parent.frameGeometry().height()))
        scrollArea.setWidgetResizable(True)
        self.finalWindowWidget.setLayout(self.finalWindow)
        
        self.final = QtGui.QVBoxLayout()
        self.final.addWidget(self.finalWindowWidget)
        
        self.parent.setLayout(self.final)
        #scrollArea = QtGui.QScrollArea()
        #scrollArea.setBackgroundRole(Qt.Gui.QPalette.Dark)
        #scrollArea.setWidget(self.mainWindow)
    
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
