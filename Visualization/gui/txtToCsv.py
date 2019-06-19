import csv
import re
import os
import sys
import datetime

#class to help encapsulate
class txtToCsv:
    #function to send all file lines off to process
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
        #strips blank lines
        line = re.sub("\A\s+\Z", "", line)
        #subs space to commas and then splits into an arrays based on commas
        line = re.sub("\s+", ",", line)
        lineArray = line.split(",")

        #checks not an empty line if it is ignore
        if not re.search("^$",line):
            #inits a variable that signals what catagory it is designated
            thisSection=""
            #checks meta data so it can put it in the meta file
            if re.match("dut1",line) or re.match("TestStarted",line) or re.match("SITE",line):
                thisSection="meta"
                self.postMetaFlag+=1
                self.metaData.append(lineArray)
            #once end of file is triggered all lines put in meta file
            elif self.postMetaFlag>2:
                thisSection="meta"
                self.metaData.append(lineArray)

            #triggered for the pins data and puts in that function and data
            elif re.match("[0-9]+,[A-Z0-9]+,[a-z0-9_]+,[A-Z0-9_]+,[a-z_]+,[a-zA-Z]+,",line):
                thisSection="pins"
                self.parsePin(line,lineArray)

            #triggered for the leakage data and puts in that function and data
            elif re.search("\Atb_leakage_",line):
                thisSection="leakage"
                self.parseLeakage(line,lineArray)

            #triggered for the yield standard cell data and puts in that function and data
            elif re.search("\A[0-9]+,tb_sc_yd_vmin_shm",line) or re.search("\Ashmoo_bsmin_vec_stdcell_",line):
                thisSection="vminStd"
                self.parseVminStd(line,lineArray)

            #triggered for the mem yld data and puts in that function and data
            elif re.match("[0-9]+?,tb_mem_yd_ckb",line) or (re.match("\([0-9]+?,pins\),FAILED",line) and self.lastLineSection=="mem"):
                thisSection="mem"
                self.parseMem(line,lineArray)

            #triggered for the mem vmin and puts in that function and data
            #NOTE REFFERED TO AS VMIN CKB AS  WAS UNSURE AT THE TIME WHAT IT WAS FOR
            elif re.search("\A[0-9]+,tb_vmin_ckb",line) or (re.match("\([0-9]+?,pins\),FAILED",line) and self.lastLineSection=="vminCkb") or (re.search("\Ashmoo_bsmin_vec(?!_stdcell_)",line) and self.lastLineSection=="vminCkb"):
                thisSection="vminCkb"
                self.parseVminCkb(line,lineArray)

            #triggered for the shmoo data and puts in that function and data (NOTE this didnt appear often)
            elif re.match("shmoo_vec_",line) or (re.match("shmoo_bsmin_vec_",line) and self.lastLineSection=="shmoo"):
                thisSection="shmoo"
                self.parseShmoo(line,lineArray)

            #anything that isnt the first line of pin data gets known as unused puts in file and calls function
            else:
                if(not re.match("TstNum,Pin,Chn",line)):
                    thisSection=""
                    self.unusedData.append(lineArray)
            #shifts into last section buffer variable
            self.lastLineSection=thisSection

    #pin function to parse pin Data
    def parsePin(self,line,lineArray):
        #if its the first line of pins it adds the header
        if(self.lastLineSection!="pins"):
            #if its a new  file and not appened one
            if self.fileCount is 1:
                #changes header depending on the output form
                header = ["TstNum","Pin","Chn","Pin Name","Test Block","Test Name","Force Value","Low Limit","Test Value","P/F","High Limit"]
                if self.outputForm is 3:
                    header = ["Chip Type","Chip Temp","File Index"]+header
                if self.outputForm is 2:
                    header = ["Chip Type","Chip Temp"]+header
                if self.outputForm is 1:
                    header = ["Chip Type"]+header
                self.pinsData.append(header)
        units=["uA","mV","mA","uA","pV","V"]
        #changes test name as it has a space which can cause issues because of the spaces
        if(lineArray[5]=="Cont"):
            lineArray[5]="Cont N"
            lineArray.pop(6)

        #if theres no fail add in a pass
        if(not lineArray[12]=="(F)"):
            lineArray.insert(12,"(P)")

        #attempts to put the number and unit in one cell in a variety of formats
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

        #appends a few cells to start depending on output form
        if self.outputForm is 3:
            lineArray=[self.fileType,self.fileTemp,self.fileIndex]+lineArray
        if self.outputForm is 2:
            lineArray=[self.fileType,self.fileTemp]+lineArray
        if self.outputForm is 1:
            lineArray=[self.fileType]+lineArray
        #appends to final array
        self.pinsData.append(lineArray)

    #function to parse a line of leakage data
    def parseLeakage(self,line,lineArray):
        #checks if first line so it can append the header line
        if self.lastLineSection != "leakage":
            if self.fileCount is 1:
                #different header format for different output format types
                header = ["Leakage Test Type","Pin","VDD (Range)","DVDD (Range)","Period (Range)","Value"]
                if self.outputForm is 3:
                    header = ["Chip Type","Chip Temp","File Index"]+header
                if self.outputForm is 2:
                    header = ["Chip Type","Chip Temp"]+header
                if self.outputForm is 1:
                    header = ["Chip Type"]+header
                self.leakageData.append(header)

        #checks high or low leakage type
        if lineArray[0] == "tb_leakage_high":
            lineArray[0]="high"
        elif lineArray[0] == "tb_leakage_low":
            lineArray[0]="low"

        #matches cell formats and inserts them in cell layout
        lineArray.insert(1,re.match("[a-zA-Z0-9_]+(?=_leakage)",lineArray[1]).group(0))
        lineArray.insert(2,re.search("(?<=vdd_)[\-0-9\.]+(?=V_dvdd)",lineArray[2]).group(0)+" V")
        lineArray.insert(3,re.search("(?<=dvdd_)[\-0-9\.]+(?=V_)",lineArray[3]).group(0)+" V")
        lineArray[4]=re.search("(?<=_)[-0-9.]+(?=ns\Z)",lineArray[4]).group(0)+" ns"

        #combines cell and number
        if(lineArray[6]=="uA"):
            lineArray[5]+=" uA"
            lineArray.pop(6)

        #adds cells to start of each line depending on output form
        if self.outputForm is 3:
            lineArray=[self.fileType,self.fileTemp,self.fileIndex]+lineArray
        if self.outputForm is 2:
            lineArray=[self.fileType,self.fileTemp]+lineArray
        if self.outputForm is 1:
            lineArray=[self.fileType]+lineArray
        #appends to data array
        self.leakageData.append(lineArray)

    #a function to parse vmin data for standard cell data
    def parseVminStd(self,line,lineArray):
        #checks if first line of data to add header
        if self.lastLineSection is not "vminStd":
            if self.fileCount is 1:
                header = ["Test Number","Test Item","VDD (Range)","DVDD (Range)","Period (Range)","Result","Shmoo Value"]
                #custom header for different output form
                if self.outputForm is 3:
                    header = ["Chip Type","Chip Temp","File Index"]+header
                if self.outputForm is 2:
                    header = ["Chip Type","Chip Temp"]+header
                if self.outputForm is 1:
                    header = ["Chip Type"]+header
                self.vminStdData.append(header)

        #if its a shmoo line after vmin std cell data append it as a cell and leave the function
        if re.search("\Ashmoo_bsmin_vec_stdcell_",line):
            self.vminStdData[len(self.vminStdData)-1].append(lineArray[1][:-1])
            return

        #always remove the meta data of "tb_sc_yd_vmin_shm"
        if lineArray[1]=="tb_sc_yd_vmin_shm":
            lineArray.pop(1)

        #insert library in next cell
        lineArray.insert(1,re.search("(?<=stdcell_)[a-z0-9]+?_[a-z0-9]+?_[a-z0-9]+?_[a-z0-9]+?(?=_)",lineArray[1]).group(0))

        #all range info then matched for format and appened on
        lineArray.insert(2,re.search("(?<=vdd_)[\-0-9\.]+(?=V_dvdd)",lineArray[2]).group(0))
        lineArray.insert(3,re.search("(?<=dvdd_)[\-0-9\.]+(?=V_)",lineArray[3]).group(0)+" V")
        lineArray[4]=re.search("(?<=_)[-0-9.]+(?=nS\Z)",lineArray[4]).group(0)+" ns"

        #inserts different cells on the beginning depending on output form
        if self.outputForm is 3:
            lineArray=[self.fileType,self.fileTemp,self.fileIndex]+lineArray
        if self.outputForm is 2:
            lineArray=[self.fileType,self.fileTemp]+lineArray
        if self.outputForm is 1:
            lineArray=[self.fileType]+lineArray
        #append on whole data array
        self.vminStdData.append(lineArray)

    #function for parseing memory yield data
    def parseMem(self,line,lineArray):
        #if first line then adds a header
        if self.lastLineSection is not "mem":
            if self.fileCount is 1:
                header = ["Test Number","A/S","R/F","Architecture","??","EMA#1","EMA#2","EMAW","EMAS","EMAP","WABL","WABLM","RAWL","RAWLM","KEN","VDDPE (Range)","VDDCE (Range)","DVDD (Range)","Period (Range)","Value","Number of Failed Pins","Failed Pins"]
                #adds different cells for different output form
                if self.outputForm is 3:
                    header = ["Chip Type","Chip Temp","File Index"]+header
                if self.outputForm is 2:
                    header = ["Chip Type","Chip Temp"]+header
                if self.outputForm is 1:
                    header = ["Chip Type"]+header
                self.memData.append(header)

        #if any pins have failed append them at the end
        if re.match("\([0-9]+?,pins\),FAILED",line):
            tempList = []
            tempList.append(lineArray[0][1:])
            counter=5
            #while over all different pins
            while(lineArray[counter][0]!="}"):
                if(counter==5):
                    tempList.append(lineArray[counter])
                else:
                    tempList[1]=tempList[1]+" "+lineArray[counter]
                counter+=1
            self.memData[len(self.memData)-1].extend(tempList)
            return

        #seperate data and appened into individual cells
        lineArray.insert(1,re.search("[a-zA-Z]+(?=_[A-Z]\Z)",lineArray[1]).group(0))
        lineArray[2]=re.search("(?<=_)[A-Z]\Z",lineArray[2]).group(0)

        #if its in cln16ffcll it gets its own format
        #NOTE THIS IS UNKNOWN SO FORMAT FOR cln16ffcll WAS ASSUMED
        if re.search("(?<=\Afunc_vec_)[a-zA-Z0-9]+?(?=_)",lineArray[3]).group(0) == "cln16ffcll":
            lineArray.insert(3,re.search("(?<=\Afunc_vec_)[a-zA-Z0-9_]+?_[a-zA-Z0-9]+?_[a-zA-Z0-9]+?_[a-zA-Z0-9]+?(?=_)",lineArray[3]).group(0))
            lineArray[4]=re.sub("\Afunc_vec_[a-zA-Z0-9_]+?_[a-zA-Z0-9]+?_[a-zA-Z0-9]+?_[a-zA-Z0-9]+?_","",lineArray[4])
        else:
            lineArray.insert(3,re.search("(?<=\Afunc_vec_)[a-zA-Z0-9]+?_[a-zA-Z0-9]+?(?=_)",lineArray[3]).group(0))
            lineArray[4]=re.sub("\Afunc_vec_[a-zA-Z0-9]+?_[a-zA-Z0-9]+?_","",lineArray[4])

        #continues seperating data into distinct cells
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
        lineArray.insert(15,re.search("(?<=_vddpe_)[\-\..a-zA-Z0-9]+?(?=V_vddce)",lineArray[15]).group(0))
        lineArray.insert(16,re.search("(?<=_vddce_)[\-\.a-zA-Z0-9]+?(?=V_dvdd)",lineArray[16]).group(0))
        lineArray.insert(17,re.search("(?<=_dvdd_)[\-\.a-zA-Z0-9]+?(?=V_)",lineArray[17]).group(0)+" V")
        lineArray[18]=re.search("(?<=_)[\-\.a-zA-Z0-9]+?(?=ns\Z)",lineArray[18]).group(0)+" ns"
        #if it passed append that 0 cells failed
        if(lineArray[19]=="(P)"):
            lineArray.append("0")

        #add different beginnging cells depending on output form
        if self.outputForm is 3:
            lineArray=[self.fileType,self.fileTemp,self.fileIndex]+lineArray
        if self.outputForm is 2:
            lineArray=[self.fileType,self.fileTemp]+lineArray
        if self.outputForm is 1:
            lineArray=[self.fileType]+lineArray
        #append onto whole data array
        self.memData.append(lineArray)

    #function for processing mem vmin data (basically same as above one with shmoo values)
    def parseVminCkb(self,line,lineArray):
        #adds header if first line of data
        if self.lastLineSection is not "vminCkb":
            if self.fileCount is 1:
                header = ["Test Number","A/S","Arch. Type","Architecture","??","EMA#1","EMA#2","EMAW","EMAS","EMAP","WABL","WABLM","RAWL","RAWLM","KEN","VDDPE (Range)","VDDCE (Range)","DVDD (Range)","Period (Range)","Value","Shmoo Value","Number of Failed Pins","Failed Pins"]
                #different format for different output form
                if self.outputForm is 3:
                    header = ["Chip Type","Chip Temp","File Index"]+header
                if self.outputForm is 2:
                    header = ["Chip Type","Chip Temp"]+header
                if self.outputForm is 1:
                    header = ["Chip Type"]+header
                self.vminCkbData.append(header)

        #if failed appends that on and exits function
        if re.match("\([0-9]+?,pins\),FAILED",line):
            tempList = []
            tempList.append(lineArray[0][1:])
            counter=5
            #runs a while loop over each pin
            while(lineArray[counter][0]!="}"):
                if(counter==5):
                    tempList.append(lineArray[counter])
                else:
                    tempList[1]=tempList[1]+" "+lineArray[counter]
                counter+=1
            self.vminCkbData[len(self.vminCkbData)-1].extend(tempList)
            return

        #if a shmoo line appends the value at the end of the line and exits function
        if re.search("\Ashmoo_bsmin_vec",line):
            tempLen = len(self.vminCkbData)-1
            self.vminCkbData[tempLen][len(self.vminCkbData[tempLen])-2] = lineArray[1][:-1]
            return

        #checks cell info and adds into individual cell
        lineArray.insert(1,re.search("[a-zA-Z]+(?=_[a-zA-Z0-9]+\Z)",lineArray[1]).group(0))
        lineArray[2]=re.search("(?<=_)[a-zA-Z0-9]+\Z",lineArray[2]).group(0)

        #if its in cln16ffcll it gets its own format
        #NOTE THIS IS UNKNOWN SO FORMAT FOR cln16ffcll WAS ASSUMED
        if re.search("(?<=\AVmax_vec_)[a-zA-Z0-9]+?(?=_)",lineArray[3]).group(0) == "cln16ffcll":
            lineArray.insert(3,re.search("(?<=\AVmax_vec_)[a-zA-Z0-9_]+?_[a-zA-Z0-9]+?_[a-zA-Z0-9]+?_[a-zA-Z0-9]+?(?=_)",lineArray[3]).group(0))
            lineArray[4]=re.sub("\AVmax_vec_[a-zA-Z0-9_]+?_[a-zA-Z0-9]+?_[a-zA-Z0-9]+?_[a-zA-Z0-9]+?_","",lineArray[4])
        else:
            lineArray.insert(3,re.search("(?<=\AVmax_vec_)[a-zA-Z0-9]+?_[a-zA-Z0-9]+?(?=_)",lineArray[3]).group(0))
            lineArray[4]=re.sub("\AVmax_vec_[a-zA-Z0-9]+?_[a-zA-Z0-9]+?_","",lineArray[4])

        #continues seperating data into distinct cells
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
        lineArray.insert(15,re.search("(?<=_vddpe_)[\-\..a-zA-Z0-9]+?(?=V_vddce)",lineArray[15]).group(0))
        lineArray.insert(16,re.search("(?<=_vddce_)[\-\.a-zA-Z0-9]+?(?=V_dvdd)",lineArray[16]).group(0))
        lineArray.insert(17,re.search("(?<=_dvdd_)[\-\.a-zA-Z0-9]+?(?=V_)",lineArray[17]).group(0)+" V")
        lineArray[18]=re.search("(?<=_)[\-\.a-zA-Z0-9]+?(?=ns\Z)",lineArray[18]).group(0)+" ns"
        lineArray.append("")
        #if it passed append that 0 cells failed
        if(lineArray[19]=="(P)"):
            lineArray.append("0")

        #add different beginnging cells depending on output form
        if self.outputForm is 3:
            lineArray=[self.fileType,self.fileTemp,self.fileIndex]+lineArray
        if self.outputForm is 2:
            lineArray=[self.fileType,self.fileTemp]+lineArray
        if self.outputForm is 1:
            lineArray=[self.fileType]+lineArray
        #append onto whole data array
        self.vminCkbData.append(lineArray)

    #parses shmoo only line of data
    def parseShmoo(self,line,lineArray):
        #if first line append header line
        if self.lastLineSection is not "shmoo":
            if self.fileCount is 1:
                header = ["Test Number","A/S","Arch. Type","Architecture","Test Location META","??","EMA#1","EMA#2","EMAW","EMAS","EMAP","WABL","WABLM","RAWL","RAWLM","KEN","VDDPE (Range)","VDDCE (Range)","DVDD (Range)","Period (Range)","Value","Shmoo Value","Number of Failed Pins","Failed Pins"]
                #different for different output forms
                if self.outputForm is 3:
                    header = ["Chip Type","Chip Temp","File Index"]+header
                if self.outputForm is 2:
                    header = ["Chip Type","Chip Temp"]+header
                if self.outputForm is 1:
                    header = ["Chip Type"]+header
                self.shmooData.append(header)

        #if any pins fail appeneds that
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

        #appends data into single cells
        if re.search("\Ashmoo_bsmin_vec",line):
            self.shmooData[len(self.shmooData)-1].append(lineArray[1][:-1])
            return

        #if its in cln16ffcll it gets its own format
        #NOTE THIS IS UNKNOWN SO FORMAT FOR cln16ffcll WAS ASSUMED
        if re.search("(?<=\Ashmoo_vec_)[a-zA-Z0-9]+?(?=_)",lineArray[0]).group(0) == "cln16ffcll":
            lineArray.insert(0,re.search("(?<=\Ashmoo_vec_)[a-zA-Z0-9_]+?_[a-zA-Z0-9]+?_[a-zA-Z0-9]+?_[a-zA-Z0-9]+?(?=_)",lineArray[0]).group(0))
            lineArray[1]=re.sub("\Ashmoo_vec_[a-zA-Z0-9_]+?_[a-zA-Z0-9]+?_[a-zA-Z0-9]+?_[a-zA-Z0-9]+?_","",lineArray[1])
        else:
            lineArray.insert(0,re.search("(?<=\Ashmoo_vec_)[a-zA-Z0-9]+?_[a-zA-Z0-9]+?(?=_)",lineArray[0]).group(0))
            lineArray[1]=re.sub("\Ashmoo_vec_[a-zA-Z0-9]+?_[a-zA-Z0-9]+?_","",lineArray[1])

        #continues seperating data into distinct cells
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

        #add different beginnging cells depending on output form
        if self.outputForm is 3:
            lineArray=[self.fileType,self.fileTemp,self.fileIndex]+lineArray
        if self.outputForm is 2:
            lineArray=[self.fileType,self.fileTemp]+lineArray
        if self.outputForm is 1:
            lineArray=[self.fileType]+lineArray
        #append onto whole data array
        self.shmooData.append(lineArray)

    #a function to make a directory if it doesn't exist
    def makeDir(self,path):
        if not os.path.exists(path):
            os.makedirs(path)

    #the function called to process a files
    #file count- indicates what number file it is in direc EG if one should create new file not appends
    #file temp, file index, file type- all meta info for file that gets appened
    #inFilePath- is file location to read
    #filePath- is file location to write
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

        #processes all lines into their distinct arrays
        self.processFileLines(inFilePath)
        #creates the output array
        self.makeDir(filePath)
        writeAppend = "a"

        #if writing not appeneding (if first file) changes it here
        if self.fileCount is 1:
            writeAppend = "w"

        #writes all data to the unused file and throws exception if there are lines the process doesn't understand
        with open(filePath+"/unused.csv", writeAppend) as out_file1:
            #writes csv file from list
            writer = csv.writer(out_file1)
            writer.writerows(self.unusedData)
            throwawayDataSize=len(self.unusedData)
            if(throwawayDataSize>0):
                print("file \""+filePath+"\".txt has "+str(throwawayDataSize)+" unrecognized lines")

        #writes data for pin data
        with open(filePath+"/pins.csv", writeAppend) as out_file2:
            #writes csv file from list
            writer = csv.writer(out_file2)
            writer.writerows(self.pinsData)

        #writes data for leakage data
        with open(filePath+"/leakage.csv", writeAppend) as out_file3:
            #writes csv file from list
            writer = csv.writer(out_file3)
            writer.writerows(self.leakageData)

        #writes data for vmin standard cell data
        with open(filePath+"/vminStd.csv", writeAppend) as out_file4:
            #writes csv file from list
            writer = csv.writer(out_file4)
            writer.writerows(self.vminStdData)

        #writes data for mem yield data
        with open(filePath+"/mem.csv", writeAppend) as out_file5:
            #writes csv file from list
            writer = csv.writer(out_file5)
            writer.writerows(self.memData)

        #writes data for mem vmin data
        with open(filePath+"/vminCkb.csv", writeAppend) as out_file6:
            #writes csv file from list
            writer = csv.writer(out_file6)
            writer.writerows(self.vminCkbData)

        #writes data for shmoo only data
        with open(filePath+"/shmoo.csv", writeAppend) as out_file7:
            #writes csv file from list
            writer = csv.writer(out_file7)
            writer.writerows(self.shmooData)

        #writes all the extra meta data
        with open(filePath+"/meta.csv", writeAppend) as out_file7:
            #writes csv file from list
            writer = csv.writer(out_file7)
            writer.writerows(self.metaData)

#if you want a file with all lines uncomment below
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
