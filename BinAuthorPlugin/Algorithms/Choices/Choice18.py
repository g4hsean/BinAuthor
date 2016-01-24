from idaapi import *
from idc import *
import idautils
import math
import idc
import idaapi
from idautils import *
import simhash
from pymongo import MongoClient
import minhash

class Choice18():
    def __init__(self):
        self.functionAddresstoRealFunctionName = {}
        self.functionRegisterChains = {}
        self.finalOutput = ''
        self.finalOutputFunctionLevel = ''
        self.simhashList = []
        self.registerChainMinhash = []
        self.blocks = []
        self.fileName = idaapi.get_root_filename()
        self.fileMD5 = idautils.GetInputFileMD5()
        self.authorName = self.fileName

    def createRegisterChain(self,p,ea):
        f = idaapi.FlowChart(idaapi.get_func(ea))
        
        functionName = idaapi.get_func_name(ea)
        client = MongoClient('localhost', 27017)
        db = client.BinAuthor
        collection = db.Choice18
        
        if idaapi.get_func_name(ea) not in self.functionRegisterChains.keys():
            self.functionRegisterChains[idaapi.get_func_name(ea)] = {}
        for block in f:
            if p:
                registerChain = {}
                for address in Heads(block.startEA,block.endEA):
                    if idc.GetOpType(address, 0) == 1 and idc.GetOpnd(address, 0) != "":
                        if idc.GetOpnd(address, 0) not in self.functionRegisterChains[idaapi.get_func_name(ea)].keys():
                            self.functionRegisterChains[idaapi.get_func_name(ea)][idc.GetOpnd(address, 0)] = [GetMnem(address)]
                        else:
                            self.functionRegisterChains[idaapi.get_func_name(ea)][idc.GetOpnd(address, 0)].append(GetMnem(address))
                            
                        if idc.GetOpnd(address, 0) not in registerChain.keys():
                            registerChain[idc.GetOpnd(address, 0)] = [GetMnem(address)]
                        else:
                            registerChain[idc.GetOpnd(address, 0)].append(GetMnem(address))
                    if idc.GetOpType(address, 1) == 1  and idc.GetOpnd(address, 1) != "":
                        if idc.GetOpnd(address, 1) not in self.functionRegisterChains[idaapi.get_func_name(ea)].keys():
                            self.functionRegisterChains[idaapi.get_func_name(ea)][idc.GetOpnd(address, 1)] = [GetMnem(address)]
                        else:
                            self.functionRegisterChains[idaapi.get_func_name(ea)][idc.GetOpnd(address, 1)].append(GetMnem(address))
                        
                        if idc.GetOpnd(address, 1) not in registerChain.keys():
                            registerChain[idc.GetOpnd(address, 1)] = [GetMnem(address)]
                        else:
                            registerChain[idc.GetOpnd(address, 1)].append(GetMnem(address))
                for register in registerChain.keys():
                    fingerPrint = str(register)
                    functionMinhashes = {}
                    functionMinhashes["FunctionName"] = functionName
                    functionMinhashes["FileName"] = self.fileName
                    functionMinhashes["FileMD5"] = self.fileMD5
                    functionMinhashes["Author Name"] = self.authorName
                    functionMinhashes["BlockStartEA"] = block.startEA
                    functionMinhashes["register"] = register
                    functionMinhashes["registerChain"] = registerChain[register]
                    counter = 0
                    for instruction in registerChain[register]:
                        fingerPrint += " " + str(instruction)
                        counter += 1
                        
                    functionMinhashes["SimHashSignature"] = str(simhash.Simhash(fingerPrint).value)

                    self.simhashList.append([counter,simhash.Simhash(fingerPrint).value])
                    if len(fingerPrint.split(" ")) >= 6:
                        self.registerChainMinhash.append([fingerPrint,minhash.minHash(minhash.createShingles(fingerPrint))])
                        functionMinhashes["MinHashSignature"] = minhash.minHash(minhash.createShingles(fingerPrint))
                        collection.insert(functionMinhashes)
                    else:
                        self.registerChainMinhash.append([fingerPrint,])
                        
    def createRegisterChainA(self,p,ea):
        f = idaapi.FlowChart(idaapi.get_func(ea))
        
        functionName = idaapi.get_func_name(ea)
        
        functions = []
        
        if idaapi.get_func_name(ea) not in self.functionRegisterChains.keys():
            self.functionRegisterChains[idaapi.get_func_name(ea)] = {}
        for block in f:
            if p:
                registerChain = {}
                for address in Heads(block.startEA,block.endEA):
                    if idc.GetOpType(address, 0) == 1 and idc.GetOpnd(address, 0) != "":
                        if idc.GetOpnd(address, 0) not in self.functionRegisterChains[idaapi.get_func_name(ea)].keys():
                            self.functionRegisterChains[idaapi.get_func_name(ea)][idc.GetOpnd(address, 0)] = [GetMnem(address)]
                        else:
                            self.functionRegisterChains[idaapi.get_func_name(ea)][idc.GetOpnd(address, 0)].append(GetMnem(address))
                            
                        if idc.GetOpnd(address, 0) not in registerChain.keys():
                            registerChain[idc.GetOpnd(address, 0)] = [GetMnem(address)]
                        else:
                            registerChain[idc.GetOpnd(address, 0)].append(GetMnem(address))
                    if idc.GetOpType(address, 1) == 1  and idc.GetOpnd(address, 1) != "":
                        if idc.GetOpnd(address, 1) not in self.functionRegisterChains[idaapi.get_func_name(ea)].keys():
                            self.functionRegisterChains[idaapi.get_func_name(ea)][idc.GetOpnd(address, 1)] = [GetMnem(address)]
                        else:
                            self.functionRegisterChains[idaapi.get_func_name(ea)][idc.GetOpnd(address, 1)].append(GetMnem(address))
                        
                        if idc.GetOpnd(address, 1) not in registerChain.keys():
                            registerChain[idc.GetOpnd(address, 1)] = [GetMnem(address)]
                        else:
                            registerChain[idc.GetOpnd(address, 1)].append(GetMnem(address))
                for register in registerChain.keys():
                    fingerPrint = str(register)
                    functionMinhashes = {}
                    functionMinhashes["FunctionName"] = functionName
                    functionMinhashes["FileName"] = self.fileName
                    functionMinhashes["FileMD5"] = self.fileMD5
                    functionMinhashes["Author Name"] = self.authorName
                    functionMinhashes["BlockStartEA"] = block.startEA
                    functionMinhashes["register"] = register
                    functionMinhashes["registerChain"] = registerChain[register]
                    counter = 0
                    for instruction in registerChain[register]:
                        fingerPrint += " " + str(instruction)
                        counter += 1
                        
                    functionMinhashes["SimHashSignature"] = str(simhash.Simhash(fingerPrint).value)

                    self.simhashList.append([counter,simhash.Simhash(fingerPrint).value])
                    if len(fingerPrint.split(" ")) >= 6:
                        self.registerChainMinhash.append([fingerPrint,minhash.minHash(minhash.createShingles(fingerPrint))])
                        functionMinhashes["MinHashSignature"] = minhash.minHash(minhash.createShingles(fingerPrint))
                        functions.append(functionMinhashes)
                    else:
                        self.registerChainMinhash.append([fingerPrint,])
        return functions

    def choice18(self):
        for function in Functions():
            self.functionAddresstoRealFunctionName[function] = idaapi.get_func_name(function)
            self.createRegisterChain(True,function)
            
    def choice18A(self):
        functions = []
        for function in Functions():
            self.functionAddresstoRealFunctionName[function] = idaapi.get_func_name(function)
            functions.append(self.createRegisterChainA(True,function))
            
        return functions
   