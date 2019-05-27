import txtToCsv
import txtToOneCsv
import os
import re
import datetime

class fileToParse:
    def __init__(self,_topPath,_section,_fileName,_index,_degrees):
        self.filePath = _topPath+"/"+_section+"/"+_fileName
        self.folderPath = "results/"+_topPath+"/"+_section+"/"+_fileName[:-4]
        self.topPath = _topPath
        self.section = _section
        self.fileName = _fileName
        self.type = _section
        self.index = _index
        self.degrees = _degrees


#txtToCsvClass = txtToCsv.test1_()
txtToOneCsvClass = txtToOneCsv.txtToCsv()

allFiles=[]
fileTypes = ["TT","FF","FS","SF","SS"]
direcOfFiles = "extract_SC_Mem_yield_Vmin"
for type in fileTypes:
    for fileName in os.listdir(direcOfFiles+"/"+type):
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
                        allFiles.append(fileToParse(direcOfFiles,type,fileName,index,degrees))

startTime = datetime.datetime.now()
counter=0
averageTestTime=startTime-startTime
for fileNumber,file in enumerate(allFiles, 1):
    #try:
        startTestTime = datetime.datetime.now()
        #txtToCsvClass.makeAllCSVs(file.filePath,file.folderPath)

        #txtToOneCsvClass.output(file.filePath,"resultsOneFile")
        if file.fileName =="121_TT_M40C.txt":
            txtToOneCsvClass.outputOneFile(fileNumber,file.degrees,file.index,file.type,file.filePath,"resultsOneFile")

        testTime = datetime.datetime.now()-startTestTime
        #print("file "+file.fileName+" in time = "+str(testTime))
        counter+=1
        averageTestTime += testTime
    #except AttributeError as error:
        #print(str(error)+" lines in file "+file.fileName+" were not created")

print("Total test time = "+str(averageTestTime))
averageTestTime /= counter
endTime=datetime.datetime.now()
print("All conversions complete with avgTst = "+str(averageTestTime))
