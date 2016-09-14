import imp
import pip
import os
import sys
            
installerDirectory = os.getcwd()
os.chdir("../")
binAuthorDirectory = os.getcwd()
FeaturesDirectory = os.path.join(binAuthorDirectory,"Features")
os.chdir(installerDirectory)
os.chdir("./Dependencies")
dir_path = os.getcwd()
python = os.path.join(os.path.dirname(sys.executable),"python.exe")
from os import listdir
from os.path import isfile, join
from subprocess import call

dependencyName = ["pymongo","numpy","scipy","Levenshtein","simhash","sark","PySide","matplotlib"]
listOfDependencies = {"pymongo":"pymongo","numpy":os.path.join(dir_path, "numpy-1.11.1+mkl-cp27-cp27m-win32.whl"),"scipy":os.path.join(dir_path, "scipy-0.18.0-cp27-cp27m-win32.whl"),"Levenshtein":"python-Levenshtein","simhash":"simhash","sark":"git+https://github.com/tmr232/Sark.git#egg=Sark","PySide":os.path.join(dir_path,"PySide-1.2.2-cp27-none-win32.whl"),"matplotlib":"matplotlib-1.4.3-cp27-none-win32.whl"}

def install(package):
    pip.main(['install', package])

def checkImports():
    for dependency in dependencyName:
        try:
            imp.find_module(dependency)
            found = True
            print dependency + " found!"
        except ImportError:
            found = False
            print dependency + " not found!"
            print "Now installing " + dependency + "..."
            install(listOfDependencies[dependency])
    #print "installing pywin32 dlls..."
    #pywin32Path = os.path.join(os.path.join(os.path.dirname(sys.executable),"Scripts"),"pywin32_postinstall.py")
    #call([python,pywin32Path,"-install"])
    return 0

def installIDADependencies():
        from PySide import QtGui, QtCore, QtUiTools
        from shutil import copyfile
        
        app = QtGui.QApplication(sys.argv)
        print "Requesting Path For IDA Pro..."
        idaFolder = QtGui.QFileDialog.getExistingDirectory(options=0)
        folder = os.path.join(idaFolder,"plugins")

        setSystemPathVariable(idaFolder)

        binAuthorFile = os.path.join(folder,"BinAuthor_importer.py")
        with open(binAuthorFile,'w') as pluginFile:
            pluginFile.write("import sys\n")
            pluginFile.write("import imp\n")
            pluginFile.write("sys.path.append(\"" + binAuthorDirectory.replace("\\","\\\\") + "\")\n")
            pluginFile.write("plugin = imp.load_source(__name__,\"" + os.path.join(binAuthorDirectory,"BinAuthor.py").replace("\\","\\\\") + "\")\n")
            pluginFile.write("PLUGIN_ENTRY = plugin.PLUGIN_ENTRY\n")
            
        idaPythonFolder = os.path.join(idaFolder,"python")
        
        with open(os.path.join(idaPythonFolder,"pluginConfigurations.py"),"w") as moduleConfigFile:
            moduleConfigFile.write("def getRoot():\n")
            moduleConfigFile.write("\treturn \"" + FeaturesDirectory.replace("\\","\\\\") + "\\\\\"\n")
            moduleConfigFile.write("def getInstructionListPath():\n\treturn getRoot()\n")
            moduleConfigFile.write("def getGroupPath():\n\treturn getRoot()\n")
            pythonPath = str(sys.executable).replace("pythonw.exe","python.exe")
            moduleConfigFile.write("def getPythonPath():\n\treturn \"" + pythonPath + "\"\n")

        minhashFolder = os.path.join(os.path.join(os.path.join(binAuthorDirectory,"BinAuthorPlugin"),"ExternalScripts"),"minhash")

        onlyfiles = [f for f in listdir(minhashFolder) if isfile(join(minhashFolder, f))]
        for minhashFile in onlyfiles:
            copyfile(os.path.join(minhashFolder,minhashFile), os.path.join(idaPythonFolder,minhashFile))
        
def installMongoDBDependencies():
    from PySide import QtGui, QtCore, QtUiTools
    from shutil import copyfile

    #app = QtGui.QApplication(sys.argv)
    print "Requesting Install Path For MongoDB..."
    mongoDBFolder = QtGui.QFileDialog.getExistingDirectory(options=0)
    for root, directory, filelist in os.walk(mongoDBFolder):
            for file in filelist:
                if file  == 'mongod.exe': 
                    fullpath  = root
    mongoDBExecutablePath = os.path.join(fullpath, 'mongod.exe')
    databaseDataPath = os.path.join(os.path.join(binAuthorDirectory,"Database"),"data")
    desktopPath = os.path.join(os.path.expanduser("~/Desktop"),"BinAuthor_MongoDB_Start.bat")
    with open(desktopPath,"w") as script:
        script.write("\"" + mongoDBExecutablePath + "\" --dbpath \"" + databaseDataPath + "\"")

def setSystemPathVariable(pathToAdd):
    from _winreg import *
    
    aReg = ConnectRegistry(None,HKEY_LOCAL_MACHINE)

    environmentVariableKey = OpenKey(aReg, r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment",0,KEY_ALL_ACCESS)
    pathData = QueryValueEx(environmentVariableKey,"Path")
    value = pathData[0] + os.pathsep + "\"" + pathToAdd + "\""
    SetValueEx(environmentVariableKey,"Path",0,pathData[1],value)
    CloseKey(environmentVariableKey)

def installPlugin():
    installIDADependencies()
    installMongoDBDependencies()
    call([os.path.join(installerDirectory, "WM_SETTINGCHANGE_Broadcast.exe")])
    

if checkImports() == 0:
    installPlugin()
