import csv
import re
import os
import sys
import datetime

class txtToCsv:
    #function to send all file lines off
    def processFileLines(self,inFilePath):
        #declares post processed line arrays
        self.metaData=[]
        self.unusedData=[]
        self.pinsData=[]
        self.leakageData=[]
        self.vminStdData=[]
        self.memData=[]
        self.vminCkbData=[]
        self.shmooData=[]
        #used to find the timing at the end of the file
        self.postMetaFlag=0
        #indicates section on last line
        self.lastLineSection=""

        with open(inFilePath, 'r') as in_file:
            for line_number, line in enumerate(in_file, 1):
                self.parseAnyLine(line,line_number)

    def parseAnyLine(self,line,line_number):
        #removes - < and spaces from file
        line = line.strip()
        line = re.sub("[-]+", "", line)
        line = re.sub("<", "", line)
        line = re.sub("\A\s+\Z", "", line)
        #subs space to commas and then splits into an array
        line = re.sub("\s+", ",", line)
        lineArray = line.split(",")

        #checks not an empty line
        #if(re.search("F_F",line) or re.search("S_S",line) or re.search("f_f",line)):
            #print("found in file temp "+self.fileTemp+" index "+self.fileIndex+" and type "+self.fileType)
        if not re.search("^$",line):
            thisSection=""
            #checks meta data so it can
            if re.match("dut1",line) or re.match("TestStarted",line) or re.match("SITE",line):
                thisSection="meta"
                self.postMetaFlag+=1
                self.metaData.append(lineArray)
            #this if is triggered at the end of the txt file for timing
            elif self.postMetaFlag>2:
                thisSection="meta"
                self.metaData.append(lineArray)
            #triggered for the pins if matches any o
            elif re.match("[0-9]+,[A-Z0-9]+,[a-z0-9_]+,[A-Z0-9_]+,[a-z_]+,[a-zA-Z]+,",line):
                thisSection="pins"
                self.parsePin(line,lineArray)
            elif re.search("\Atb_leakage_",line):
                thisSection="leakage"
                self.parseLeakage(line,lineArray)
            elif re.search("\A[0-9]+,tb_sc_yd_vmin_shm",line) or re.search("\Ashmoo_bsmin_vec_stdcell_",line):
                thisSection="vminStd"
                self.parseVminStd(line,lineArray)
            elif re.match("[0-9]+?,tb_mem_yd_ckb",line) or (re.match("\([0-9]+?,pins\),FAILED",line) and self.lastLineSection=="mem"):
                thisSection="mem"
                self.parseMem(line,lineArray)
            elif re.search("\A[0-9]+,tb_vmin_ckb",line) or (re.match("\([0-9]+?,pins\),FAILED",line) and self.lastLineSection=="vminCkb") or (re.search("\Ashmoo_bsmin_vec(?!_stdcell_)",line) and self.lastLineSection=="vminCkb"):
                thisSection="vminCkb"
                self.parseVminCkb(line,lineArray)
            elif re.match("shmoo_vec_",line) or (re.match("shmoo_bsmin_vec_",line) and self.lastLineSection=="shmoo"):
                thisSection="shmoo"
                self.parseShmoo(line,lineArray)
            else:
                if(not re.match("TstNum,Pin,Chn",line)):
                    thisSection=""
                    self.unusedData.append(lineArray)
            self.lastLineSection=thisSection

    def parsePin(self,line,lineArray):
        if(self.lastLineSection!="pins"):
            if self.fileCount is 1:
                header = ["TstNum","Pin","Chn","Pin Name","Test Block","Test Name","Force Value","Low Limit","Test Value","P/F","High Limit"]
                if self.outputForm is 3:
                    header = ["Chip Type","Chip Temp","File Index"]+header
                if self.outputForm is 2:
                    header = ["Chip Type","Chip Temp"]+header
                if self.outputForm is 1:
                    header = ["Chip Type"]+header
                self.pinsData.append(header)
        units=["uA","mV","mA","uA","pV","V"]
        if(lineArray[5]=="Cont"):
            lineArray[5]="Cont N"
            lineArray.pop(6)

        if(not lineArray[12]=="(F)"):
            lineArray.insert(12,"(P)")

        breakFlag=0
        for unitName in units:
            if lineArray[7] in unitName:
                lineArray[6]=lineArray[6]+" "+unitName
                lineArray.pop(7)
                break
            else:
                continue
            break
        for unitName in units:
            if lineArray[8] in unitName:
                lineArray[7]=lineArray[7]+" "+unitName
                lineArray.pop(8)
                break
            else:
                continue
            break
        for unitName in units:
            if lineArray[9] in unitName:
                lineArray[8]=lineArray[8]+" "+unitName
                lineArray.pop(9)
                break
            else:
                continue
            break
        for unitName in units:
            if lineArray[11] in unitName:
                lineArray[10]=lineArray[10]+" "+unitName
                lineArray.pop(11)
                break
            else:
                continue
            break

        if self.outputForm is 3:
            lineArray=[self.fileType,self.fileTemp,self.fileIndex]+lineArray
        if self.outputForm is 2:
            lineArray=[self.fileType,self.fileTemp]+lineArray
        if self.outputForm is 1:
            lineArray=[self.fileType]+lineArray
        self.pinsData.append(lineArray)
    def parseLeakage(self,line,lineArray):
        if self.lastLineSection != "leakage":
            if self.fileCount is 1:
                header = ["Leakage Test Type","Pin","VDD (Range)","DVDD (Range)","Period (Range)","Value"]
                if self.outputForm is 3:
                    header = ["Chip Type","Chip Temp","File Index"]+header
                if self.outputForm is 2:
                    header = ["Chip Type","Chip Temp"]+header
                if self.outputForm is 1:
                    header = ["Chip Type"]+header
                self.leakageData.append(header)

        if lineArray[0] == "tb_leakage_high":
            lineArray[0]="high"
        elif lineArray[0] == "tb_leakage_low":
            lineArray[0]="low"

        lineArray.insert(1,re.match("[a-zA-Z0-9_]+(?=_leakage)",lineArray[1]).group(0))
        lineArray.insert(2,re.search("(?<=vdd_)[\-0-9\.]+(?=V_dvdd)",lineArray[2]).group(0)+" V")
        lineArray.insert(3,re.search("(?<=dvdd_)[\-0-9\.]+(?=V_)",lineArray[3]).group(0)+" V")
        lineArray[4]=re.search("(?<=_)[-0-9.]+(?=ns\Z)",lineArray[4]).group(0)+" ns"

        if(lineArray[6]=="uA"):
            lineArray[5]+=" uA"
            lineArray.pop(6)

        if self.outputForm is 3:
            lineArray=[self.fileType,self.fileTemp,self.fileIndex]+lineArray
        if self.outputForm is 2:
            lineArray=[self.fileType,self.fileTemp]+lineArray
        if self.outputForm is 1:
            lineArray=[self.fileType]+lineArray
        self.leakageData.append(lineArray)
    def parseVminStd(self,line,lineArray):
        if self.lastLineSection is not "vminStd":
            if self.fileCount is 1:
                header = ["Test Number","Test Item","VDD (Range)","DVDD (Range)","Period (Range)","Result","Shmoo Value"]
                if self.outputForm is 3:
                    header = ["Chip Type","Chip Temp","File Index"]+header
                if self.outputForm is 2:
                    header = ["Chip Type","Chip Temp"]+header
                if self.outputForm is 1:
                    header = ["Chip Type"]+header
                self.vminStdData.append(header)
        if re.search("\Ashmoo_bsmin_vec_stdcell_",line):
            self.vminStdData[len(self.vminStdData)-1].append(lineArray[1][:-1])
            return

        if lineArray[1]=="tb_sc_yd_vmin_shm":
            lineArray.pop(1)

        lineArray.insert(1,re.search("(?<=stdcell_)[a-z0-9]+?_[a-z0-9]+?_[a-z0-9]+?_[a-z0-9]+?(?=_)",lineArray[1]).group(0))

        lineArray.insert(2,re.search("(?<=vdd_)[\-0-9\.]+(?=V_dvdd)",lineArray[2]).group(0)+" V")
        lineArray.insert(3,re.search("(?<=dvdd_)[\-0-9\.]+(?=V_)",lineArray[3]).group(0)+" V")

        lineArray[4]=re.search("(?<=_)[-0-9.]+(?=nS\Z)",lineArray[4]).group(0)+" ns"

        if self.outputForm is 3:
            lineArray=[self.fileType,self.fileTemp,self.fileIndex]+lineArray
        if self.outputForm is 2:
            lineArray=[self.fileType,self.fileTemp]+lineArray
        if self.outputForm is 1:
            lineArray=[self.fileType]+lineArray
        self.vminStdData.append(lineArray)
    def parseMem(self,line,lineArray):
        if self.lastLineSection is not "mem":
            if self.fileCount is 1:
                header = ["Test Number","A/S","R/F","Architecture","??","EMA#1","EMA#2","EMAW","EMAS","EMAP","WABL","WABLM","RAWL","RAWLM","KEN","VDDPE (Range)","VDDCE (Range)","DVDD (Range)","Period (Range)","Value","Number of Failed Pins","Failed Pins"]
                if self.outputForm is 3:
                    header = ["Chip Type","Chip Temp","File Index"]+header
                if self.outputForm is 2:
                    header = ["Chip Type","Chip Temp"]+header
                if self.outputForm is 1:
                    header = ["Chip Type"]+header
                self.memData.append(header)
        if re.match("\([0-9]+?,pins\),FAILED",line):
            tempList = []
            tempList.append(lineArray[0][1:])
            counter=5
            while(lineArray[counter][0]!="}"):
                if(counter==5):
                    tempList.append(lineArray[counter])
                else:
                    tempList[1]=tempList[1]+" "+lineArray[counter]
                counter+=1
            self.memData[len(self.memData)-1].extend(tempList)
            return

        lineArray.insert(1,re.search("[a-zA-Z]+(?=_[A-Z]\Z)",lineArray[1]).group(0))
        lineArray[2]=re.search("(?<=_)[A-Z]\Z",lineArray[2]).group(0)

        if re.search("(?<=\Afunc_vec_)[a-zA-Z0-9]+?(?=_)",lineArray[3]).group(0) == "cln16ffcll":
            lineArray.insert(3,re.search("(?<=\Afunc_vec_)[a-zA-Z0-9_]+?_[a-zA-Z0-9]+?_[a-zA-Z0-9]+?_[a-zA-Z0-9]+?(?=_)",lineArray[3]).group(0))
            lineArray[4]=re.sub("\Afunc_vec_[a-zA-Z0-9_]+?_[a-zA-Z0-9]+?_[a-zA-Z0-9]+?_[a-zA-Z0-9]+?_","",lineArray[4])
        else:
            lineArray.insert(3,re.search("(?<=\Afunc_vec_)[a-zA-Z0-9]+?_[a-zA-Z0-9]+?(?=_)",lineArray[3]).group(0))
            lineArray[4]=re.sub("\Afunc_vec_[a-zA-Z0-9]+?_[a-zA-Z0-9]+?_","",lineArray[4])

        lineArray.insert(4,re.search("\A[a-zA-Z0-9_]+?(?=_ema)",lineArray[4]).group(0))
        lineArray.insert(5,re.search("(?<=ema)[a-zA-Z0-9]+?(?=_ema)",lineArray[5]).group(0))
        lineArray.insert(6,re.search("(?<=ema)[a-zA-Z0-9]+?(?=_emaw)",lineArray[6]).group(0))
        lineArray.insert(7,re.search("(?<=_emaw)[a-zA-Z0-9]+?(?=_emas)",lineArray[7]).group(0))
        lineArray.insert(8,re.search("(?<=_emas)[a-zA-Z0-9]+?(?=_emap)",lineArray[8]).group(0))
        lineArray.insert(9,re.search("(?<=_emap)[a-zA-Z0-9]+?(?=_wabl)",lineArray[9]).group(0))
        lineArray.insert(10,re.search("(?<=_wabl)[a-zA-Z0-9]+?(?=_wablm)",lineArray[10]).group(0))
        lineArray.insert(11,re.search("(?<=_wablm)[a-zA-Z0-9]+?(?=_rawl)",lineArray[11]).group(0))
        lineArray.insert(12,re.search("(?<=_rawl)[a-zA-Z0-9]+?(?=_rawlm)",lineArray[12]).group(0))
        lineArray.insert(13,re.search("(?<=_rawlm)[a-zA-Z0-9]+?(?=_ken)",lineArray[13]).group(0))
        lineArray.insert(14,re.search("(?<=_ken)[a-zA-Z0-9]+?(?=_vddpe)",lineArray[14]).group(0))
        lineArray.insert(15,re.search("(?<=_vddpe_)[\-\..a-zA-Z0-9]+?(?=V_vddce)",lineArray[15]).group(0)+" V")
        lineArray.insert(16,re.search("(?<=_vddce_)[\-\.a-zA-Z0-9]+?(?=V_dvdd)",lineArray[16]).group(0)+" V")
        lineArray.insert(17,re.search("(?<=_dvdd_)[\-\.a-zA-Z0-9]+?(?=V_)",lineArray[17]).group(0)+" V")
        lineArray[18]=re.search("(?<=_)[\-\.a-zA-Z0-9]+?(?=ns\Z)",lineArray[18]).group(0)+" ns"

        if(lineArray[19]=="(P)"):
            lineArray.append("0")

        if self.outputForm is 3:
            lineArray=[self.fileType,self.fileTemp,self.fileIndex]+lineArray
        if self.outputForm is 2:
            lineArray=[self.fileType,self.fileTemp]+lineArray
        if self.outputForm is 1:
            lineArray=[self.fileType]+lineArray
        self.memData.append(lineArray)
    def parseVminCkb(self,line,lineArray):
        if self.lastLineSection is not "vminCkb":
            if self.fileCount is 1:
                header = ["Test Number","A/S","Arch. Type","Architecture","??","EMA#1","EMA#2","EMAW","EMAS","EMAP","WABL","WABLM","RAWL","RAWLM","KEN","VDDPE (Range)","VDDCE (Range)","DVDD (Range)","Period (Range)","Value","Shmoo Value","Number of Failed Pins","Failed Pins"]
                if self.outputForm is 3:
                    header = ["Chip Type","Chip Temp","File Index"]+header
                if self.outputForm is 2:
                    header = ["Chip Type","Chip Temp"]+header
                if self.outputForm is 1:
                    header = ["Chip Type"]+header
                self.vminCkbData.append(header)
        if re.match("\([0-9]+?,pins\),FAILED",line):
            tempList = []
            tempList.append(lineArray[0][1:])
            counter=5
            while(lineArray[counter][0]!="}"):
                if(counter==5):
                    tempList.append(lineArray[counter])
                else:
                    tempList[1]=tempList[1]+" "+lineArray[counter]
                counter+=1
            self.vminCkbData[len(self.vminCkbData)-1].extend(tempList)
            return
        if re.search("\Ashmoo_bsmin_vec",line):
            tempLen = len(self.vminCkbData)-1
            self.vminCkbData[tempLen][len(self.vminCkbData[tempLen])-2] = lineArray[1][:-1]
            return
        lineArray.insert(1,re.search("[a-zA-Z]+(?=_[a-zA-Z0-9]+\Z)",lineArray[1]).group(0))
        lineArray[2]=re.search("(?<=_)[a-zA-Z0-9]+\Z",lineArray[2]).group(0)

        if re.search("(?<=\AVmax_vec_)[a-zA-Z0-9]+?(?=_)",lineArray[3]).group(0) == "cln16ffcll":
            lineArray.insert(3,re.search("(?<=\AVmax_vec_)[a-zA-Z0-9_]+?_[a-zA-Z0-9]+?_[a-zA-Z0-9]+?_[a-zA-Z0-9]+?(?=_)",lineArray[3]).group(0))
            lineArray[4]=re.sub("\AVmax_vec_[a-zA-Z0-9_]+?_[a-zA-Z0-9]+?_[a-zA-Z0-9]+?_[a-zA-Z0-9]+?_","",lineArray[4])
        else:
            lineArray.insert(3,re.search("(?<=\AVmax_vec_)[a-zA-Z0-9]+?_[a-zA-Z0-9]+?(?=_)",lineArray[3]).group(0))
            lineArray[4]=re.sub("\AVmax_vec_[a-zA-Z0-9]+?_[a-zA-Z0-9]+?_","",lineArray[4])

        lineArray.insert(4,re.search("\A[a-zA-Z0-9_]+?(?=_ema)",lineArray[4]).group(0))
        lineArray.insert(5,re.search("(?<=ema)[a-zA-Z0-9]+?(?=_ema)",lineArray[5]).group(0))
        lineArray.insert(6,re.search("(?<=ema)[a-zA-Z0-9]+?(?=_emaw)",lineArray[6]).group(0))
        lineArray.insert(7,re.search("(?<=_emaw)[a-zA-Z0-9]+?(?=_emas)",lineArray[7]).group(0))
        lineArray.insert(8,re.search("(?<=_emas)[a-zA-Z0-9]+?(?=_emap)",lineArray[8]).group(0))
        lineArray.insert(9,re.search("(?<=_emap)[a-zA-Z0-9]+?(?=_wabl)",lineArray[9]).group(0))
        lineArray.insert(10,re.search("(?<=_wabl)[a-zA-Z0-9]+?(?=_wablm)",lineArray[10]).group(0))
        lineArray.insert(11,re.search("(?<=_wablm)[a-zA-Z0-9]+?(?=_rawl)",lineArray[11]).group(0))
        lineArray.insert(12,re.search("(?<=_rawl)[a-zA-Z0-9]+?(?=_rawlm)",lineArray[12]).group(0))
        lineArray.insert(13,re.search("(?<=_rawlm)[a-zA-Z0-9]+?(?=_ken)",lineArray[13]).group(0))
        lineArray.insert(14,re.search("(?<=_ken)[a-zA-Z0-9]+?(?=_vddpe)",lineArray[14]).group(0))
        lineArray.insert(15,re.search("(?<=_vddpe_)[\-\..a-zA-Z0-9]+?(?=V_vddce)",lineArray[15]).group(0)+" V")
        lineArray.insert(16,re.search("(?<=_vddce_)[\-\.a-zA-Z0-9]+?(?=V_dvdd)",lineArray[16]).group(0)+" V")
        lineArray.insert(17,re.search("(?<=_dvdd_)[\-\.a-zA-Z0-9]+?(?=V_)",lineArray[17]).group(0)+" V")
        lineArray[18]=re.search("(?<=_)[\-\.a-zA-Z0-9]+?(?=ns\Z)",lineArray[18]).group(0)+" ns"

        lineArray.append("")
        if(lineArray[19]=="(P)"):
            lineArray.append("0")

        if self.outputForm is 3:
            lineArray=[self.fileType,self.fileTemp,self.fileIndex]+lineArray
        if self.outputForm is 2:
            lineArray=[self.fileType,self.fileTemp]+lineArray
        if self.outputForm is 1:
            lineArray=[self.fileType]+lineArray
        self.vminCkbData.append(lineArray)
    def parseShmoo(self,line,lineArray):
        if self.lastLineSection is not "shmoo":
            if self.fileCount is 1:
                header = ["Test Number","A/S","Arch. Type","Architecture","Test Location META","??","EMA#1","EMA#2","EMAW","EMAS","EMAP","WABL","WABLM","RAWL","RAWLM","KEN","VDDPE (Range)","VDDCE (Range)","DVDD (Range)","Period (Range)","Value","Shmoo Value","Number of Failed Pins","Failed Pins"]
                if self.outputForm is 3:
                    header = ["Chip Type","Chip Temp","File Index"]+header
                if self.outputForm is 2:
                    header = ["Chip Type","Chip Temp"]+header
                if self.outputForm is 1:
                    header = ["Chip Type"]+header
                self.shmooData.append(header)
        if re.match("\([0-9]+?,pins\),FAILED",line):
            tempList = []
            tempList.append(lineArray[0][1:])
            counter=5
            while(lineArray[counter][0]!="}"):
                if(counter==5):
                    tempList.append(lineArray[counter])
                else:
                    tempList[1]=tempList[1]+" "+lineArray[counter]
                counter+=1
            self.shmooData[len(self.shmooData)-1].extend(tempList)
            return

        if re.search("\Ashmoo_bsmin_vec",line):
            self.shmooData[len(self.shmooData)-1].append(lineArray[1][:-1])
            return

        if re.search("(?<=\Ashmoo_vec_)[a-zA-Z0-9]+?(?=_)",lineArray[0]).group(0) == "cln16ffcll":
            lineArray.insert(0,re.search("(?<=\Ashmoo_vec_)[a-zA-Z0-9_]+?_[a-zA-Z0-9]+?_[a-zA-Z0-9]+?_[a-zA-Z0-9]+?(?=_)",lineArray[0]).group(0))
            lineArray[1]=re.sub("\Ashmoo_vec_[a-zA-Z0-9_]+?_[a-zA-Z0-9]+?_[a-zA-Z0-9]+?_[a-zA-Z0-9]+?_","",lineArray[1])
        else:
            lineArray.insert(0,re.search("(?<=\Ashmoo_vec_)[a-zA-Z0-9]+?_[a-zA-Z0-9]+?(?=_)",lineArray[0]).group(0))
            lineArray[1]=re.sub("\Ashmoo_vec_[a-zA-Z0-9]+?_[a-zA-Z0-9]+?_","",lineArray[1])

        lineArray.insert(1,re.search("\A[a-zA-Z0-9_]+?(?=_ema)",lineArray[1]).group(0))
        lineArray.insert(2,re.search("(?<=ema)[a-zA-Z0-9]+?(?=_ema)",lineArray[2]).group(0))
        lineArray.insert(3,re.search("(?<=ema)[a-zA-Z0-9]+?(?=_emaw)",lineArray[3]).group(0))
        lineArray.insert(4,re.search("(?<=_emaw)[a-zA-Z0-9]+?(?=_emas)",lineArray[4]).group(0))
        lineArray.insert(5,re.search("(?<=_emas)[a-zA-Z0-9]+?(?=_emap)",lineArray[5]).group(0))
        lineArray.insert(6,re.search("(?<=_emap)[a-zA-Z0-9]+?(?=_wabl)",lineArray[6]).group(0))
        lineArray.insert(7,re.search("(?<=_wabl)[a-zA-Z0-9]+?(?=_wablm)",lineArray[7]).group(0))
        lineArray.insert(8,re.search("(?<=_wablm)[a-zA-Z0-9]+?(?=_rawl)",lineArray[8]).group(0))
        lineArray.insert(9,re.search("(?<=_rawl)[a-zA-Z0-9]+?(?=_rawlm)",lineArray[9]).group(0))
        lineArray.insert(10,re.search("(?<=_rawlm)[a-zA-Z0-9]+?(?=_ken)",lineArray[10]).group(0))
        lineArray[11]=re.search("(?<=_ken)[a-zA-Z0-9]+?\Z",lineArray[11]).group(0)

        if self.outputForm is 3:
            lineArray=[self.fileType,self.fileTemp,self.fileIndex]+lineArray
        if self.outputForm is 2:
            lineArray=[self.fileType,self.fileTemp]+lineArray
        if self.outputForm is 1:
            lineArray=[self.fileType]+lineArray
        self.shmooData.append(lineArray)

    def makeDir(self,path):
        if not os.path.exists(path):
            os.makedirs(path)

    def output(self,outputForm,fileCount,fileTemp,fileIndex,fileType,inFilePath,filePath="default"):
        self.outputForm=outputForm
        self.fileCount=fileCount
        if self.outputForm is 3:
            self.fileTemp=fileTemp
            self.fileIndex=fileIndex
            self.fileType=fileType
        if self.outputForm is 2:
            self.fileTemp=fileTemp
            self.fileIndex=""
            self.fileType=fileType
        if self.outputForm is 1:
            self.fileTemp=""
            self.fileIndex=""
            self.fileType=fileType
        if self.outputForm is 0:
            self.fileTemp=""
            self.fileIndex=""
            self.fileType=""

        self.processFileLines(inFilePath)
        self.makeDir(filePath)
        writeAppend = "a"

        if self.fileCount is 1:
            writeAppend = "w"

        with open(filePath+"/unused.csv", writeAppend) as out_file1:
            #writes csv file from list
            writer = csv.writer(out_file1)
            writer.writerows(self.unusedData)
            throwawayDataSize=len(self.unusedData)
            if(throwawayDataSize>0):
                print("file \""+filePath+"\".txt has "+str(throwawayDataSize)+" unrecognized lines")
        with open(filePath+"/pins.csv", writeAppend) as out_file2:
            #writes csv file from list
            writer = csv.writer(out_file2)
            writer.writerows(self.pinsData)
        with open(filePath+"/leakage.csv", writeAppend) as out_file3:
            #writes csv file from list
            writer = csv.writer(out_file3)
            writer.writerows(self.leakageData)
        with open(filePath+"/vminStd.csv", writeAppend) as out_file4:
            #writes csv file from list
            writer = csv.writer(out_file4)
            writer.writerows(self.vminStdData)
        with open(filePath+"/mem.csv", writeAppend) as out_file5:
            #writes csv file from list
            writer = csv.writer(out_file5)
            writer.writerows(self.memData)
        with open(filePath+"/vminCkb.csv", writeAppend) as out_file6:
            #writes csv file from list
            writer = csv.writer(out_file6)
            writer.writerows(self.vminCkbData)
        with open(filePath+"/shmoo.csv", writeAppend) as out_file7:
            #writes csv file from list
            writer = csv.writer(out_file7)
            writer.writerows(self.shmooData)
        with open(filePath+"/meta.csv", writeAppend) as out_file7:
            #writes csv file from list
            writer = csv.writer(out_file7)
            writer.writerows(self.metaData)

        #--------don't need fullOutput-------
        #with open(filePath+"/fullOutput.csv", writeAppend) as out_file8:
            #writer = csv.writer(out_file8)
            #writer.writerows(self.pinsData)
            #writer.writerows(self.leakageData)
            #writer.writerows(self.vminStdData)
            #writer.writerows(self.memData)
            #writer.writerows(self.vminCkbData)
            #writer.writerows(self.shmooData)
            #writer.writerows(self.metaData)
