from idaapi import *
from idc import *
import idautils
import idc
import idaapi
from idautils import *
from pymongo import MongoClient
import numpy as N

'''
This code was translated from: http://people.revoledu.com/kardi/tutorial/Similarity/MahalanobisDistance.html
It was tested using the sample dataset on this blogsite.
'''
class Mahalanobis():
    def __init__(self):
        self.client = MongoClient('localhost', 27017)
        self.db = self.client.BinAuthor
        self.collection = self.db.Mahalanobis
        
        self.fileName = idaapi.get_root_filename()
        self.fileMD5 = idautils.GetInputFileMD5()
        self.authorName = self.fileName
        
    def mahalanobisDistance(self,A,B):
        A = N.array(A)
        B = N.array(B)
        
        AShape = A.shape
        BShape = B.shape
        
        n = AShape[0] + BShape[0]
        
        if AShape[1] != BShape[1]:
            print "Number of columns of A and B must be the same!"
            return
        else:
            xDiff = N.mean(A,axis=0)-N.mean(B,axis=0)
            cA = self.Covariance(A)
            cB = self.Covariance(B)
            pC=N.dot(AShape[0]/float(n),cA)+N.dot(BShape[0]/float(n),cB)
            return N.sqrt(N.dot(N.dot(xDiff,N.linalg.inv(pC)),xDiff))
    def Covariance(self,X):
        xShape = X.shape
        Xc = X-N.tile(N.mean(X,axis=0),(xShape[0],1))
        return N.dot(Xc.T,Xc)/xShape[0]

    #def getMD(self):
        
        
''' Example Usage:        
test = Mahalanobis()

vector1 = [[2, 2],[2, 5],[6, 5],[7, 3],[4, 7],[6, 4],[5, 3],[4, 6],[2, 5],[1, 3]]
vector2 = [[6, 5], [7, 4], [8, 7], [5, 6], [5, 4]]

print test.mahalanobisDistance(vector1,vector2)

'''
