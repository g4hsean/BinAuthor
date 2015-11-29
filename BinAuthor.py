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
import BinAuthorPlugin.Views.StatisticsView as StatsView
import BinAuthorPlugin.Algorithms.CategorizeFunction as FunctionCategorizer
import pluginConfigurations

class FeatureExtractor():
    def __init__(self):
        self.client = MongoClient('localhost', 27017)
        self.db = self.client.BinAuthor
        self.collection = self.db.Functions

        self.instructionList = pluginConfigurations.getInstructionListPath() + "InstructionList.txt"
        self.groupList = pluginConfigurations.getGroupPath() + "InstructionGroups.txt"

        self.instructions = {}
        self.groups = {}

        self.fileName = get_root_filename()
        self.fileMD5 = GetInputFileMD5()
        self.fileMD5
        self.dateAnalyzed = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    #load instructions into dictionary
    def loadInstructionList(self):
        for line in open(self.instructionList, "r"):
            self.instructions[line.replace(" ","").replace("\n","")] = 0

    def loadInstructionGroups(self):
        currentGroup = ''
        for line in open(self.groupList, "r"):
            if line.find("[") != -1:
               currentGroup = line.replace("[",'').replace("]",'').replace('\n','')
               self.groups[currentGroup] = [{},0]
            else:
               self.groups[currentGroup][0][line.replace('\n','')] = 0

    def writeInstructionFeatures(self,instructions,sum,functionInstructions,file):
        oldFileName = file
        bulkInsert = []
        for instruction in instructions.keys():
            mean = (functionInstructions[instruction]/float(sum))
            variance = ((functionInstructions[instruction] - mean)**2/sum)
            if functionInstructions[instruction] > 0:
                hashFunction = hashlib.md5()
                hashFunction.update(self.fileMD5 + "," + file + "," + "instructions," + instruction + "," + str(functionInstructions[instruction]) + "," + str(mean) + "," + str(variance))
                bulkInsert.append({"binaryFileName":self.fileName,"MD5":self.fileMD5,"Date Analyzed":self.dateAnalyzed,"function":oldFileName,"type":"instructions","hash":hashFunction.hexdigest(),"instruction": instruction,"instructionCount": functionInstructions[instruction], "mean": mean, "variance": variance})
        try:
            self.collection.insert_many(bulkInsert)
        except:
            pass

    def writeInstructionGroupFeatures(self,groups,allGroupSum,functionGroups,file):
        oldFileName = file
        bulkInsert = []
        for group in groups.keys():
            mean = (functionGroups[group][1]/float(allGroupSum))
            variance = ((functionGroups[group][1] - mean)**2/allGroupSum)
            if functionGroups[group][1] > 0:
                hashFunction = hashlib.md5()
                hashFunction.update(self.fileMD5 + "," + file + "," + "groups," + group + "," + str(functionGroups[group][1]) + "," + str(mean) + "," + str(variance))
                bulkInsert.append({"binaryFileName":self.fileName,"MD5":self.fileMD5,"Date Analyzed":self.dateAnalyzed,"function":oldFileName,"type":"groups","hash":hashFunction.hexdigest(),"group":group,"groupCount":functionGroups[group][1],"mean":mean,"variance":variance})
        try:
            self.collection.insert_many(bulkInsert)
        except:
            pass

    def run(self):
        self.loadInstructionList()
        self.loadInstructionGroups()
        functionNamesToEA = {}
            
        ea = BeginEA()
        count = 0
        for funcea in Functions(SegStart(ea), SegEnd(ea)):
            functionInstructions = copy.deepcopy(self.instructions)
            functionGroups = copy.deepcopy(self.groups)
            sum = 0
            allGroupSum = 0
            functionName = GetFunctionName(funcea)
            functionNamesToEA[functionName] = funcea
            originalfuncea = funcea
            currentea = funcea
            while currentea != BADADDR and currentea < FindFuncEnd(funcea):
                currentInstruction = GetMnem(currentea)
                if currentInstruction in self.instructions.keys():
                    functionInstructions[currentInstruction] += 1
                    sum += 1
                
                for group in self.groups.keys():
                    if currentInstruction in self.groups[group][0].keys():
                        functionGroups[group][1] += 1
                        functionGroups[group][0][currentInstruction] += 1
                        allGroupSum += 1
                        
                currentea = NextHead(currentea)
            self.writeInstructionFeatures(self.instructions,sum,functionInstructions,functionName)
            self.writeInstructionGroupFeatures(self.groups,allGroupSum,functionGroups,functionName)
        return functionNamesToEA
    
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
class FunctionFilter():
    def init(self):
        pass
    
    def colorFunctions(self):
        client = MongoClient('localhost', 27017)
        db = client.BinAuthor
        collection = db.FunctionLabels
        functionsToColor = list(collection.find({"MD5":GetInputFileMD5()}))
        
        userFunctions = [userfunc["function"] for userfunc in list(collection.find({"MD5":GetInputFileMD5(),"type":"user"}))]
        compilerFunctions = [compilerfunc["function"] for compilerfunc in list(collection.find({"MD5":GetInputFileMD5(),"type":"compiler"}))]
        otherFunctions = [otherfunc["function"] for otherfunc in list(collection.find({"MD5":GetInputFileMD5(),"type":"other"}))]
        
        userFuncStat = (len(userFunctions)/float(len(functionsToColor)))*100
        compilerFuncStat = (len(compilerFunctions)/float(len(functionsToColor)))*100
        otherFuncStat = (len(otherFunctions)/float(len(functionsToColor)))*100
        
        
        #v = idaapi.simplecustviewer_t()
        #v.Create("Function Classification")
        #v.Show()
        sumCounter = 0
        for function in functionsToColor:
            funcEA = self.functionNamesToEA[function["function"]]
            func = get_func(funcEA)
            flags = idc.GetFunctionFlags(funcEA)
            typeCounter = 0
            if ((flags&FUNC_LIB) != FUNC_LIB) and ((flags&1152) != 1152):
                if function["type"] == "compiler":
                    func.color = 0xACC7FF
                if function["type"] == "other":
                    func.color = 0xCC6600
                if function["type"] == "user":
                    func.color = 0x80FFCC
        funcTypeStatsView = ImpExpForm_t()
        print len(functionsToColor)
        print collection.find({"MD5":GetInputFileMD5(),"type":"user"}).count()
        funcTypeStatsView.setDetails([userFuncStat, compilerFuncStat, otherFuncStat],{"User":userFunctions,"Compiler":compilerFunctions,"Other":otherFunctions})
        funcTypeStatsView.Show()
        refresh_idaview_anyway()
        request_refresh(IWID_FUNCS)
        
    def run(self):
        extractor = FeatureExtractor()
        categorizer = FunctionCategorizer.FunctionCategorizer()
        self.functionNamesToEA = extractor.run()
        categorizer.run()
        self.colorFunctions()

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


class ImpExpForm_t(PluginForm):
	
    def imports_names_cb(self, ea, name, ord):
        self.items.append((ea, '' if not name else name, ord))
        # True -> Continue enumeration
        return True
    
    def setDetails(self,pieStats,funcTypeDict):
        self.pieStats = pieStats
        self.funcTypeDict = funcTypeDict
   
    def OnCreate(self, form):
        """
        Called when the plugin form is created
        """
        self.statisticsView = None
        # Get parent widget
        self.parent = self.FormToPySideWidget(form)

        w = QtGui.QWidget()
        #w.resize(200, 200)
        #w.move(100, 300)
        #w.setWindowTitle('Simple')

        # The slices will be ordered and plotted counter-clockwise.
        labels = 'User', 'Compiler', 'Other'
        sizes = self.pieStats#[15, 55, 30]
        colors = ['#80FFCC', '#ACC7FF' , '#CC6600']
        explode = (0, 0.1, 0)  # only "explode" the 2nd slice (i.e. 'Hogs')

        plt.pie(sizes, explode=explode, labels=labels, colors=colors,
                autopct='%1.1f%%', shadow=True, startangle=90)
        # Set aspect ratio to be equal so that pie is drawn as a circle.
        plt.axis('equal')
        figure = plt.figure(figsize=(10,0.2))
        figure.set_facecolor(None)
        figure.patch.set_alpha(0.0)
        canvas = FigureCanvas(figure)
        axes = figure.add_subplot(111)
        axes.pie(sizes, explode=explode, labels=labels, colors=colors,
                autopct='%1.1f%%', shadow=True, startangle=90)
    
        self.results_tree = QtGui.QTreeWidget()
        self.results_tree.setSortingEnabled(False)
        self.results_tree.headerItem().setText(0, 'Function Type')
        self.results_tree.headerItem().setText(1, 'Function Name')
        
        #exampleFunctionTypes = {"User":["__ArrayUnwind(void *,uint,int,void (*)(void *))","std::char_traits<char>::compare(char const *,char const *,uint)","solve(int)","_main","std::_Tree_val<std::_Tset_traits<std::basic_string<char,std::char_traits<char>,std::allocator<char>>,std::less<std::basic_string<char,std::char_traits<char>,std::allocator<char>>>,std::allocator<std::basic_string<char,std::char_traits<char>,std::allocator<char>>>,0>>::~_Tree_val<std::_Tset_traits<std::basic_string<char,std::char_traits<char>,std::allocator<char>>,std::less<std::basic_string<char,std::char_traits<char>,std::allocator<char>>>,std::allocator<std::basic_string<char,std::char_traits<char>,std::allocator<char>>>,0>>(void)","std::basic_string<char,std::char_traits<char>,std::allocator<char>>::insert(uint,uint,char)","?erase@?$_Tree@V?$_Tset_traits@V?$basic_string@DU?$char_traits@D@std@@V?$allocator@D@2@@std@@U?$less@V?$basic_string@DU?$char_traits@D@std@@V?$allocator@D@2@@std@@@2@V?$allocator@V?$basic_string@DU?$char_traits@D@std@@V?$allocator@D@2@@std@@@2@$0A@@std@@@std@@QAE?AV?$_Tree_const_iterator@V?$_Tree_val@V?$_Tset_traits@V?$basic_string@DU?$char_traits@D@std@@V?$allocator@D@2@@std@@U?$less@V?$basic_string@DU?$char_traits@D@std@@V?$allocator@D@2@@std@@@2@V?$allocator@V?$basic_string@DU?$char_traits@D@std@@V?$al_"],"Compiler":["std::bad_alloc::`vector deleting destructor'(uint)","std::set<std::basic_string<char,std::char_traits<char>,std::allocator<char>>,std::less<std::basic_string<char,std::char_traits<char>,std::allocator<char>>>,std::allocator<std::basic_string<char,std::char_traits<char>,std::allocator<char>>>>::~set<std::basic_string<char,std::char_traits<char>,std::allocator<char>>,std::less<std::basic_string<char,std::char_traits<char>,std::allocator<char>>>,std::allocator<std::basic_string<char,std::char_traits<char>,std::allocator<char>>>>(void)","std::basic_string<char,std::char_traits<char>,std::allocator<char>>::~basic_string<char,std::char_traits<char>,std::allocator<char>>(void)","std::basic_string<char,std::char_traits<char>,std::allocator<char>>::assign(char const *,uint)"],"Other":["??1bad_alloc@std@@UAE@XZ","operator delete(void *,void *)","__security_check_cookie(x)","std::exception::what(void)","std::exception::exception(std::exception const &)","operator delete(void *)"]}
        counter = 0
        for funcType in self.funcTypeDict.keys():
            funcTypeTree = QtGui.QTreeWidgetItem(self.results_tree)
            funcTypeTree.setText(0, funcType)
            funcTreeCounter = 0
            for funcName in self.funcTypeDict[funcType]:
                funcItem = QtGui.QTreeWidgetItem(funcTypeTree)
                funcItem.setText(0,funcType)
                funcItem.setText(1,funcName)
                funcTreeCounter += 1
            counter +=1
            self.results_tree.addTopLevelItem(funcTypeTree)
        canvas.resize(20,20)
        layout = QtGui.QVBoxLayout()
        layout.addWidget(canvas)
        w.setLayout(layout)
        w.setFixedWidth(500)
        w.setFixedHeight(500)
        
        self.results_tree.itemClicked.connect(self.item_click)
        layoutMain = QtGui.QGridLayout()
        layoutMain.addWidget(w,0,0)
        layoutMain.addWidget(self.results_tree,0,1)
        canvas.draw()
        # Populate PluginForm
        self.parent.setLayout(layoutMain)
    def item_click(self,item):
        print str(item.text(1))
        self.statisticsView = StatsView.StatsView()
        self.statisticsView.setDetails(item.text(1))
        self.statisticsView.Show()

    def OnClose(self, form):
        """
        Called when the plugin form is closed
        """
        #global ImpExpForm
        #del ImpExpForm
        print "Closed"


    def Show(self):
        """Creates the form is not created or focuses it if it was"""
        return PluginForm.Show(self,
                               "Function Classes",
                               options = PluginForm.FORM_PERSIST)

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
            self.BinAuthorFunctionFilter = FunctionFilter()
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
