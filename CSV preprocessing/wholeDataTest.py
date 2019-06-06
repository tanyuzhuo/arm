import txtToCsv
import os
import re
import datetime

#if this constant is 0 ouputs csv per file
#if this constant is 1 ouputs csv per type
#if this constant is 2 ouputs csv per type, temp
#if this constant is 3 ouputs csv per all direc
OUTPUT_FORM = 3

class fileToParse:
    def __init__(self,_topPath,_section,_fileName,_index,_degrees):
        self.filePath = _topPath+"/"+_section+"/"+_fileName
        self.topPath = _topPath
        self.section = _section
        self.fileName = _fileName
        self.type = _section
        self.index = _index
        self.degrees = _degrees

class wholeDataTest:
    def __init__(self):
        self.allFiles=[]
        self.fileTypes = ["TT","FF","FS","SF","SS"]
        self.direcOfFiles = "extract_SC_Mem_yield_Vmin"

    def collectFiles(self):
        try:
            for type in self.fileTypes:
                for fileName in os.listdir(self.direcOfFiles+"/"+type):
                    if(len(fileName)>4):
                        if(fileName[-4:]==".txt"):
                            if(re.match("1st_",fileName)):
                                print("fileName = "+fileName+" is invalid and will be ignored")
                                #index = re.search("(?<=1st_)[0-9]+?(?=_(TT|FF|FS|SF|SS))",fileName).group(0)
                            else:
                                index = re.match("[0-9]+?(?=_(TT|FF|FS|SF|SS))",fileName).group(0)
                                if(re.search("_1.txt\Z",fileName)):
                                    print("fileName = "+fileName+" is invalid and will be ignored")
                                    #degrees = re.search("[M0-9]+(?=C_1.txt\Z)",fileName).group(0)
                                else:
                                    degrees = re.search("[M0-9]+(?=C.txt\Z)",fileName).group(0)
                                    self.allFiles.append(fileToParse(self.direcOfFiles,type,fileName,index,degrees))
        except FileNotFoundError:
            raise FileNotFoundError("Directory not found")

    def processAllCSV(self):
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

                #new file for every file
                if OUTPUT_FORM == 0:
                    folderPath="resultsPerFile/"+file.topPath+"/"+file.section+"/"+file.fileName[:-4]
                    txtToCsvClass.output(OUTPUT_FORM,1,"","","",file.filePath,folderPath)
                #new file for every temp type combo
                elif OUTPUT_FORM == 1:
                    if lastFileTemp != file.degrees:
                        if lastFileType != file.type:
                            fileCounter=1
                    lastFileType = file.type
                    lastFileTemp = file.degrees
                    folderPath="resultsPerTypeTemp/"+file.topPath+"/"+file.section+"/"+file.degrees
                    txtToCsvClass.output(OUTPUT_FORM,fileCounter,"","",file.type,file.filePath,folderPath)
                #new file for every type
                elif OUTPUT_FORM == 2:
                    if lastFileType != file.type:
                        fileCounter=1
                    lastFileType = file.type
                    folderPath="resultsPerType/"+file.topPath+"/"+file.section
                    txtToCsvClass.output(OUTPUT_FORM,fileCounter,file.degrees,"",file.type,file.filePath,folderPath)
                #one set of files
                elif OUTPUT_FORM == 3:
                    txtToCsvClass.output(OUTPUT_FORM,fileCounter,file.degrees,file.index,file.type,file.filePath,"resultsPerDir")

                testTime = datetime.datetime.now()-startTestTime
                print("I am on number "+str(allFilesCounter)+" of "+str(totalNoFiles), end='\r', flush=True)
                print("file "+file.fileName+" in time = "+str(testTime))
                averageTestTime += testTime
            except AttributeError as error:
                print(str(error)+" lines in file "+file.fileName+" were not created")

        print("Total test time = "+str(averageTestTime))
        averageTestTime /= totalNoFiles
        endTime=datetime.datetime.now()
        print("All conversions complete with avgTst = "+str(averageTestTime))

wholeDataTest = wholeDataTest()
wholeDataTest.collectFiles()
wholeDataTest.processAllCSV()
