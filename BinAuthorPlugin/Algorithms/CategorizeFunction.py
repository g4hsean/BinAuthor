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

class FunctionCategorizer():
    def __init__(self):
        self.client = MongoClient('localhost', 27017)
        self.db = self.client.BinAuthor
        self.collection = self.db.FunctionLabels
        self.collection2 = self.db.GroupLabels

        self.instructionFeatures = {}
        self.groupFeatures = {}
        self.compilerInstructionFeatures = {}
        self.compilerGroupFeatures = {}
        self.rootFolder = pluginConfigurations.getRoot()
        self.thresholdPath = "With_Threshold\\"
        self.outputResults = {}
        self.outputResultsOnlyMatch = {}
        self.outputResultsThresholdMatch = {}

        self.outputGroupResults = {}
        self.outputGroupResultsOnlyMatch = {}
        self.outputGroupResultsOnlyThresholdMatch = {}

        self.numCompilerFunctionInstructions = {}
        self.numFileFunctionInstructions = {}

        self.numCompilerFunctionGroups = {}
        self.numFileFunctionGroups = {}

        self.executableName = "Student1-A1.exe"
        self.featuresPath = "author 1\\A1-2.exe"
        self.compilerFunctionsDetected = []
        self.otherFunctionsDetected = []
        self.userFunctionsDetected = []

        self.compilerFunctionsDetectedGroup = []
        self.otherFunctionsDetectedGroup = []
        self.userFunctionsDetectedGroup = []
        self.CurrentfileName = get_root_filename()
        self.fileMD5 = GetInputFileMD5()
        self.dateAnalyzed = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    def loadCompilerInstructionFeatures(self,path,fileName):
        newDict = 0
        numOfInstructions = 0
        for line in open(path + "\\instructions\\" + fileName,"r"):
            line = line.split(",")
            numOfInstructions += int(line[1])
            instruction = line[0]
            mean = float(line[2])
            variance = float(line[3].replace('\n',''))
            if newDict == 0:
                self.compilerInstructionFeatures[fileName] = {instruction:[mean,variance]}
                newDict = 1
            else:
                self.compilerInstructionFeatures[fileName][instruction] = [mean,variance]
        self.numCompilerFunctionInstructions[fileName] = numOfInstructions
                
    def loadcompilerGroupFeatures(self,path,fileName):
        newDict = 0
        numOfGroups = 0
        for line in open(path + "\\groups\\" + fileName,"r"):
            line = line.split(",")
            group = line[0]
            numOfGroups += int(line[1])
            mean = float(line[2])
            variance = float(line[3].replace('\n',''))
            if newDict == 0:
                self.compilerGroupFeatures[fileName] = {group:[mean,variance]}
                newDict = 1
            else:
                self.compilerGroupFeatures[fileName][group] = [mean,variance]
        self.numCompilerFunctionGroups[fileName] = numOfGroups
        
    def loadInstructionFeatures(self,function):
        newDict = 0
        numOfInstructions = 0
        col = self.db.Functions
        results = list(col.find({"MD5":self.fileMD5,"type":"instructions","function":function}))
        for line in results:
            numOfInstructions += int(line["instructionCount"])
            instruction = line["instruction"]
            mean = float(line["mean"])
            variance = float(line["variance"])
            if newDict == 0:
                self.instructionFeatures[function] = {instruction:[mean,variance]}
                newDict = 1
            else:
                self.instructionFeatures[function][instruction] = [mean,variance]
        self.numFileFunctionInstructions[function] = numOfInstructions

    def loadGroupFeatures(self,function):
        newDict = 0
        numOfGroups = 0
        col = self.db.Functions
        results = list(col.find({"MD5":self.fileMD5,"type":"groups","function":function}))
        for line in results:
            group = line["group"]
            numOfGroups += int(line["groupCount"])
            mean = float(line["mean"])
            variance = float(line["variance"])
            if newDict == 0:
                self.groupFeatures[function] = {group:[mean,variance]}
                newDict = 1
            else:
                self.groupFeatures[function][group] = [mean,variance]
        self.numFileFunctionGroups[function] = numOfGroups
    def run(self):
        col = self.db.Functions
        functions = list(col.distinct("function",{"MD5":self.fileMD5,"type":"instructions"}))

        for function in functions:
            self.loadInstructionFeatures(function)

        functions = list(col.distinct("function",{"MD5":self.fileMD5,"type":"groups"}))
        for function in functions:
            self.loadGroupFeatures(function)

        for files in listdir(self.rootFolder + "compilerFeatures\\instructions"):
            if isfile(self.rootFolder + "compilerFeatures\\instructions\\" + files):
                self.loadCompilerInstructionFeatures(self.rootFolder + "compilerFeatures", files)


        for files in listdir(self.rootFolder + "compilerFeatures\\groups"):
            if isfile(self.rootFolder + "compilerFeatures\\groups\\" + files):
                self.loadcompilerGroupFeatures(self.rootFolder + "compilerFeatures", files)

        for function in self.instructionFeatures.keys():
            thresholdMatches = {}
            for instruction in self.instructionFeatures[function].keys():
                mean = self.instructionFeatures[function][instruction][0]
                variance = self.instructionFeatures[function][instruction][1]
                if function not in self.outputResults.keys():
                    self.outputResults[function] = {}
                if function not in self.outputResultsOnlyMatch.keys():
                    self.outputResultsOnlyMatch[function] = {}
                if function not in self.outputResultsThresholdMatch.keys():
                    self.outputResultsThresholdMatch[function] = {}
                
                for compilerFunction in self.compilerInstructionFeatures.keys():
                    if instruction in self.compilerInstructionFeatures[compilerFunction].keys():
                        compilerMean = self.compilerInstructionFeatures[compilerFunction][instruction][0]
                        compilerVariance = self.compilerInstructionFeatures[compilerFunction][instruction][1]
                        distance = ((compilerMean-mean)**2/(compilerVariance**2+variance**2))
                            
                        if instruction not in self.outputResults[function].keys():
                                self.outputResults[function][instruction] = [mean,variance, {}]
                        if ((self.numCompilerFunctionInstructions[compilerFunction]/float(self.numFileFunctionInstructions[function])) >= 0.7 and (self.numCompilerFunctionInstructions[compilerFunction]/float(self.numFileFunctionInstructions[function])) <= 1.45) and ((len(self.compilerInstructionFeatures[compilerFunction])-len(self.instructionFeatures[function])) or (len(self.compilerInstructionFeatures[compilerFunction])-len(self.instructionFeatures[function]))):                                                                                                                                                                                                                       
                                self.outputResults[function][instruction][2][compilerFunction] = distance

                        if distance == 0.0:
                            if instruction not in self.outputResultsOnlyMatch[function].keys():
                                self.outputResultsOnlyMatch[function][instruction] = [mean,variance, {}]
                                self.outputResultsOnlyMatch[function][instruction][2][compilerFunction] = distance
                            else:
                                self.outputResultsOnlyMatch[function][instruction][2][compilerFunction] = distance
                        if distance <= 0.0005:
                            if instruction not in self.outputResultsThresholdMatch[function].keys():
                                self.outputResultsThresholdMatch[function][instruction] = [mean,variance, {}]
                                self.outputResultsThresholdMatch[function][instruction][2][compilerFunction] = distance
                            else:
                                self.outputResultsThresholdMatch[function][instruction][2][compilerFunction] = distance
                            if instruction not in thresholdMatches.keys():
                                thresholdMatches[instruction] = 0
                            else:
                                thresholdMatches[instruction] += 1

            percentValue = len(thresholdMatches.keys())/float(len(self.instructionFeatures[function].keys())) * 100
            
            numOfInstructionsThreshold = 15
            '''
            if len(self.instructionFeatures[function].keys()) < numOfInstructionsThreshold:
                self.otherFunctionsDetected.append(function)
            elif percentValue >= 75:
                self.compilerFunctionsDetected.append(function)
            else:
                self.userFunctionsDetected.append(function)
            '''
            if percentValue >= 75:
                self.compilerFunctionsDetected.append(function)
            elif len(self.instructionFeatures[function].keys()) < numOfInstructionsThreshold:
                self.otherFunctionsDetected.append(function)
            else:
                self.userFunctionsDetected.append(function)    
            
        bulkInsert = []
        output = 'Compiler Functions'
        for function in self.compilerFunctionsDetected:
            output += "," + str(function)
            hashFunction = hashlib.md5()
            hashFunction.update(self.fileMD5 + "," + function + ",compiler") 
            bulkInsert.append({"binaryFileName":self.CurrentfileName,"MD5":self.fileMD5,"Date Analyzed":self.dateAnalyzed,"hash":hashFunction.hexdigest(),"type":"compiler","function":str(function)})
        try:
            self.collection.insert_many(bulkInsert)
        except:
            pass

        bulkInsert = []
        output += "\nOther Functions"
        for function in self.otherFunctionsDetected:
            output += "," + str(function)
            hashFunction = hashlib.md5()
            hashFunction.update(self.fileMD5 + "," + function + ",other") 
            bulkInsert.append({"binaryFileName":self.CurrentfileName,"MD5":self.fileMD5,"Date Analyzed":self.dateAnalyzed,"hash":hashFunction.hexdigest(),"type":"other","function":str(function)})
        try:
            self.collection.insert_many(bulkInsert)
        except:
            pass
        bulkInsert = []
        output += "\nUser Functions"
        for function in self.userFunctionsDetected:
            output += "," + str(function)
            hashFunction = hashlib.md5()
            hashFunction.update(self.fileMD5 + "," + function + ",user") 
            bulkInsert.append({"binaryFileName":self.CurrentfileName,"MD5":self.fileMD5,"Date Analyzed":self.dateAnalyzed,"hash":hashFunction.hexdigest(),"type":"user","function":str(function)})
        try:
            self.collection.insert_many(bulkInsert)
        except:
            pass



        #=====================[GROUPS]===========================================================================

        for function in self.groupFeatures.keys():
            thresholdMatches = {}
            for group in self.groupFeatures[function].keys():
                mean = self.groupFeatures[function][group][0]
                variance = self.groupFeatures[function][group][1]
                if function not in self.outputGroupResults.keys():
                    self.outputGroupResults[function] = {}
                if function not in self.outputGroupResultsOnlyMatch.keys():
                    self.outputGroupResultsOnlyMatch[function] = {}
                if function not in self.outputGroupResultsOnlyThresholdMatch.keys():
                    self.outputGroupResultsOnlyThresholdMatch[function] = {}
                
                
                for compilerFunction in self.compilerGroupFeatures.keys():
                    if group in self.compilerGroupFeatures[compilerFunction].keys():
                        compilerMean = self.compilerGroupFeatures[compilerFunction][group][0]
                        compilerVariance = self.compilerGroupFeatures[compilerFunction][group][1]
                        distance = ((compilerMean-mean)**2/(compilerVariance**2+variance**2))
                        if group not in self.outputGroupResults[function].keys():
                            self.outputGroupResults[function][group] = [mean,variance, {}]
                            
                        if ((self.numCompilerFunctionGroups[compilerFunction]/self.numFileFunctionGroups[function]) >= 0.7 and (self.numCompilerFunctionGroups[compilerFunction]/self.numFileFunctionGroups[function]) <= 1.45):
                            self.outputGroupResults[function][group][2][compilerFunction] = distance
                            
                        if distance == 0.0:
                            if group not in self.outputGroupResultsOnlyMatch[function].keys():
                                self.outputGroupResultsOnlyMatch[function][group] = [mean,variance, {}]
                                self.outputGroupResultsOnlyMatch[function][group][2][compilerFunction] = distance
                            else:
                                self.outputGroupResultsOnlyMatch[function][group][2][compilerFunction] = distance
                        
                        if distance <= 0.005:
                            if group not in self.outputGroupResultsOnlyThresholdMatch[function].keys():
                                self.outputGroupResultsOnlyThresholdMatch[function][group] = [mean,variance, {}]
                                self.outputGroupResultsOnlyThresholdMatch[function][group][2][compilerFunction] = distance
                            else:
                                self.outputGroupResultsOnlyThresholdMatch[function][group][2][compilerFunction] = distance
                            if group not in thresholdMatches.keys():
                                thresholdMatches[group] = 0
                            else:
                                thresholdMatches[group] += 1
            percentValue = len(thresholdMatches.keys())/float(len(self.compilerGroupFeatures[compilerFunction].keys())) * 100

            if percentValue >= 25:
                self.compilerFunctionsDetectedGroup.append(function)
            else:
                self.userFunctionsDetectedGroup.append(function)    
     
        bulkInsert = []
        output = 'Compiler Functions'
        for function in self.compilerFunctionsDetectedGroup:
            output += "," + str(function)
            hashFunction = hashlib.md5()
            hashFunction.update(self.fileMD5 + "," + function + ",compiler") 
            bulkInsert.append({"binaryFileName":self.CurrentfileName,"MD5":self.fileMD5,"Date Analyzed":self.dateAnalyzed,"hash":hashFunction.hexdigest(),"type":"compiler","function":str(function)})
        try:
            self.collection2.insert_many(bulkInsert)
        except:
            pass
        bulkInsert = []
        output += "\nOther Functions"
        for function in self.otherFunctionsDetectedGroup:
            output += "," + str(function)
            hashFunction = hashlib.md5()
            hashFunction.update(self.fileMD5 + "," + function + ",other") 
            bulkInsert.append({"binaryFileName":self.CurrentfileName,"MD5":self.fileMD5,"Date Analyzed":self.dateAnalyzed,"hash":hashFunction.hexdigest(),"type":"other","function":str(function)})
        try:
            self.collection2.insert_many(bulkInsert)
        except:
            pass
        bulkInsert = []
        output += "\nUser Functions"
        for function in self.userFunctionsDetectedGroup:
            output += "," + str(function)
            hashFunction = hashlib.md5()
            hashFunction.update(self.fileMD5 + "," + function + ",user") 
            bulkInsert.append({"binaryFileName":self.CurrentfileName,"MD5":self.fileMD5,"Date Analyzed":self.dateAnalyzed,"hash":hashFunction.hexdigest(),"type":"user","function":str(function)})
        try:
            self.collection2.insert_many(bulkInsert)
        except:
            pass
