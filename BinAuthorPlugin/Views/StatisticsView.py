from idautils import *
from idaapi import *
from idaapi import PluginForm
from pymongo import MongoClient
import random
from itertools import cycle, islice
import copy
from datetime import datetime
import idc

import numpy as np
import matplotlib

matplotlib.use('Qt4Agg')
matplotlib.rcParams['backend.qt4']='PySide'

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
from PySide import QtGui, QtCore
import BinAuthorPlugin.Algorithms.FunctionStatistics as InstructionGroupStatistics

class htmlReport():
    def generateReport(self,executableName,MD5,function,statsTable):
        dateNow = datetime.now()
        html = '''
        <style>
    
    #mainContainer {
        margin-left:15%
    }
    #statsDiv td {
        vertical-align:top
    }
	#statsDiv.table td{
		width:100%
	}
    #statsDiv table{
		width:85%
	}
</style>
<html>
    <div align="center"><h1>BinAuthor: Function Analysis Report</h1></div>
    <div id="mainContainer">
    <div >
        <table border="1">
            <tr>
                <td><b>Executable Name:</b></td><td>''' + executableName + '''</td>
            </tr>
            <tr>
                <td><b>Executable Hash:</b></td><td>''' + MD5 + '''</td>
            </tr>
            <tr>
                <td><b>Function:</b></td><td>''' + function + '''</td>
            </tr>
            <tr>
                <td><b>Report Generation Date:</b></td><td>''' + dateNow.strftime('%Y/%m/%d %I:%M:%S %p') +  '''</td>
            </tr>
        </table>
    </div><br>
    <div id="statsDiv">
    ''' + statsTable + '''
    </div><br>
    <div>
        <table border="">
            <tr>
                <td><img src="KurtosisSkewness.png" alt="Function Kurtosis And Skewness" height="250" width="600" /></td><td><img src="GroupMean.png" alt="Group Mean" height="250" width="600" /></td>
            </tr>
            <tr>
                <td><img src="GroupVariance.png" alt="Smiley face" height="250" width="600" /></td><td><img src="MinimumFrequencies.png" alt="Instructions With Minimum Frequencies" height="250" width="600" /></td>
            </tr>
            <tr>
                <td><img src="MaximumFrequencies.png" alt="Instructions With Maximum Frequencies" height="250" width="600" /></td><td><img src="FunctionCorrelations.png" alt="Top 5 Function Correlations" height="250" width="600" /></td>
            </tr>
        </table>
    </div>
    </div>
</html>
'''
        return html

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
        
        self.statsFigures = {"KurtosisSkewness": None,"GroupMean": None, "GroupVariance": None,"MinimumFrequencies": None,"MaximumFrequencies":None,"FunctionCorrelations":None}
		
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
        canvas2.setMinimumHeight(150)
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
        canvas2.setMinimumHeight(150)
        return canvas2
    
    def createBarChartCorrelation(self,dataTupple):
        f1 = plt.figure(figsize=(1.5625,1.5))
        #f1.set_facecolor(None)
        #f1.patch.set_alpha(0.0)
        temp = f1.add_subplot(111)
        
        x_axis_Titles = [function[0] for function in dataTupple]
        dataPoints = [function[1] for function in dataTupple]
        
        my_colors = list(islice(cycle(['b', 'r', 'g', 'y', 'k']), None, len(dataTupple)))
        
        temp.bar(range(len(dataTupple)), dataPoints, align='center', width=0.2,color=my_colors)
        temp.set_xticks(range(len(dataTupple)))
        temp.set_xticklabels(x_axis_Titles)
        plt.setp(temp.get_xticklabels(), rotation=20, horizontalalignment='right')
        canvas2 = FigureCanvas(f1)
        plt.gcf().subplots_adjust(bottom=0.5)
        plt.gca().set_ylim([min(dataPoints)-0.2,1])
        plt.title("Function Correlation")
        canvas2.setMinimumWidth(150)
        canvas2.setMinimumHeight(150)
        self.statsFigures["FunctionCorrelations"] = f1
        return canvas2
        
    def createBarChartA(self,dataDict,title,type):
               
        f1 = plt.figure(figsize=(1.5625,1.5))
        #f1.set_facecolor(None)
        #f1.patch.set_alpha(0.0)
        temp = f1.add_subplot(111)
        
        my_colors = list(islice(cycle(['b', 'r', 'g', 'y', 'k']), None, len(dataDict)))
        
        temp.bar(range(len(dataDict)), dataDict.values(), align='center', width=0.2,color=my_colors)
        temp.set_xticks(range(len(dataDict)))
        temp.set_xticklabels(dataDict.keys())
        plt.setp(temp.get_xticklabels(), rotation=20, horizontalalignment='right')
        canvas2 = FigureCanvas(f1)
        plt.gcf().subplots_adjust(bottom=0.5)
        plt.title(title)
        canvas2.setMinimumWidth(150)
        canvas2.setMinimumHeight(150)
        
        self.statsFigures[type] = f1
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

    def saveReport(self):
        fileName = str(idaapi.get_root_filename() + "_" + self.FunctionName[:15] + ".html")
        dir = idc.AskFile(1,fileName,"Save as")
        dir = dir[:-len(fileName)]
        
        if not os.path.exists(dir + str(idaapi.get_root_filename() + "_" + self.FunctionName[:15])):
            os.makedirs(dir + str(idaapi.get_root_filename() + "_" + self.FunctionName[:15]))
        dir = dir + str(idaapi.get_root_filename() + "_" + self.FunctionName[:15]) + "\\"
        report = htmlReport()

        fileOutput = open(dir+fileName,"wb")
        fileOutput.write(report.generateReport(idaapi.get_root_filename(),self.CurrentMD5,self.FunctionName,self.generateStatisticsTable()))
        fileOutput.close()
        
        for graph in self.statsFigures.keys():
            self.statsFigures[graph].set_figheight(2.500)
            self.statsFigures[graph].set_figwidth(6.000)
            self.statsFigures[graph].set_dpi(10)
            self.statsFigures[graph].savefig(dir + graph + ".png")

    def saveFigures(self):
        dir = idc.AskFile(1,"Skewness.png","Save as")
        dir = dir[:-len("Skewness.png")]
        
        if not os.path.exists(dir + str(idaapi.get_root_filename() + "_" + self.FunctionName[:15])):
            os.makedirs(dir + str(idaapi.get_root_filename() + "_" + self.FunctionName[:15]))
        dir = dir + str(idaapi.get_root_filename() + "_" + self.FunctionName[:15]) + "\\"
        
        for graph in self.statsFigures.keys():
            self.statsFigures[graph].set_figheight(2.500)
            self.statsFigures[graph].set_figwidth(6.000)
            self.statsFigures[graph].set_dpi(10)
            self.statsFigures[graph].savefig(dir + graph + ".png")  
            
    
    def generateStatisticsTable(self):
        output = ''
        outputSequence = ["Mean","Variance","Min","Max","Skewness","Kurtosis","Correlation"]
        for statsType in outputSequence:
            if statsType == "Skewness":
                output += '<tr><td><b>Skewness:</b></td><td>' + str(self.statistics[statsType]) + '</td></tr>'
            elif statsType == "Kurtosis":
                output += '<tr><td><b>Kurtosis:</b></td><td>' + str(self.statistics[statsType]) + '</td></tr></table></td><td>'
            elif statsType == "Mean":
                output += '<table><tr><td><h3>Group Mean:</h3><table border="">'
                for group in self.statistics[statsType].keys():
                    output += '<tr><td><b>' + group + ':</b></td><td>' + str(self.statistics[statsType][group]) + '</td></tr>'
                output += '</table></td><td>'
            elif statsType == "Variance":
                output += '<h3>Group Variance:</h3><table border="">'
                for group in self.statistics[statsType].keys():
                    output += '<tr><td><b>' + group + ':</b></td><td>' + str(self.statistics[statsType][group]) + '</td></tr>'
                output += '</table></td><td>'
            elif statsType == "Min":
                output += '<h3>Group Instruction Minimums:</h3><table border="">'
                for group in self.statistics[statsType].keys():
                    output += '<tr><td><b>' + group + ':</b></td><td>' + str(self.statistics[statsType][group]) + '</td></tr>'
                output += '</table></td></tr>'
            elif statsType == "Max":
                output += '<tr><td><h3>Group Instruction Maximums:</h3><table border="">'
                for group in self.statistics[statsType].keys():
                    output += '<tr><td><b>' + group + ':</b></td><td>' + str(self.statistics[statsType][group]) + '</td></tr>'
                output += '</table></td><td><h3>Skewness & Kurtosis:</h3><table border="">'
            elif statsType == "Correlation":
                output += '<h3>Correlated Functions:</h3><table border="">'
                for function in self.statistics[statsType]:
                    output += '<tr><td><b>' + function[0] + ':</b></td><td>' + str(function[1]) + '</td></tr>'
                output += '</table></td></tr></table>'
        return output
    def storeFunctionStatistics(self):
        outputSequence = ["Mean","Variance","Min","Max","Skewness","Kurtosis","Correlation"]
        outputDict = {"ExecutableName":idaapi.get_root_filename(),"ExecutableMD5Hash":self.CurrentMD5,"FunctionName":self.FunctionName}
        for statsType in outputSequence:
            if statsType == "Skewness":
                outputDict["Skewness"] = self.statistics[statsType]
            elif statsType == "Kurtosis":
                outputDict["Kurtosis"] = self.statistics[statsType]
            elif statsType == "Mean":
                groupMeans = {}
                for group in self.statistics[statsType].keys():
                    groupMeans[group] = self.statistics[statsType][group]
                outputDict[statsType] = groupMeans
            elif statsType == "Variance":
                groupVariance = {}
                for group in self.statistics[statsType].keys():
                    groupVariance[group] = self.statistics[statsType][group]
                outputDict[statsType] = groupVariance
            elif statsType == "Min":
                groupMin = {}
                for group in self.statistics[statsType].keys():
                    groupMin[group] = self.statistics[statsType][group]
                outputDict[statsType] = groupMin
            elif statsType == "Max":
                groupMax = {}
                for group in self.statistics[statsType].keys():
                    groupMax[group] = self.statistics[statsType][group]
                outputDict[statsType] = groupMax
            elif statsType == "Correlation":
                correlated = {}
                for function in self.statistics[statsType]:
                    correlated[function[0]] = function[1]
                outputDict[statsType] = correlated
        collection = self.db.FunctionFingerPrint
        collection.insert(outputDict)
        print "Function Fingerprint has been successfully saved to the database!"
            
    def OnCreate(self, Form):
        self.parent = self.FormToPySideWidget(Form)
        
        self.FunctionStats = InstructionGroupStatistics.InstructionGroupStatistics(self.CurrentMD5,self.FunctionName)
        
        skewness = self.FunctionStats.getSkewness()
        kurtosis = self.FunctionStats.getKurtosis()
        
        mean = self.FunctionStats.getInstructionGroupMeans()
        variance = self.FunctionStats.getInstructionGroupVariance()
        
        max = self.FunctionStats.getMaxInstructionFromGroup()
        min = self.FunctionStats.getMinInstructionFromGroup()
        
        correlation = self.FunctionStats.correlation()
        
        self.statistics = {"Skewness": skewness,"Kurtosis":kurtosis,"Mean":mean,"Variance":variance,"Max":max,"Min":min,"Correlation":correlation}
        
        ######
        
        self.leftPanel = QtGui.QWidget() #Left panel
        self.leftPanel.setMinimumWidth(300)
        
        self.listView = QtGui.QTableWidget(len(self.legend.keys()),2)
        
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
        
        self.leftPanelLayout = QtGui.QVBoxLayout() 
        self.leftPanelLayout.addWidget(self.listView,QtCore.Qt.AlignRight|QtCore.Qt.AlignTop)
        self.leftPanel.setLayout(self.leftPanelLayout)
        self.leftPanelLayout.setAlignment(self.listView,QtCore.Qt.AlignRight|QtCore.Qt.AlignTop)
        #self.leftPanel.setMinimumHeight(self.parent.frameGeometry().height())
        
        
        vwidth = self.listView.verticalHeader().width()
        hwidth = self.listView.horizontalHeader().length()
        swidth = self.listView.style().pixelMetric(QtGui.QStyle.PM_ScrollBarExtent)
        fwidth = self.listView.frameWidth() * 2
        
        vheight = self.listView.verticalHeader().length()
        hheight = self.listView.horizontalHeader().length()
        self.listView.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.listView.setMinimumSize(QtCore.QSize(vwidth + hwidth + fwidth,vheight +25))
        self.listView.setMaximumSize(QtCore.QSize(vwidth + hwidth + fwidth, vheight+25))
        #self.listView.setMinimumSize(QtCore.QSize(vwidth + hwidth + swidth + fwidth, 33.225*len(self.legend.keys())))
        #self.listView.setMaximumSize(QtCore.QSize(vwidth + hwidth + swidth + fwidth, 33.225*len(self.legend.keys())))
        
        
        
        self.middlePanel = QtGui.QWidget() #Middle panel
        self.middlePanel.setMinimumWidth((self.parent.frameGeometry().width()-400)/2)
        
        self.middlePanelLayout = QtGui.QVBoxLayout()
        self.middlePanelLayout.addWidget(self.createBarChartA({u'Skewness':skewness, u'Kurtosis': kurtosis},"Function Skewness & Kurtosis","KurtosisSkewness"))
        self.middlePanelLayout.addWidget(self.createBarChartA(variance,"Group Variance","GroupVariance"))
        self.middlePanelLayout.addWidget(self.createBarChartA(max,"Instruction With Maximum Frequencies","MaximumFrequencies"))
        
        self.middlePanel.setLayout(self.middlePanelLayout)
        
        self.rightPanel = QtGui.QWidget() #Right panel
        self.rightPanel.setMinimumWidth((self.parent.frameGeometry().width()-400)/2)
        
        self.rightPanelLayout = QtGui.QVBoxLayout()
        self.rightPanelLayout.addWidget(self.createBarChartA(mean,"Group Mean","GroupMean"))
        self.rightPanelLayout.addWidget(self.createBarChartA(min,"Instruction With Minimum Frequencies","MinimumFrequencies"))
        self.rightPanelLayout.addWidget(self.createBarChartCorrelation(correlation))
        
        
        #### for figures stupid fix but it works for now!
        self.createBarChartA({u'Skewness':skewness, u'Kurtosis': kurtosis},"Function Skewness & Kurtosis","KurtosisSkewness")
        self.createBarChartA(variance,"Group Variance","GroupVariance")
        self.createBarChartA(max,"Instruction With Maximum Frequencies","MaximumFrequencies")
        self.createBarChartA(mean,"Group Mean","GroupMean")
        self.createBarChartA(min,"Instruction With Minimum Frequencies","MinimumFrequencies")
        self.createBarChartCorrelation(correlation)
        ####
        
        
        self.rightPanel.setLayout(self.rightPanelLayout)
        
        #self.containerPanel = QtGui.QWidget() #Widget that contains all pannels
        self.containerPanelLayout = QtGui.QHBoxLayout()
        
        self.containerPanelLayout.addWidget(self.leftPanel,QtCore.Qt.AlignTop)
        self.containerPanelLayout.addWidget(self.middlePanel)
        self.containerPanelLayout.addWidget(self.rightPanel)
        
        self.centerMainPanel = QtGui.QWidget() #Center of main panel
        self.centerMainPanel.setLayout(self.containerPanelLayout)
        
        self.label = QtGui.QLabel(self.parent) #Label
        self.label.setGeometry(QtCore.QRect(self.parent.frameGeometry().width()/2, 0, 271, 51))
        font = QtGui.QFont()
        font.setPointSize(25)
        self.label.setFont(font)
        self.label.setText(self.FunctionName[:15])
        
        
        self.buttonsWidget = QtGui.QWidget() #Buttons
        self.buttonsLayout = QtGui.QGridLayout()
        
        figuresButton = QtGui.QPushButton("&Save Figures")
        figuresButton.clicked.connect(self.saveFigures)
        self.buttonsLayout.addWidget(figuresButton,0,0) 
        
        reportButton = QtGui.QPushButton("&Save Report")
        reportButton.clicked.connect(self.saveReport)
        self.buttonsLayout.addWidget(reportButton,0,1)
        
        fingerprintButton = QtGui.QPushButton("&Save Fingerprint")
        fingerprintButton.clicked.connect(self.storeFunctionStatistics)
        self.buttonsLayout.addWidget(fingerprintButton,0,2)
        self.buttonsWidget.setLayout(self.buttonsLayout)
        
        #self.column3.addWidget(self.buttonsWidget)
        self.buttonsWidget.setGeometry(QtCore.QRect(self.parent.frameGeometry().width()/2, 0, 300, 51))
        
        self.FinalPanelLayout = QtGui.QVBoxLayout()
        self.FinalPanelLayout.addWidget(self.label)
        self.FinalPanelLayout.addWidget(self.centerMainPanel)
        self.FinalPanelLayout.addWidget(self.buttonsWidget)
        
        self.FinalPanelLayout.setAlignment(self.label,QtCore.Qt.AlignCenter)
        self.FinalPanelLayout.setAlignment(self.buttonsWidget,QtCore.Qt.AlignTop|QtCore.Qt.AlignRight)        
        
        self.parent.setLayout(self.FinalPanelLayout)
        self.parent.repaint()
        #####
        
        
        
        '''
        print correlation
        self.widget1 = QtGui.QWidget()
        self.widget1.setMinimumWidth((self.parent.frameGeometry().width()-300)/2)
        self.widget2 = QtGui.QWidget()
        self.widget2.setMinimumWidth((self.parent.frameGeometry().width()-300)/2)
        
        self.listView = QtGui.QTableWidget(len(self.legend.keys()),2)
        self.listView.setMaximumSize(QtCore.QSize(300, 70*len(self.legend.keys())))
        
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
        self.column2.addWidget(self.createBarChartA({u'Skewness':skewness, u'Kurtosis': kurtosis},"Function Skewness & Kurtosis"))
        self.column2.addWidget(self.createBarChartA(variance,"Group Variance"))
        self.column2.addWidget(self.createBarChartA(max,"Instruction With Maximum Frequencies"))
        
        self.widget1.setLayout(self.column2)
        
        self.column3 = QtGui.QVBoxLayout()
        self.column3.addWidget(self.createBarChartA(mean,"Group Mean"))
        self.column3.addWidget(self.createBarChartA(min,"Instruction With Minimum Frequencies"))
        self.column3.addWidget(self.createBarChartCorrelation(correlation))
        
        self.button1Widget = QtGui.QWidget()
        QtGui.QPushButton("&Save Figures", self.button1Widget)
        self.button2Widget = QtGui.QWidget()
        QtGui.QPushButton("&Save Report", self.button2Widget)
        self.button3Widget = QtGui.QWidget()
        QtGui.QPushButton("&Save Fingerprint", self.button3Widget)
        
        #self.dummyWidget = QtGui.QWidget()
        #self.dummyWidget.setMinimumWidth(10)
        
        self.buttonsWidget = QtGui.QWidget()
        self.buttonsLayout = QtGui.QGridLayout()
        self.buttonsLayout.addWidget(self.button1Widget,0,0)
        self.buttonsLayout.addWidget(self.button2Widget,0,1)
        self.buttonsLayout.addWidget(self.button3Widget,0,2)
        #self.buttonsLayout.addWidget(self.dummyWidget,0,3)
        self.buttonsLayout.setContentsMargins(0,0,5,0)
        self.buttonsWidget.setLayout(self.buttonsLayout)
        
        #self.column3.addWidget(self.buttonsWidget)
        self.buttonsWidget.setFixedWidth(300)
        
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
        
        self.label = QtGui.QLabel(self.parent)
        self.label.setGeometry(QtCore.QRect(self.parent.frameGeometry().width()/2, 0, 271, 51))
        font = QtGui.QFont()
        font.setPointSize(25)
        self.label.setFont(font)
        self.label.setText(self.FunctionName[:15])
        
        self.finalWindowWidget = QtGui.QWidget()
        
        scrollArea = QtGui.QScrollArea()
        scrollArea.setWidget(self.finalWindowWidget)
        scrollArea.setGeometry(QtCore.QRect(0, 0, (self.parent.frameGeometry().width()-217), self.parent.frameGeometry().height()))
        scrollArea.setWidgetResizable(True)
        self.finalWindowWidget.setLayout(self.finalWindow)
        
        self.final = QtGui.QVBoxLayout()
        self.final.addWidget(self.label)
        self.final.addWidget(self.finalWindowWidget)
        
        self.parent.setLayout(self.final)'''
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
