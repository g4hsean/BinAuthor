import idautils
import idc
import idaapi
from scipy import stats
from pymongo import MongoClient

class InstructionGroupStatistics(object):
    def __init__(self,MD5,functionName):
        self.client = MongoClient('localhost', 27017)
        self.db = self.client.BinAuthor
        self.collection = self.db.Functions
        self.functionGroupCount = self.collection.find({"function":functionName,"MD5":str(MD5), "group": { "$exists": "true"}},{"group": 1, "groupCount":1,"_id":0,"mean":1,"variance":1,"min_instruction_count":1,"max_instruction_count":1,"max_instruction":1,"min_instruction":1})
        self.groupCounts = []
        self.groupList = []
        
        for item in self.functionGroupCount:
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