import idautils
import idc
import idaapi
import math
from scipy import stats
from pymongo import MongoClient
import operator
import BinAuthorPlugin.Algorithms.Choices.Choice1 as Choice1
import BinAuthorPlugin.Algorithms.Choices.Choice2 as Choice2
import BinAuthorPlugin.Algorithms.Choices.Choice18 as Choice18
class AuthorClassification():
        
    def __init__(self):
        self.client = MongoClient('localhost', 27017)
        self.db = self.client.BinAuthor
        self.collection = self.db.Functions
        self.choice1 = self.db.Choice1
        self.choice2 = self.db.Choice2
        self.choice1Results = {}
    
    def getChoice1(self):
        choice1 = Choice1.Choice1()
        choice1 = choice1.getChoice1()
        features = choice1["features"]
        documents = self.choice1.find({"$or":[{"features.0":features[0]},{"features.1":features[1]},{"features.2":features[2]},{"features.3":features[3]},{"features.4":features[4]},{"features.5":features[5]},{"features.6":features[6]},{"features.7":features[7]},{"features.8":features[8]},{"features.9":features[9]},{"features.10":features[10]}]})

        for doc in documents:
            jaccardCoefficient = len(list(set(doc["features"])& set(features)))/float(len(list(set(doc["features"])| set(features))))
            self.choice1Results[doc['Author Name']] = jaccardCoefficient
        print self.choice1Results
    def getChoice2(self):
        choice2 = Choice2.Choice2()
        choice2 = choice2.getChoice2()
        return 0