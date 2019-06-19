import txtToCsv
import os
import re
import datetime

#if this constant is 0 ouputs csv per file
#if this constant is 1 ouputs csv per type
#if this constant is 2 ouputs csv per type, temp
#if this constant is 3 ouputs csv per all direc
OUTPUT_FORM = 3

#a class to store a list of file information so they can be looped through quickly
class fileToParse:
    def __init__(self,_topPath,_section,_fileName,_index,_degrees):
        self.filePath = _topPath+"/"+_section+"/"+_fileName
        self.topPath = _topPath
        self.section = _section
        self.fileName = _fileName
        self.type = _section
        self.index = _index
        self.degrees = _degrees

#make the whole thing a class to avoid globals and attempt to encapsulate as much as possible
#also split into different functions to help testing
class wholeDataTest:
    #input the directory to where all the files are stored "extract_SC_Mem_yield_Vmin"
    def __init__(self,textDirec):
        self.allFiles=[]
        #adjust this variable if all files don't exist
        self.fileTypes = ["TT","FF","FS","SF","SS"]
        self.direcOfFiles = textDirec

    #this function works through the file directory and compiles them in the fileToParse class into a list
    def collectFiles(self):
        try:
            #adjust in constructor to cater to more or less files
            for type in self.fileTypes:
                for fileName in os.listdir(self.direcOfFiles+"/"+type):
                    #avoids an index out of bounds
                    if(len(fileName)>4):
                        #cuts off ".txt"
                        if(fileName[-4:]==".txt"):
                            #matches manually created files and ignores them
                            if(re.match("1st_",fileName)):
                                print("fileName = "+fileName+" is invalid and will be ignored")
                            else:
                                #matches manually created files and ignores them
                                if(re.search("_1.txt\Z",fileName)):
                                    print("fileName = "+fileName+" is invalid and will be ignored")
                                else:
                                    #finally gets some meta-info for class and appends to list
                                    degrees = re.search("[M0-9]+(?=C.txt\Z)",fileName).group(0)
                                    index = re.match("[0-9]+?(?=_(TT|FF|FS|SF|SS))",fileName).group(0)
                                    self.allFiles.append(fileToParse(self.direcOfFiles,type,fileName,index,degrees))
        #if file isnt found print error not crash
        except FileNotFoundError:
            raise FileNotFoundError("Directory not found")

    #the actual processing function that for each class item calls the function in txtToCsv
    def processAllCSV(self):
        #takes time taken for each one for timing help prints in terminal
        averageTestTime=datetime.datetime.now()-datetime.datetime.now()

        allFilesCounter = 0
        fileCounter = 0
        lastFileType = ""
        lastFileTemp = ""
        txtToCsvClass = txtToCsv.txtToCsv()
        totalNoFiles = len(self.allFiles)

        for file in self.allFiles:
            allFilesCounter+=1
            fileCounter+=1
            try:
                startTestTime = datetime.datetime.now()

                #FORM - new file for every file
                if OUTPUT_FORM == 0:
                    folderPath="resultsPerFile/"+file.topPath+"/"+file.section+"/"+file.fileName[:-4]
                    txtToCsvClass.output(OUTPUT_FORM,1,"","","",file.filePath,folderPath)
                #FORM - new file for every temp type combo
                elif OUTPUT_FORM == 1:
                    if lastFileTemp != file.degrees:
                        if lastFileType != file.type:
                            fileCounter=1
                    lastFileType = file.type
                    lastFileTemp = file.degrees
                    folderPath="resultsPerTypeTemp/"+file.topPath+"/"+file.section+"/"+file.degrees
                    txtToCsvClass.output(OUTPUT_FORM,fileCounter,"","",file.type,file.filePath,folderPath)
                #FORM - new file for every type
                elif OUTPUT_FORM == 2:
                    if lastFileType != file.type:
                        fileCounter=1
                    lastFileType = file.type
                    folderPath="resultsPerType/"+file.topPath+"/"+file.section
                    txtToCsvClass.output(OUTPUT_FORM,fileCounter,file.degrees,"",file.type,file.filePath,folderPath)
                #FORM - one set of files
                elif OUTPUT_FORM == 3:
                    txtToCsvClass.output(OUTPUT_FORM,fileCounter,file.degrees,file.index,file.type,file.filePath,"resultsPerDir")

                testTime = datetime.datetime.now()-startTestTime
                print("I am on number "+str(allFilesCounter)+" of "+str(totalNoFiles)+" finished last file in "+str(testTime), end='\r', flush=True)
                averageTestTime += testTime
            #if a line isn't know will print below
            except AttributeError as error:
                print(str(error)+" lines in file "+file.fileName+" were not created")
        #prints timing info at the end
        print("Total test time = "+str(averageTestTime))
        averageTestTime /= totalNoFiles
        endTime=datetime.datetime.now()
        print("All conversions complete with avgTst = "+str(averageTestTime))

#laid out the same as the above function but splits the function up so that a progress bar can be shown
    def processAllCSVInit(self):
        self.averageTestTime=datetime.datetime.now()-datetime.datetime.now()

        self.allFilesCounter = 0
        self.fileCounter = 0
        self.lastFileType = ""
        self.lastFileTemp = ""
        self.txtToCsvClass = txtToCsv.txtToCsv()
        self.totalNoFiles = len(self.allFiles)

        return self.totalNoFiles

    def processIndivCSV(self,fileNo):
        file = self.allFiles[fileNo]
        self.allFilesCounter+=1
        self.fileCounter+=1
        try:
            startTestTime = datetime.datetime.now()

            #new file for every file
            if OUTPUT_FORM == 0:
                folderPath="resultsPerFile/"+file.topPath+"/"+file.section+"/"+file.fileName[:-4]
                self.txtToCsvClass.output(OUTPUT_FORM,1,"","","",file.filePath,folderPath)
            #new file for every temp type combo
            elif OUTPUT_FORM == 1:
                if self.lastFileType != file.degrees:
                    if self.lastFileType != file.type:
                        self.fileCounter=1
                self.lastFileType = file.type
                self.lastFileType = file.degrees
                folderPath="resultsPerTypeTemp/"+file.topPath+"/"+file.section+"/"+file.degrees
                self.txtToCsvClass.output(OUTPUT_FORM,self.fileCounter,"","",file.type,file.filePath,folderPath)
            #new file for every type
            elif OUTPUT_FORM == 2:
                if self.lastFileType != file.type:
                    self.fileCounter=1
                self.lastFileType = file.type
                folderPath="resultsPerType/"+file.topPath+"/"+file.section
                self.txtToCsvClass.output(OUTPUT_FORM,self.fileCounter,file.degrees,"",file.type,file.filePath,folderPath)
            #one set of files
            elif OUTPUT_FORM == 3:
                self.txtToCsvClass.output(OUTPUT_FORM,self.fileCounter,file.degrees,file.index,file.type,file.filePath,"resultsPerDir")

            testTime = datetime.datetime.now()-startTestTime
            print("I am on number "+str(self.allFilesCounter)+" of "+str(self.totalNoFiles)+", finished last file in "+str(testTime), end='\r', flush=True)
            self.averageTestTime += testTime
        except AttributeError as error:
            print(str(error)+" lines in file "+file.fileName+" were not created")

    def testsFinished(self):
        print()
        print("Total test time = "+str(self.averageTestTime))
        self.averageTestTime /= self.totalNoFiles
        endTime=datetime.datetime.now()
        print("All conversions complete with avgTst = "+str(self.averageTestTime))

#wholeDataTest = wholeDataTest()
#wholeDataTest.collectFiles()
#wholeDataTest.processAllCSV()
