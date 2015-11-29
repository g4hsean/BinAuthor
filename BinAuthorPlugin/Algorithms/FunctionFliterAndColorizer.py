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
from idaapi import plugin_t
from pprint import pprint
from idaapi import PluginForm
import pluginConfigurations
import FunctionFeatureExtractor as FeatureExtractor
import CategorizeFunction as FunctionCategorizer

import BinAuthorPlugin.Views.FunctionFilterView as FunctionFilterList

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
        funcTypeStatsView = FunctionFilterList.FunctionFilterList()
        print len(functionsToColor)
        print collection.find({"MD5":GetInputFileMD5(),"type":"user"}).count()
        funcTypeStatsView.setDetails([userFuncStat, compilerFuncStat, otherFuncStat],{"User":userFunctions,"Compiler":compilerFunctions,"Other":otherFunctions})
        funcTypeStatsView.Show()
        refresh_idaview_anyway()
        request_refresh(IWID_FUNCS)
        
    def run(self):
        extractor = FeatureExtractor.FeatureExtractor()
        categorizer = FunctionCategorizer.FunctionCategorizer()
        self.functionNamesToEA = extractor.run()
        categorizer.run()
        self.colorFunctions()
