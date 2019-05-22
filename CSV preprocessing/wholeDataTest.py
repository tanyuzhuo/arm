import txtToCsv
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


txtToCsvClass = txtToCsv.test1_()

allFiles=[]
fileTypes = ["TT","FF","FS","SF","SS"]
direcOfFiles = "extract_SC_Mem_yield_Vmin"
for type in fileTypes:
    for fileName in os.listdir(direcOfFiles+"/"+type):
        if(len(fileName)>4):
            if(fileName[-4:]==".txt"):
                if(re.match("1st_",fileName)):
                    index = re.search("(?<=1st_)[0-9]+?(?=_(TT|FF|FS|SF|SS))",fileName).group(0)
                else:
                    index = re.match("[0-9]+?(?=_(TT|FF|FS|SF|SS))",fileName).group(0)
                if(re.search("_1.txt\Z",fileName)):
                    degrees = re.search("[M0-9]+(?=C_1.txt\Z)",fileName).group(0)
                else:
                    degrees = re.search("[M0-9]+(?=C.txt\Z)",fileName).group(0)
                allFiles.append(fileToParse(direcOfFiles,type,fileName,index,degrees))

startTime = datetime.datetime.now()
counter=0
averageTestTime=startTime-startTime
for file  in allFiles[:5]:
    try:
        startTestTime = datetime.datetime.now()
        txtToCsvClass.makeAllCSVs(file.filePath,file.folderPath)
        testTime = datetime.datetime.now()-startTestTime
        counter+=1
        print("File #"+str(counter)+" \""+file.fileName+"\" with time = "+str(testTime))
        averageTestTime += testTime
    except AttributeError as error:
        print(str(error)+" lines in file "+file.fileName+" were not created")
averageTestTime /= counter
endTime=datetime.datetime.now()
print("All conversions complete with avgTst = "+str(averageTestTime))
