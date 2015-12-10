from subprocess import call
import subprocess
from pymongo import MongoClient
import threading,Queue
from multiprocessing import Pool
import sys
from os import listdir
from os.path import isfile, join, isdir
import os
import shlex

def executeScripts(file):
    scriptsFolder = os.path.dirname(os.path.realpath(__file__)) + ""
    choice1 = join(scriptsFolder,"computeChoice1.py")
    fileToAnalyze = file[0]
    AuthorName = file[1]
    
    executionString = shlex.split('idaw.exe -B -A -S"' + choice1 + ' \\"'+ AuthorName + '\\"" ' + '"'+fileToAnalyze+'"')
    
    call(executionString)

    
def main():
    mypath = sys.argv[1]
    multiple = 0

    
    if len(sys.argv) >= 3:
        if "1" in sys.argv[2]:
            author = mypath.split("/")[-1:][0]
            multiple = 1
        else:
            author = sys.argv[3]

    client = MongoClient('localhost', 27017)
    db = client.BinAuthor
    collection = db.test
    collection.insert({"mypath":mypath,"multiple":multiple,"author":author})
            
    onlyfiles = [ [join(mypath,f),author] for f in listdir(mypath) if isfile(join(mypath,f)) ]
    onlyfolders = [ join(mypath,f) for f in listdir(mypath) if isdir(join(mypath,f)) ]
    
    if multiple == 1:
        for folder in onlyfolders:
            folderName = folder.split("\\")[-1:][0]
            onlyfiles = onlyfiles + [ [join(folder,f),folderName] for f in listdir(folder) if isfile(join(folder,f)) ]
    
    processPool = Pool(10)
    processPool.map(executeScripts,onlyfiles)

if __name__ == "__main__":
    main()