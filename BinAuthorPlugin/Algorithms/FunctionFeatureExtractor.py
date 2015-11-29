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
            
        ea = idc.BeginEA()
        count = 0
        for funcea in Functions(idc.SegStart(ea), idc.SegEnd(ea)):
            functionInstructions = copy.deepcopy(self.instructions)
            functionGroups = copy.deepcopy(self.groups)
            sum = 0
            allGroupSum = 0
            functionName = idc.GetFunctionName(funcea)
            functionNamesToEA[functionName] = funcea
            originalfuncea = funcea
            currentea = funcea
            while currentea != idc.BADADDR and currentea < idc.FindFuncEnd(funcea):
                currentInstruction = idc.GetMnem(currentea)
                if currentInstruction in self.instructions.keys():
                    functionInstructions[currentInstruction] += 1
                    sum += 1
                
                for group in self.groups.keys():
                    if currentInstruction in self.groups[group][0].keys():
                        functionGroups[group][1] += 1
                        functionGroups[group][0][currentInstruction] += 1
                        allGroupSum += 1
                        
                currentea = idc.NextHead(currentea)
            self.writeInstructionFeatures(self.instructions,sum,functionInstructions,functionName)
            self.writeInstructionGroupFeatures(self.groups,allGroupSum,functionGroups,functionName)
        return functionNamesToEA