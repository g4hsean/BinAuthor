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

class Choice2():
    def __init__(self):
        self.fileName = idaapi.get_root_filename()
        self.fileMD5 = idautils.GetInputFileMD5()
        self.authorName = self.fileName
        self.allStrings = {}
        self.subStrings = ["cout","endl","Xlength_error","cerr"]
        self.returns = {"ret":0,"retn":0}
        self.libraryFunctionNamesDict = {"printf":[0,0],"fprintf":[0,0],"cout":[0,0],"exit":[0,0],"fflush":[0,0],"endl":[0,0],"puts":[0,0],"Xlength_error":[0,0],"clock":[0,0],"cerr":[0,0]}#,"scanf":[0,0]}

        self.standardRegisters = {"eax":0,"ebx":0,"ecx":0,"edx":0,"esi":0,"edi":0}
        self.libraryFunctionNameEADict = {}
            
    def choice2(self):
        client = MongoClient('localhost', 27017)
        db = client.BinAuthor
        collection = db.Choice2
        
        numOfInstructions = 0
        printfNewline = [0,0]
        mainEA = 0
        #fileName = idc.ARGV[1]

        self.getAllStrings()
        for name in Names():
            if (str(name[1]).find("main") != -1) and (len(str(name[1])) <= 5):
                mainEA = name[0]

        numberOfImports = idaapi.get_import_module_qty()

        for counter in xrange(0, numberOfImports):
            idaapi.enum_import_names(counter, self.getImportedFunctions)

        for address in Heads(mainEA,FindFuncEnd(mainEA)):
            numOfInstructions += 1


        currentInstruction = 0
        currentStackValue = ''
        numberOfCalls = 0
        previousInstructionEA = 0
        for address in Heads(mainEA,FindFuncEnd(mainEA)):
            currentInstruction += 1
            if GetMnem(address) == "push":
                previousInstructionEA = address
                currentStackValue = idc.GetOpnd(address,0)
            elif GetMnem(address) == "pop":
                currentStackValue = ''
            elif GetMnem(address) == "mov":
                if idc.GetOpnd(address,0) in self.standardRegisters.keys():
                    self.standardRegisters[idc.GetOpnd(address,0)] = idc.GetOperandValue(address,1)
                    
            distanceFromEndOfFunction = int(numOfInstructions * (3/float(4)))
            if idc.GetOpType(address,0) == 1 and idc.GetOpnd(address,0) in self.standardRegisters.keys():
                libraryInstruction = self.standardRegisters[idc.GetOpnd(address,0)]
            else:
                libraryInstruction = idc.GetOperandValue(address,0)
            
            for string in self.subStrings:
                if string in idc.GetOpnd(address,1) and currentInstruction >= distanceFromEndOfFunction:
                    self.libraryFunctionNamesDict[string][1] +=1
            
            if GetMnem(address) == "call" and currentInstruction >= distanceFromEndOfFunction:
                numberOfCalls += 1
            
            if GetMnem(address) in self.returns.keys() and currentInstruction >= distanceFromEndOfFunction:
                self.returns[GetMnem(address)] += 1
                
            if GetMnem(address) == "call" and libraryInstruction in self.libraryFunctionNameEADict.keys() and currentInstruction >= distanceFromEndOfFunction:
                if self.libraryFunctionNameEADict[libraryInstruction] == "exit":
                    if currentStackValue == "1":
                        self.libraryFunctionNamesDict[self.libraryFunctionNameEADict[libraryInstruction]][1] += 1
                else:
                    if "printf" in self.libraryFunctionNameEADict[libraryInstruction] and GetMnem(previousInstructionEA) == "push":
                        locationOfPushValue = idc.GetOperandValue(previousInstructionEA,0)
                        
                        if locationOfPushValue in self.allStrings.keys():
                            if "\n" in self.allStrings[locationOfPushValue]:
                                printfNewline[0] += 1
                            else:
                                printfNewline[1] += 1
                            
                            
                    self.libraryFunctionNamesDict[self.libraryFunctionNameEADict[libraryInstruction]][1] += 1

        output = {"LibraryFunctions": {}}
        for libraryFunction in self.libraryFunctionNamesDict.keys():
            output["LibraryFunctions"][libraryFunction] = self.libraryFunctionNamesDict[libraryFunction][1]
        
        output["calls"] = numberOfCalls
        
        output["returns"] = self.returns
        output["printf with newline"] = printfNewline[0]
        output["printf without newline"] = printfNewline[1]
        output["FileName"] = self.fileName
        output["FileMD5"] = self.fileMD5
        output["Author Name"] = self.authorName
        collection.insert(output)

    def getAllStrings(self):
        strings = idautils.Strings(default_setup = False)
        strings.setup(strtypes=Strings.STR_C | Strings.STR_UNICODE, ignore_instructions = True, display_only_existing_strings = True,minlen=1)
        for string in strings:
            self.allStrings[string.ea] = str(string)

    def getImportedFunctions(self,ea, libraryFunctionName, ord):
        if libraryFunctionName in self.libraryFunctionNamesDict.keys():
            self.libraryFunctionNamesDict[libraryFunctionName][0] = ea
            self.libraryFunctionNameEADict[ea] = libraryFunctionName
        
        if "cout" in libraryFunctionName:
            self.libraryFunctionNamesDict["cout"][0] = ea
            self.libraryFunctionNameEADict[ea] = "cout"
        
        if "endl" in libraryFunctionName:
            self.libraryFunctionNamesDict["endl"][0] = ea
            self.libraryFunctionNameEADict[ea] = "endl"
        
        if "Xlength_error" in libraryFunctionName:
            self.libraryFunctionNamesDict["Xlength_error"][0] = ea
            self.libraryFunctionNameEADict[ea] = "Xlength_error"
        
        if "cerr" in libraryFunctionName:
            self.libraryFunctionNamesDict["cerr"][0] = ea
            self.libraryFunctionNameEADict[ea] = "cerr"
        return True
