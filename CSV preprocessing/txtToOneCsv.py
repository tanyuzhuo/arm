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
            elif re.search("\A[0-9]+,tb_vmin_ckb",line) or (re.match("\([0-9]+?,pins\),FAILED",line) and self.lastLineSection=="vminCkb") or re.search("\Ashmoo_bsmin_vec(?!_stdcell_)",line):
                thisSection="vminCkb"
                self.parseVminCkb(line,lineArray)
            else:
                if(not re.match("TstNum,Pin,Chn",line)):
                    thisSection=""
                    self.unusedData.append(lineArray)
            self.lastLineSection=thisSection

    def parsePin(self,line,lineArray):
        if(self.lastLineSection!="pins"):
            self.pinsData.append(["TstNum","Pin","Chn","Pin Name","Test Block","Test Name","Force Value","Low Limit","Test Value","P/F","High Limit"])
        units=["uA","mV","mA","uA","V"]
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

        self.pinsData.append(lineArray)
    def parseLeakage(self,line,lineArray):
        if self.lastLineSection != "leakage":
            self.leakageData.append(["Leakage Test Type","Pin","VDD (Range)","DVDD (Range)","Period (Range)","Value"])

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

        self.leakageData.append(lineArray)
    def parseVminStd(self,line,lineArray):
        if self.lastLineSection is not "vminStd":
            self.vminStdData.append(["Test Number","Test Item","Library #1","Library #2","Library #3","VDD (Range)","DVDD (Range)","Period (Range)","Result","Shmoo Value"])

        if re.search("\Ashmoo_bsmin_vec_stdcell_",line):
            self.vminStdData[len(self.vminStdData)-1].insert(20,lineArray[1])
            return

        if lineArray[1]=="tb_sc_yd_vmin_shm":
            lineArray.pop(1)
        else:
            raise AttributeError("standard cell format not correct")

        if lineArray[1][:17]!="func_vec_stdcell_":
            raise AttributeError("standard cell format not correct")

        lineArray.insert(1,re.search("(?<=stdcell_)[a-z0-9]+(?=_)",lineArray[1]).group(0))
        lineArray[2]=re.sub("[a-zA-Z0-9_]+(stdcell_)[a-zA-Z0-9]+_","",lineArray[2])

        lineArray.insert(2,re.search("\A[a-z]+(?=_)",lineArray[2]).group(0))
        lineArray[3]=re.sub("\A[a-z]+_","",lineArray[3])

        lineArray.insert(3,re.search("\A[a-z0-9]+(?=_)",lineArray[3]).group(0))
        lineArray.insert(4,re.search("(?<=_)[a-z0-9]+(?=_pattern)",lineArray[4]).group(0))

        lineArray.insert(5,re.search("(?<=vdd_)[\-0-9\.]+(?=V_dvdd)",lineArray[5]).group(0)+" V")
        lineArray.insert(6,re.search("(?<=dvdd_)[\-0-9\.]+(?=V_)",lineArray[6]).group(0)+" V")

        lineArray[7]=re.search("(?<=_)[-0-9.]+(?=nS\Z)",lineArray[7]).group(0)+" ns"

        self.vminStdData.append(lineArray)
    def parseMem(self,line,lineArray):
        if self.lastLineSection is not "mem":
            self.memData.append(["Test Number","A/S","R/F","Architecture","Test Location META","??","EMA#1","EMA#2","EMAW","EMAS","EMAP","WABL","WABLM","RAWL","RAWLM","KEN","VDDPE (Range)","VDDCE (Range)","DVDD (Range)","Period (Range)","Value","Number of Failed Pins","Failed Pins"])
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
            lineArray.insert(3,re.search("(?<=\Afunc_vec_)[a-zA-Z0-9_]+?(?=_w)",lineArray[3]).group(0))
            lineArray[4]=re.sub("\Afunc_vec_[a-zA-Z0-9_]+?(?=w)","",lineArray[4])
        else:
            lineArray.insert(3,re.search("(?<=\Afunc_vec_)[a-zA-Z0-9]+?(?=_)",lineArray[3]).group(0))
            lineArray[4]=re.sub("\Afunc_vec_[a-zA-Z0-9]+?_","",lineArray[4])

        lineArray.insert(4,re.match("[a-zA-Z0-9]+?(?=_)",lineArray[4]).group(0))
        lineArray[5]=re.sub("\A[a-zA-Z0-9]+?_","",lineArray[5])

        lineArray.insert(5,re.search("\A[a-zA-Z0-9_]+?(?=_ema)",lineArray[5]).group(0))
        lineArray.insert(6,re.search("(?<=ema)[a-zA-Z0-9]+?(?=_ema)",lineArray[6]).group(0))
        lineArray.insert(7,re.search("(?<=ema)[a-zA-Z0-9]+?(?=_emaw)",lineArray[7]).group(0))
        lineArray.insert(8,re.search("(?<=_emaw)[a-zA-Z0-9]+?(?=_emas)",lineArray[8]).group(0))
        lineArray.insert(9,re.search("(?<=_emas)[a-zA-Z0-9]+?(?=_emap)",lineArray[9]).group(0))
        lineArray.insert(10,re.search("(?<=_emap)[a-zA-Z0-9]+?(?=_wabl)",lineArray[10]).group(0))
        lineArray.insert(11,re.search("(?<=_wabl)[a-zA-Z0-9]+?(?=_wablm)",lineArray[11]).group(0))
        lineArray.insert(12,re.search("(?<=_wablm)[a-zA-Z0-9]+?(?=_rawl)",lineArray[12]).group(0))
        lineArray.insert(13,re.search("(?<=_rawl)[a-zA-Z0-9]+?(?=_rawlm)",lineArray[13]).group(0))
        lineArray.insert(14,re.search("(?<=_rawlm)[a-zA-Z0-9]+?(?=_ken)",lineArray[14]).group(0))
        lineArray.insert(15,re.search("(?<=_ken)[a-zA-Z0-9]+?(?=_vddpe)",lineArray[15]).group(0))
        lineArray.insert(16,re.search("(?<=_vddpe_)[\-\..a-zA-Z0-9]+?(?=V_vddce)",lineArray[16]).group(0)+" V")
        lineArray.insert(17,re.search("(?<=_vddce_)[\-\.a-zA-Z0-9]+?(?=V_dvdd)",lineArray[17]).group(0)+" V")
        lineArray.insert(18,re.search("(?<=_dvdd_)[\-\.a-zA-Z0-9]+?(?=V_)",lineArray[18]).group(0)+" V")
        lineArray[19]=re.search("(?<=_)[\-\.a-zA-Z0-9]+?(?=ns\Z)",lineArray[19]).group(0)+" ns"

        if(lineArray[20]=="(P)"):
            lineArray.append("0")

        self.memData.append(lineArray)
    def parseVminCkb(self,line,lineArray):
        if self.lastLineSection is not "vminCkb":
            self.vminCkbData.append(["Test Number","A/S","Arch. Type","Architecture","Test Location META","??","EMA#1","EMA#2","EMAW","EMAS","EMAP","WABL","WABLM","RAWL","RAWLM","KEN","VDDPE (Range)","VDDCE (Range)","DVDD (Range)","Period (Range)","Value","Shmoo Value","Number of Failed Pins","Failed Pins"])
        if re.search("\Ashmoo_bsmin_vec",line):
            self.vminCkbData[len(self.vminCkbData)-1].insert(21,lineArray[1])
            return
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
            self.vminStdData[len(self.vminStdData)-1].append(lineArray[1])
            self.vminStdData.append(lineArray)
            return

        lineArray.insert(1,re.search("[a-zA-Z]+(?=_[a-zA-Z0-9]+\Z)",lineArray[1]).group(0))
        lineArray[2]=re.search("(?<=_)[a-zA-Z0-9]+\Z",lineArray[2]).group(0)

        if re.search("(?<=\AVmax_vec_)[a-zA-Z0-9]+?(?=_)",lineArray[3]).group(0) == "cln16ffcll":
            lineArray.insert(3,re.search("(?<=\AVmax_vec_)[a-zA-Z0-9_]+?(?=_w)",lineArray[3]).group(0))
            lineArray[4]=re.sub("\AVmax_vec_[a-zA-Z0-9_]+?(?=w)","",lineArray[4])
        else:
            lineArray.insert(3,re.search("(?<=\AVmax_vec_)[a-zA-Z0-9]+?(?=_)",lineArray[3]).group(0))
            lineArray[4]=re.sub("\AVmax_vec_[a-zA-Z0-9]+?_","",lineArray[4])

        lineArray.insert(4,re.match("[a-zA-Z0-9]+?(?=_)",lineArray[4]).group(0))
        lineArray[5]=re.sub("\A[a-zA-Z0-9]+?_","",lineArray[5])

        lineArray.insert(5,re.search("\A[a-zA-Z0-9_]+?(?=_ema)",lineArray[5]).group(0))
        lineArray.insert(6,re.search("(?<=ema)[a-zA-Z0-9]+?(?=_ema)",lineArray[6]).group(0))
        lineArray.insert(7,re.search("(?<=ema)[a-zA-Z0-9]+?(?=_emaw)",lineArray[7]).group(0))
        lineArray.insert(8,re.search("(?<=_emaw)[a-zA-Z0-9]+?(?=_emas)",lineArray[8]).group(0))
        lineArray.insert(9,re.search("(?<=_emas)[a-zA-Z0-9]+?(?=_emap)",lineArray[9]).group(0))
        lineArray.insert(10,re.search("(?<=_emap)[a-zA-Z0-9]+?(?=_wabl)",lineArray[10]).group(0))
        lineArray.insert(11,re.search("(?<=_wabl)[a-zA-Z0-9]+?(?=_wablm)",lineArray[11]).group(0))
        lineArray.insert(12,re.search("(?<=_wablm)[a-zA-Z0-9]+?(?=_rawl)",lineArray[12]).group(0))
        lineArray.insert(13,re.search("(?<=_rawl)[a-zA-Z0-9]+?(?=_rawlm)",lineArray[13]).group(0))
        lineArray.insert(14,re.search("(?<=_rawlm)[a-zA-Z0-9]+?(?=_ken)",lineArray[14]).group(0))
        lineArray.insert(15,re.search("(?<=_ken)[a-zA-Z0-9]+?(?=_vddpe)",lineArray[15]).group(0))
        lineArray.insert(16,re.search("(?<=_vddpe_)[\-\..a-zA-Z0-9]+?(?=V_vddce)",lineArray[16]).group(0)+" V")
        lineArray.insert(17,re.search("(?<=_vddce_)[\-\.a-zA-Z0-9]+?(?=V_dvdd)",lineArray[17]).group(0)+" V")
        lineArray.insert(18,re.search("(?<=_dvdd_)[\-\.a-zA-Z0-9]+?(?=V_)",lineArray[18]).group(0)+" V")
        lineArray[19]=re.search("(?<=_)[\-\.a-zA-Z0-9]+?(?=ns\Z)",lineArray[19]).group(0)+" ns"

        if(lineArray[20]=="(P)"):
            lineArray.append("0")

        self.vminCkbData.append(lineArray)




    def makeDir(self,path):
        if not os.path.exists(path):
            os.makedirs(path)

    def output(self,inFilePath="Temp Folder/101_TT_25C.txt",filePath="this file"):
        #opens output file
        self.processFileLines(inFilePath)
        self.makeDir(filePath)
        with open(filePath+"/unused.csv", "w") as out_file1:
            #writes csv file from list
            writer = csv.writer(out_file1)
            writer.writerows(self.unusedData)
            throwawayDataSize=len(self.unusedData)
            if(throwawayDataSize>0):
                print("file \""+filePath+"\".txt has "+str(throwawayDataSize)+" unrecognized lines")
        with open(filePath+"/pins.csv", "w") as out_file2:
            #writes csv file from list
            writer = csv.writer(out_file2)
            writer.writerows(self.pinsData)
        with open(filePath+"/leakage.csv", "w") as out_file3:
            #writes csv file from list
            writer = csv.writer(out_file3)
            writer.writerows(self.leakageData)
        with open(filePath+"/vminStd.csv", "w") as out_file4:
            #writes csv file from list
            writer = csv.writer(out_file4)
            writer.writerows(self.vminStdData)
        with open(filePath+"/mem.csv", "w") as out_file5:
            #writes csv file from list
            writer = csv.writer(out_file5)
            writer.writerows(self.memData)
        with open(filePath+"/vminCkb.csv", "w") as out_file6:
            #writes csv file from list
            writer = csv.writer(out_file6)
            writer.writerows(self.vminCkbData)
        with open(filePath+"/meta.csv", "w") as out_file7:
            #writes csv file from list
            writer = csv.writer(out_file7)
            writer.writerows(self.metaData)
        with open(filePath+"/fullOutput.csv", "w") as out_file8:
            writer = csv.writer(out_file8)
            writer.writerows(self.pinsData)
            writer.writerows(self.leakageData)
            writer.writerows(self.vminStdData)
            writer.writerows(self.memData)
            writer.writerows(self.vminCkbData)
            writer.writerows(self.metaData)



#startTime = datetime.datetime.now()
#txtToCsv = txtToCsv()
#txtToCsv.processFileLines("Temp Folder/101_TT_25C.txt")
#txtToCsv.output()
#endTime = datetime.datetime.now()
#print(endTime-startTime)
