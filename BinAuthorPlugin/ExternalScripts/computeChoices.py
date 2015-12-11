import idautils
import math
import idc
import idaapi
from idautils import *
import simhash
from pymongo import MongoClient
import minhash

idaapi.autoWait()
class choice1():
    def __init__(self):
        self.fileName = idaapi.get_root_filename()
        self.fileMD5 = idautils.GetInputFileMD5()
        self.authorName = idc.ARGV[1]
        
    def choice1(self):
        client = MongoClient('localhost', 27017)
        db = client.BinAuthor
        collection = db.Choice1

        #fileName = idaapi.get_root_filename()
        #fileMD5 = idautils.GetInputFileMD5()

        mainEA = 0

        totalInstructions = 0
        instructionCounts = {"jmp":0,"cmp":0,"test":0,"mov":0,"call":0,"lea":0,"push":0,"indirect_call" : 0, "reg_used":0} 
        registerCounts = {}

        output = {}

        #authorName = idc.ARGV[1]

        for name in Names():
            if (str(name[1]).find("main") != -1) and (len(str(name[1])) <= 5):
                mainEA = name[0]

        currentea = mainEA
        while currentea != BADADDR and currentea < FindFuncEnd(mainEA):
            currentInstruction = GetMnem(currentea)
            if currentInstruction in instructionCounts.keys():
                instructionCounts[currentInstruction] += 1
            totalInstructions += 1
            currentea = NextHead(currentea)

        for item in Heads(mainEA,FindFuncEnd(mainEA)):
            #print hex(item) + ":" + GetMnem(item) + "\t" + str(idc.GetOpType(item,0)) + "\t" + str(idc.GetOpType(item,1))
            if "call" == GetMnem(item) and idc.GetOpType(item,0) == 1:
                instructionCounts["indirect_call"] += 1
            if idc.GetOpType(item,0) == 1:
                instructionCounts["reg_used"] += 1
                
                register = idc.GetOpnd(item,0)
                if register not in registerCounts.keys():
                    registerCounts[register] = 1
                else:
                    registerCounts[register] += 1
            if idc.GetOpType(item,1) == 1:
                instructionCounts["reg_used"] += 1
                
                register = idc.GetOpnd(item,1)
                if register not in registerCounts.keys():
                    registerCounts[register] = 1
                else:
                    registerCounts[register] += 1
                
        output["Total"] = totalInstructions
        output["push"] = instructionCounts["push"]
        output["call"] = instructionCounts["call"]
        output["indirect calls"] = instructionCounts["indirect_call"]
        output["regs used"] = instructionCounts["reg_used"]

        if float(totalInstructions) != 0 :
            output["ln(num push/length)"] = math.log(instructionCounts["push"]/float(totalInstructions))
            output["ln(num call/length)"] = math.log(instructionCounts["call"]/float(totalInstructions))
        else:
            output["ln(num push/length)"] = "infinity"
            output["ln(num call/length)"] = "infinity"
        if float(totalInstructions) != 0:
            if (instructionCounts["indirect_call"]/float(totalInstructions)) != 0 and (instructionCounts["reg_used"]/float(totalInstructions)) != 0:
                output["ln(num Indirect call/length)"] = math.log(instructionCounts["indirect_call"]/float(totalInstructions))
                output["ln(num reg used/length)"] = math.log(instructionCounts["reg_used"]/float(totalInstructions))
            elif (instructionCounts["indirect_call"]/float(totalInstructions)) == 0:
                output["ln(num Indirect call/length)"] = "infinity"
                output["ln(num reg used/length)"] = math.log(instructionCounts["reg_used"]/float(totalInstructions))
            elif (instructionCounts["reg_used"]/float(totalInstructions)) == 0:
                output["ln(num Indirect call/length)"] = math.log(instructionCounts["indirect_call"]/float(totalInstructions))
                output["ln(num reg used/length)"] = "infinity"
        else:
            output["ln(num Indirect call/length)"] = "infinity"
            output["ln(num reg used/length)"] = "infinity"

        if float(instructionCounts["lea"]) != 0 and (instructionCounts["push"]/float(instructionCounts["lea"])) != 0:
            output["ln(num push/num lea)"] = math.log(instructionCounts["push"]/float(instructionCounts["lea"]))
        else:
            output["ln(num push/num lea)"] = "infinity"

        if float(instructionCounts["test"]) != 0 and (instructionCounts["cmp"]/float(instructionCounts["test"])) != 0:     
            output["ln(num cmp/num test)"] = math.log(instructionCounts["cmp"]/float(instructionCounts["test"]))
        else:
            output["ln(num cmp/num test)"] = "infinity"

        if float(instructionCounts["push"]) != 0 and (instructionCounts["mov"]/float(instructionCounts["push"])) != 0:
            output["ln(num mov/num push)"] = math.log(instructionCounts["mov"]/float(instructionCounts["push"]))
        else:
            output["ln(num mov/num push)"] = "infinity" 
        if float(instructionCounts["lea"]) != 0 and (instructionCounts["jmp"]/float(instructionCounts["lea"])) != 0:
            output["ln(num jmp/num lea)"] = math.log(instructionCounts["jmp"]/float(instructionCounts["lea"]))
        else:
            output["ln(num jmp/num lea)"] = "infinity"

        if float(instructionCounts["call"]) != 0 and (instructionCounts["indirect_call"]/float(instructionCounts["call"])) != 0:     
            output["ln(num indirect call/num call)"] = math.log(instructionCounts["indirect_call"]/float(instructionCounts["call"]))
        else:
            output["ln(num indirect call/num call)"] = "infinity"

        if float(registerCounts["ecx"]) != 0:    
            output["ln(num eax/num ecx)"] = math.log(registerCounts["eax"]/float(registerCounts["ecx"]))
        else:
            output["ln(num eax/num ecx)"] = "infinity"
        if "esi" in registerCounts.keys() and "edi" in registerCounts.keys():
            if float(registerCounts["edi"]) != 0 and (registerCounts["esi"]/float(registerCounts["edi"])) != 0:
                output["ln(num esi/num edi)"] = math.log(registerCounts["esi"]/float(registerCounts["edi"]))
            else:
                output["ln(num esi/num edi)"] = "infinity"
        else:
            output["ln(num esi/num edi)"] = "infinity"

        document = {"General": output}

        if float(instructionCounts["lea"]) != 0:
            if (instructionCounts["push"]/float(instructionCounts["lea"])) != 0:
                feature1 = math.log(instructionCounts["push"]/float(instructionCounts["lea"]))
            else:
                feature1 = -1
            if (instructionCounts["jmp"]/float(instructionCounts["lea"])) != 0:
                feature2 = math.log(instructionCounts["jmp"]/float(instructionCounts["lea"]))
            else:
                feature2 = -1
        else:
            feature1 = -1
            feature2 = -1

        if float(instructionCounts["push"]) != 0 and (instructionCounts["mov"]/float(instructionCounts["push"])) != 0:
            feature3 = math.log(instructionCounts["mov"]/float(instructionCounts["push"]))
        else:
            feature3 = -1

        if float(instructionCounts["call"]) != 0 and (instructionCounts["indirect_call"]/float(instructionCounts["call"])) != 0:
            feature4 = math.log(instructionCounts["indirect_call"]/float(instructionCounts["call"]))
        else:
            feature4 = -1

        if float(instructionCounts["test"]) != 0 and (instructionCounts["cmp"]/float(instructionCounts["test"])) != 0:
            feature5 = math.log(instructionCounts["cmp"]/float(instructionCounts["test"]))
        else:
            feature5 = -1
            
        if float(totalInstructions) != 0:
            if (instructionCounts["reg_used"]/float(totalInstructions)) != 0:
                feature6 = math.log(instructionCounts["reg_used"]/float(totalInstructions))
            else:
                feature6 = -1
            if (instructionCounts["push"]/float(totalInstructions)) != 0:
                feature7 = math.log(instructionCounts["push"]/float(totalInstructions))
            else:
                feature7 = -1
            if (instructionCounts["call"]/float(totalInstructions)) != 0:
                feature8 = math.log(instructionCounts["call"]/float(totalInstructions))
            else:
                feature8 = -1
            if (instructionCounts["indirect_call"]/float(totalInstructions)) != 0:
                feature9 = math.log(instructionCounts["indirect_call"]/float(totalInstructions))
            else:
                feature9 = -1
        else:
            feature6 = -1
            feature7 = -1
            feature8 = -1
            feature9 = -1

        if float(registerCounts["ecx"]) != 0:
            feature10 = math.log(registerCounts["eax"]/float(registerCounts["ecx"]))
        else:
            feature10 = -1

        if "edi" in registerCounts.keys():
            if float(registerCounts["edi"]) != 0:
                feature11 = math.log(registerCounts["esi"]/float(registerCounts["edi"]))
            else:
                feature11 = -1
        else:
            feature11 = -2
        featureList = [feature1,\
                       feature3,\
                       feature4,\
                       feature5,\
                       feature6,\
                       feature10,\
                       feature11,\
                       feature2,\
                       feature7,\
                       feature8,\
                       feature9]
        document["features"] = featureList
        document["FileName"] = self.fileName
        document["FileMD5"] = self.fileMD5
        document["Author Name"] = self.authorName
        collection.insert(document)

class choice2():
    def __init__(self):
        self.fileName = idaapi.get_root_filename()
        self.fileMD5 = idautils.GetInputFileMD5()
        self.authorName = idc.ARGV[1]
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

class choice18():
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
        self.authorName = idc.ARGV[1]

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

    def choice18(self):
        for function in Functions():
            self.functionAddresstoRealFunctionName[function] = idaapi.get_func_name(function)
            self.createRegisterChain(True,function)
            
            
choice1 = choice1()    
choice1.choice1()
choice2 = choice2()
choice2.choice2()
choice18 = choice18()
choice18.choice18()
idc.Exit(0)