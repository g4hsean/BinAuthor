import idautils
import idc
import idaapi
import math
from scipy import stats
from pymongo import MongoClient
import operator

class InstructionGroupStatistics(object):
    def __init__(self,MD5,functionName):
        self.client = MongoClient('localhost', 27017)
        self.db = self.client.BinAuthor
        self.collection = self.db.Functions
        self.functionGroupCount = self.collection.find({"function":functionName,"MD5":str(MD5), "group": { "$exists": "true"}},{"group": 1, "groupCount":1,"_id":0,"mean":1,"variance":1,"min_instruction_count":1,"max_instruction_count":1,"max_instruction":1,"min_instruction":1})
        self.staticGroups = ["DataTransfer","DataTransferAddressObject","DataTransferConverstion","Arithmetic","Logical","Test","ControlTransfer","Floating"]
        self.groupCounts = []
        self.groupList = []
        self.functionName = functionName
        self.MD5 = MD5
        
        self.topCorrelationResults = 5
        
        self.currentFunction = {}
        
        for item in self.functionGroupCount:
            self.currentFunction[item["group"]] = [item["groupCount"],item["mean"]]
            self.groupList.append(item)
            self.groupCounts.append(int(item["groupCount"]))
            
    def getSkewness(self):    
        return stats.skew(self.groupCounts)

    def getKurtosis(self):
        return stats.kurtosis(self.groupCounts)

    def getInstructionGroupMeans(self):
        meanDict = {}
        
        for item in self.groupList:
            if item["group"] not in meanDict.keys():
                meanDict[item["group"]] = item["mean"]
                
        return meanDict
        
    def getInstructionGroupVariance(self):
        varianceDict = {}
        
        for item in self.groupList:
            if item["group"] not in varianceDict.keys():
                varianceDict[item["group"]] = item["variance"]
                
        return varianceDict

    def getMaxInstructionFromGroup(self):
        maxDict = {}
        for item in self.groupList:
            if (item["group"] + "_" + item["max_instruction"]) not in maxDict.keys():
                maxDict[item["group"] + "_" + item["max_instruction"]] = item["max_instruction_count"]                
        return maxDict
        
    def getMinInstructionFromGroup(self):
        minDict = {}
        for item in self.groupList:
            if (item["group"] + "_" + item["min_instruction"]) not in minDict.keys():
                minDict[item["group"] + "_" + item["min_instruction"]] = item["min_instruction_count"]                
        return minDict
        
    def correlation(self):
        correlations = {}
        
        functionGroups = {}
        userFunctionNames = [item["function"] for item in self.db.FunctionLabels.find({"MD5":"07D2AB1855E0CEF2D46A198A029AFB95","type":"user","function": {"$ne":self.functionName}},{"function":1,"_id":0})]
        
        print userFunctionNames
        functions = self.collection.find({"function": {"$in":userFunctionNames},"MD5":str(self.MD5), "group": { "$exists": "true"}},{"group": 1, "function": 1, "groupCount":1,"_id":0,"mean":1,"variance":1})
        
        for function in functions:
            if function["function"] not in functionGroups.keys():
                functionGroups[function["function"]] = {function["group"] : [function["groupCount"], function["mean"]]}
            else:
                functionGroups[function["function"]][function["group"]] = [function["groupCount"], function["mean"]] 
                
        
        for function in functionGroups.keys():
            top = 0.0
            bottomA = 0.0
            bottomB = 0.0
            if (function[:15]) not in correlations.keys():
                correlations[function[:15]] = float(0.00)
            for group in self.staticGroups:
                if (group in functionGroups[function].keys()) and (group in self.currentFunction.keys()):
                    top += float((self.currentFunction[group][0] - self.currentFunction[group][1]) * (functionGroups[function][group][0] - functionGroups[function][group][1]))
                    bottomA += float((self.currentFunction[group][0] - self.currentFunction[group][1]))**2
                    bottomB += float((functionGroups[function][group][0] - functionGroups[function][group][1]))**2
                    
            if math.sqrt(bottomA*bottomB) != 0:
                correlations[function[:15]] = float((top/math.sqrt(bottomA*bottomB)))
        correlations = sorted(correlations.items(), key=operator.itemgetter(1), reverse=True)    
        return correlations[:self.topCorrelationResults]
            