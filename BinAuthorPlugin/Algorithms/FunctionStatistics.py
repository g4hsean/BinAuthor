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
        self.functionGroupCount = self.collection.find({"function":functionName,"MD5":str(MD5), "group": { "$exists": "true"}},{"group": 1, "groupCount":1,"_id":0})
        self.groupCounts = []
        
        for item in self.functionGroupCount:
            self.groupCounts.append(int(item["groupCount"]))
            
    def getSkewness(self):    
        return stats.skew(self.groupCounts)

    def getKurtosis(self):
        return stats.kurtosis(self.groupCounts)

