import csv
import re
import os
import sys

class test1_:
    #sanitizes input
    def sanitize(self, lineTemp, lineNo):
        lineTemp = re.sub("TestValue", "TestValue,P/F", lineTemp)

        #removes - < : from file
        lineTemp = re.sub("[-]+", "", lineTemp)
        lineTemp = re.sub("<", "", lineTemp)
        lineTemp = re.sub(":", "", lineTemp)

        #appends units on numbers and removes whitespace between
        lineTemp = re.sub("[\s]+(mV)[\s]", "_mV ", lineTemp)
        lineTemp = re.sub("[\s]+(mA)[\s]", "_mA ", lineTemp)
        lineTemp = re.sub("[\s]+(mS)[\s]", "_mS ", lineTemp)
        lineTemp = re.sub("[\s]+(V)[\s]", "_V ", lineTemp)
        lineTemp = re.sub("[\s]+(uA)[\s]", "_uA ", lineTemp)

        #edge cases
        lineTemp = re.sub("[\s](Cont)[\s](N)[\s]", " Cont_N ", lineTemp)
        lineTemp = re.sub("[\s](TOTAL)[\s]+(TEST)[\s]+(TIME)", " TOTAL_TEST_TIME ", lineTemp)

        #same as above but checks in case it doesnt end in whitespace
        lineTemp = re.sub("[\s]+(mV)(\Z)", "_mV", lineTemp)
        lineTemp = re.sub("[\s]+(mS)(\Z)", "_mS", lineTemp)
        lineTemp = re.sub("[\s]+(mA)(\Z)", "_mA", lineTemp)
        lineTemp = re.sub("[\s]+(V)(\Z)", "_V", lineTemp)
        lineTemp = re.sub("[\s]+(uA)(\Z)", "_uA", lineTemp)
        lineTemp = re.sub("[\s]+(N)(\Z)", "_N", lineTemp)

        #removes all space
        lineTemp = re.sub("\A\s+\Z", "", lineTemp)
        lineTemp = re.sub("\s+", ",", lineTemp)
        return lineTemp

    def genLines(self, inFileName):
        #open file
        with open(inFileName, 'r') as in_file:
            #output list
            self.allLines = []
            self.meta = []
            self.throwawayData = []
            self.pinsData = []
            self.leakageData = []
            self.vminStdData = []
            self.vminAutoData = []
            self.memYdData = []
            self.lineError = 0

            pinsOn = 0
            firstLeakageFlag=0
            firstStdVminFlag=0
            firstAutoVminFlag=0
            vminAutoShmooFlag=0
            failedMemCheckFlag=0
            failedAutoVminCheckFlag=0
            firstMemYdFlag=0
            counter=0
            match=0
            for line_number, line in enumerate(in_file, 1):
                try:
                    #removes inital and final whitespace
                    lineTemp = line.strip()
                    #santizes the lines
                    lineTemp = self.sanitize(lineTemp, line_number)
                    #splits on commas
                    lineFinal = lineTemp.split(",")
                    if(re.match("SITE",lineTemp)):
                        match=1
                        counter+=1
                        self.meta.append(lineFinal)
                        self.allLines.append(lineFinal)
                    if(re.match("TestStarted\(",lineTemp) or re.match("dut1",lineTemp)):
                        match=1
                        self.meta.append(lineFinal)
                        self.allLines.append(lineFinal)
                    if(not re.search("^$",lineTemp)):
                        if(counter > 1):
                            self.meta.append(lineFinal)
                            self.allLines.append(lineFinal)
                        else:
                            if(re.match("TstNum,Pin,Chn",lineTemp) or (((len(lineFinal) is 10) or (len(lineFinal) is 11))) and re.match("[0-9]+?,[A-Z0-9]+?,[a-z0-9_]+?,[A-Z0-9_]+?,[a-zA-Z_]+?",lineTemp)):
                                match=1
                                failedMemCheckFlag=0
                                failedAutoVminCheckFlag=0
                                if(not (lineFinal[0]=="TstNum")):
                                    if(lineFinal[9] != "(F)"):
                                        lineFinal.insert(9,"(P)")
                                self.pinsData.append(lineFinal)
                                self.allLines.append(lineFinal)
                            if(re.search("\Atb_leakage_",lineTemp)):
                                match=1
                                failedMemCheckFlag=0
                                failedAutoVminCheckFlag=0
                                if(firstLeakageFlag is 0):
                                    firstLeakageFlag = 1
                                    tempList = ["Test","Testing_Item","Test_(Repeat)","Range","Value"]
                                    self.leakageData.append(tempList)
                                    self.allLines.append(tempList)

                                lineFinal.insert(1,re.match("[a-zA-Z0-9_]+(?=_leakage)",lineFinal[1]).group(0))
                                lineFinal[2]=re.sub("\A[a-zA-Z0-9_]+(?=leakage)","",lineFinal[2])

                                lineFinal.insert(2,re.match("[a-zA-Z0-9_]+(?=_2uA)",lineFinal[2]).group(0))
                                lineFinal[3]=re.sub("\A[a-zA-Z0-9_]+(?=2uA)","",lineFinal[3])

                                self.leakageData.append(lineFinal)
                                self.allLines.append(lineFinal)
                            if(re.search("\A[0-9]+,tb_sc_yd_vmin_shm",lineTemp) or re.search("\Ashmoo_bsmin_vec_stdcell_",lineTemp)):
                                match=1
                                failedMemCheckFlag=0
                                failedAutoVminCheckFlag=0
                                if(firstStdVminFlag is 0):
                                    firstStdVminFlag = 1
                                    tempList = ["Test_Number","Test_Type","Testing_Item","Test_Type","Library","Range","Result","Test_Type_(Shmoo)","Testing_Item_(Shmoo)","Library_(Shmoo)","Result_(Shmoo)"]
                                    self.vminStdData.append(tempList)
                                    self.allLines.append(tempList)

                                if(re.search("\Ashmoo_bsmin_vec_stdcell_",lineTemp)):
                                    lineFinal.insert(0,re.match("[a-zA-Z0-9_]+(?=_sc)",lineFinal[0]).group(0))
                                    lineFinal[1]=re.sub("\A[a-zA-Z0-9_]+(?=sc)","",lineFinal[1])

                                    lineFinal.insert(1,re.match("[a-zA-Z0-9_]+(?=_sfk)",lineFinal[1]).group(0))
                                    lineFinal[2]=re.sub("\A[a-zA-Z0-9_]+(?=sfk)","",lineFinal[2])

                                    self.vminStdData[len(self.vminStdData)-1].extend(lineFinal)
                                    self.allLines[len(self.allLines)-1].extend(lineFinal)
                                else:
                                    lineFinal.insert(2,re.match("[a-zA-Z0-9_]+(?=_sc)",lineFinal[2]).group(0))
                                    lineFinal[3]=re.sub("\A[a-zA-Z0-9_]+(?=sc)","",lineFinal[3])

                                    lineFinal.insert(3,re.match("[a-zA-Z0-9_]+(?=_sfk)",lineFinal[3]).group(0))
                                    lineFinal[4]=re.sub("\A[a-zA-Z0-9_]+(?=sfk)","",lineFinal[4])

                                    lineFinal.insert(4,re.match("[a-zA-Z0-9_]+(?=_pattern)",lineFinal[4]).group(0))
                                    lineFinal[5]=re.sub("\A[a-zA-Z0-9_]+(?=pattern)","",lineFinal[5])

                                    self.vminStdData.append(lineFinal)
                                    self.allLines.append(lineFinal)

                            if(re.match("[0-9]+?,tb_mem_yd_ckb",lineTemp) or ((re.match("\([0-9]+?,pins\),FAILED",lineTemp) and (failedMemCheckFlag is 1)))):
                                match=1
                                failedMemCheckFlag=0
                                if (re.match("\([0-9]+,pins\),FAILED,\=,",lineTemp)):
                                    tempList = []
                                    tempList.append(lineTemp)
                                    tempList.insert(0,re.search("(?<=\()[0-9]+(?=,pins\),FAILED,)",tempList[0]).group(0))
                                    tempList[1]=re.sub("\([0-9]+,pins\),FAILED,\=,\{,","",tempList[1])

                                    while(re.search("[A-Z0-9_]+?,",tempList[len(tempList)-1])):
                                        tempString = re.search("[A-Z0-9_]+?,",tempList[len(tempList)-1]).group(0)
                                        tempString = tempString[:-1]+'/'
                                        tempList[len(tempList)-1] = re.sub("[A-Z0-9_]+?,",tempString,tempList[len(tempList)-1])
                                    tempList[len(tempList)-1] = tempList[len(tempList)-1][:-2]

                                    self.memYdData[len(self.memYdData)-1].pop(len(self.memYdData[len(self.memYdData)-1])-1)
                                    self.memYdData[len(self.memYdData)-1].extend(tempList)
                                    failedMemCheckFlag=0
                                else:
                                    failedMemCheckFlag=1
                                    if(firstMemYdFlag is 0):
                                        firstMemYdFlag = 1
                                        tempList = ["Test_Number","Testing_Type","A/S","Test(META???)","Location_Type","Test_Location","??","EMA#1","EMA#2","EMAW","EMAS","EMAP","WABL","WABLM","RAWL","RAWLM","KEN","RANGE","Value","Number_of_Failed_Pins","Failed_Pins"]
                                        self.memYdData.append(tempList)
                                        self.allLines.append(tempList)

                                    lineFinal.insert(1,re.match("tb_mem_yd_ckb",lineFinal[1]).group(0))
                                    lineFinal[2]=re.sub("\Atb_mem_yd_ckb_","",lineFinal[2])

                                    lineFinal.insert(3,re.match("func_vec",lineFinal[3]).group(0))
                                    lineFinal[4]=re.sub("\Afunc_vec_","",lineFinal[4])

                                    if(re.match("[a-zA-Z0-9]+?(?=_)",lineFinal[4]).group(0) == "cln16ffcll"):
                                        lineFinal.insert(4,re.match("[a-zA-Z0-9_]+?(?=_w)",lineFinal[4]).group(0))
                                        lineFinal[5]=re.sub("\A[a-zA-Z0-9_]+?(?=w)","",lineFinal[5])
                                    else:
                                        lineFinal.insert(4,re.match("[a-zA-Z0-9]+?(?=_)",lineFinal[4]).group(0))
                                        lineFinal[5]=re.sub("\A[a-zA-Z0-9]+?_","",lineFinal[5])

                                    lineFinal.insert(5,re.match("[a-zA-Z0-9]+?(?=_)",lineFinal[5]).group(0))
                                    lineFinal[6]=re.sub("\A[a-zA-Z0-9]+?_","",lineFinal[6])

                                    lineFinal.insert(6,re.match("[a-zA-Z0-9_]+?(?=_ema)",lineFinal[6]).group(0))
                                    lineFinal[7]=re.sub("\A[a-zA-Z0-9_]+?(?=ema)","",lineFinal[7])

                                    lineFinal.insert(7,re.search("(?<=ema)[a-zA-Z0-9_]+?(?=_ema)",lineFinal[7]).group(0))
                                    lineFinal[8]=re.sub("\A[a-zA-Z0-9_]+?(?=ema)","",lineFinal[8])

                                    lineFinal.insert(8,re.search("(?<=ema)[a-zA-Z0-9_]+?(?=_emaw)",lineFinal[8]).group(0))
                                    lineFinal[9]=re.sub("\A[a-zA-Z0-9_]+?(?=emaw)","",lineFinal[9])

                                    lineFinal.insert(9,re.search("(?<=emaw)[a-zA-Z0-9_]+?(?=_emas)",lineFinal[9]).group(0))
                                    lineFinal[10]=re.sub("\A[a-zA-Z0-9_]+?(?=emas)","",lineFinal[10])

                                    lineFinal.insert(10,re.search("(?<=emas)[a-zA-Z0-9_]+?(?=_emap)",lineFinal[10]).group(0))
                                    lineFinal[11]=re.sub("\A[a-zA-Z0-9_]+?(?=emap)","",lineFinal[11])

                                    lineFinal.insert(11,re.search("(?<=emap)[a-zA-Z0-9_]+?(?=_wabl)",lineFinal[11]).group(0))
                                    lineFinal[12]=re.sub("\A[a-zA-Z0-9_]+?(?=wabl)","",lineFinal[12])

                                    lineFinal.insert(12,re.search("(?<=wabl)[a-zA-Z0-9_]+?(?=_wablm)",lineFinal[12]).group(0))
                                    lineFinal[13]=re.sub("\A[a-zA-Z0-9_]+?(?=wablm)","",lineFinal[13])

                                    lineFinal.insert(13,re.search("(?<=wablm)[a-zA-Z0-9_]+?(?=_rawl)",lineFinal[13]).group(0))
                                    lineFinal[14]=re.sub("\A[a-zA-Z0-9_]+?(?=rawl)","",lineFinal[14])

                                    lineFinal.insert(14,re.search("(?<=rawl)[a-zA-Z0-9_]+?(?=_rawlm)",lineFinal[14]).group(0))
                                    lineFinal[15]=re.sub("\A[a-zA-Z0-9_]+?(?=rawlm)","",lineFinal[15])

                                    lineFinal.insert(15,re.search("(?<=rawlm)[a-zA-Z0-9_]+?(?=_ken)",lineFinal[15]).group(0))
                                    lineFinal[16]=re.sub("\A[a-zA-Z0-9_]+?(?=ken)","",lineFinal[16])

                                    lineFinal.insert(16,re.search("(?<=ken)[a-zA-Z0-9_]+?(?=_vddpe)",lineFinal[16]).group(0))
                                    lineFinal[17]=re.sub("\A[a-zA-Z0-9_]+?(?=vddpe)","",lineFinal[17])

                                    lineFinal.append("0")

                                    self.memYdData.append(lineFinal)
                                    self.allLines.append(lineFinal)
                            if(re.search("\A[0-9]+,tb_vmin_ckb",lineTemp) or (vminAutoShmooFlag is 1) or ((re.match("\([0-9]+?,pins\),FAILED",lineTemp) and (failedAutoVminCheckFlag is 1)))):
                                match=1
                                failedMemCheckFlag=0
                                if(re.match("\([0-9]+?,pins\),FAILED",lineTemp)):
                                    #raise AttributeError
                                    tempList = []
                                    tempList.append(lineTemp)
                                    tempList.insert(0,re.search("(?<=\()[0-9]+(?=,pins\),FAILED,)",tempList[0]).group(0))
                                    tempList[1]=re.sub("\([0-9]+,pins\),FAILED,\=,\{,","",tempList[1])

                                    while(re.search("[A-Z0-9_]+?,",tempList[len(tempList)-1])):
                                        tempString = re.search("[A-Z0-9_]+?,",tempList[len(tempList)-1]).group(0)
                                        tempString = tempString[:-1]+'/'
                                        tempList[len(tempList)-1] = re.sub("[A-Z0-9_]+?,",tempString,tempList[len(tempList)-1])
                                    tempList[len(tempList)-1] = tempList[len(tempList)-1][:-2]

                                    self.vminAutoData[len(self.vminAutoData)-1].pop(len(self.vminAutoData[len(self.vminAutoData)-1])-1)
                                    self.vminAutoData[len(self.vminAutoData)-1].pop(len(self.vminAutoData[len(self.vminAutoData)-1])-1)
                                    self.vminAutoData[len(self.vminAutoData)-1].extend(tempList)
                                    failedAutoVminCheckFlag=0
                                else:
                                    failedAutoVminCheckFlag=1
                                    if(firstAutoVminFlag is 0):

                                        firstAutoVminFlag = 1
                                        tempList = ["Test_Number","Test","A/S","Location_Type(Catagory)","Test(META???)","Location_Type","Test_Location","??","EMA#1","EMA#2","EMAW","EMAS","EMAP","WABL","WABLM","RAWL","RAWLM","KEN","RANGE","Value","Number_of_Failed_Pins","Failed_Pins","Test_Type(Shmoo)","Location_Type(Shmoo)","Test_Location(Shmoo)","??(Shmoo)","EMA#1(Shmoo)","EMA#2(Shmoo)","EMAW(Shmoo)","EMAS(Shmoo)","EMAP(Shmoo)","WABL(Shmoo)","WABLM(Shmoo)","RAWL(Shmoo)","RAWLM(Shmoo)","KEN(Shmoo)","Value(Shmoo)"]
                                        self.vminAutoData.append(tempList)
                                        self.allLines.append(tempList)

                                    if(re.search("\A[0-9]+,tb_vmin_ckb",lineTemp)):
                                        vminAutoShmooFlag=1

                                        lineFinal.insert(1,re.match("tb_vmin_ckb",lineFinal[1]).group(0))
                                        lineFinal[2]=re.sub("\Atb_vmin_ckb_","",lineFinal[2])

                                        lineFinal.insert(2,re.match("[a-zA-Z0-9]+?(?=_)",lineFinal[2]).group(0))
                                        lineFinal[3]=re.sub("\A[a-zA-Z0-9]+?_","",lineFinal[3])

                                        lineFinal.insert(4,re.match("Vmax_vec",lineFinal[4]).group(0))
                                        lineFinal[5]=re.sub("\AVmax_vec_","",lineFinal[5])

                                        if(re.match("[a-zA-Z0-9]+?(?=_)",lineFinal[5]).group(0) == "cln16ffcll"):
                                            lineFinal.insert(5,re.match("[a-zA-Z0-9_]+?(?=_w)",lineFinal[5]).group(0))
                                            lineFinal[6]=re.sub("\A[a-zA-Z0-9_]+?(?=w)","",lineFinal[6])
                                        else:
                                            lineFinal.insert(5,re.match("[a-zA-Z0-9]+?(?=_)",lineFinal[5]).group(0))
                                            lineFinal[6]=re.sub("\A[a-zA-Z0-9]+?_","",lineFinal[6])

                                        lineFinal.insert(6,re.match("[a-zA-Z0-9]+?(?=_)",lineFinal[6]).group(0))
                                        lineFinal[7]=re.sub("\A[a-zA-Z0-9]+?_","",lineFinal[7])

                                        lineFinal.insert(7,re.match("[a-zA-Z0-9_]+?(?=_ema)",lineFinal[7]).group(0))
                                        lineFinal[8]=re.sub("\A[a-zA-Z0-9_]+?(?=ema)","",lineFinal[8])

                                        lineFinal.insert(8,re.search("(?<=ema)[a-zA-Z0-9_]+?(?=_ema)",lineFinal[8]).group(0))
                                        lineFinal[9]=re.sub("\A[a-zA-Z0-9_]+?(?=ema)","",lineFinal[9])

                                        lineFinal.insert(9,re.search("(?<=ema)[a-zA-Z0-9_]+?(?=_emaw)",lineFinal[9]).group(0))
                                        lineFinal[10]=re.sub("\A[a-zA-Z0-9_]+?(?=emaw)","",lineFinal[10])

                                        lineFinal.insert(10,re.search("(?<=emaw)[a-zA-Z0-9_]+?(?=_emas)",lineFinal[10]).group(0))
                                        lineFinal[11]=re.sub("\A[a-zA-Z0-9_]+?(?=emas)","",lineFinal[11])

                                        lineFinal.insert(11,re.search("(?<=emas)[a-zA-Z0-9_]+?(?=_emap)",lineFinal[11]).group(0))
                                        lineFinal[12]=re.sub("\A[a-zA-Z0-9_]+?(?=emap)","",lineFinal[12])

                                        lineFinal.insert(12,re.search("(?<=emap)[a-zA-Z0-9_]+?(?=_wabl)",lineFinal[12]).group(0))
                                        lineFinal[13]=re.sub("\A[a-zA-Z0-9_]+?(?=wabl)","",lineFinal[13])

                                        lineFinal.insert(13,re.search("(?<=wabl)[a-zA-Z0-9_]+?(?=_wablm)",lineFinal[13]).group(0))
                                        lineFinal[14]=re.sub("\A[a-zA-Z0-9_]+?(?=wablm)","",lineFinal[14])

                                        lineFinal.insert(14,re.search("(?<=wablm)[a-zA-Z0-9_]+?(?=_rawl)",lineFinal[14]).group(0))
                                        lineFinal[15]=re.sub("\A[a-zA-Z0-9_]+?(?=rawl)","",lineFinal[15])

                                        lineFinal.insert(15,re.search("(?<=rawl)[a-zA-Z0-9_]+?(?=_rawlm)",lineFinal[15]).group(0))
                                        lineFinal[16]=re.sub("\A[a-zA-Z0-9_]+?(?=rawlm)","",lineFinal[16])

                                        lineFinal.insert(16,re.search("(?<=rawlm)[a-zA-Z0-9_]+?(?=_ken)",lineFinal[16]).group(0))
                                        lineFinal[17]=re.sub("\A[a-zA-Z0-9_]+?(?=ken)","",lineFinal[17])

                                        lineFinal.insert(17,re.search("(?<=ken)[a-zA-Z0-9_]+?(?=_vddpe)",lineFinal[17]).group(0))
                                        lineFinal[18]=re.sub("\A[a-zA-Z0-9_]+?(?=vddpe)","",lineFinal[18])

                                        lineFinal.append("0")
                                        lineFinal.append(None)

                                        self.vminAutoData.append(lineFinal)
                                        self.allLines.append(lineFinal)
                                    else:
                                        vminAutoShmooFlag=0

                                        lineFinal.insert(0,re.match("shmoo_bsmin_vec",lineFinal[0]).group(0))
                                        lineFinal[1]=re.sub("\Ashmoo_bsmin_vec_","",lineFinal[1])

                                        if(re.match("[a-zA-Z0-9]+?(?=_)",lineFinal[1]).group(0) == "cln16ffcll"):
                                            lineFinal.insert(1,re.match("[a-zA-Z0-9_]+?(?=_w)",lineFinal[1]).group(0))
                                            lineFinal[2]=re.sub("\A[a-zA-Z0-9_]+?(?=w)","",lineFinal[2])
                                        else:
                                            lineFinal.insert(1,re.match("[a-zA-Z0-9]+?(?=_)",lineFinal[1]).group(0))
                                            lineFinal[2]=re.sub("\A[a-zA-Z0-9]+?_","",lineFinal[2])

                                        lineFinal.insert(2,re.match("[a-zA-Z0-9]+?(?=_)",lineFinal[2]).group(0))
                                        lineFinal[3]=re.sub("\A[a-zA-Z0-9]+?_","",lineFinal[3])

                                        lineFinal.insert(3,re.match("[a-zA-Z0-9_]+?(?=_ema)",lineFinal[3]).group(0))
                                        lineFinal[4]=re.sub("\A[a-zA-Z0-9_]+?(?=ema)","",lineFinal[4])

                                        lineFinal.insert(4,re.search("(?<=ema)[a-zA-Z0-9_]+?(?=_ema)",lineFinal[4]).group(0))
                                        lineFinal[5]=re.sub("\A[a-zA-Z0-9_]+?(?=ema)","",lineFinal[5])

                                        lineFinal.insert(5,re.search("(?<=ema)[a-zA-Z0-9_]+?(?=_emaw)",lineFinal[5]).group(0))
                                        lineFinal[6]=re.sub("\A[a-zA-Z0-9_]+?(?=emaw)","",lineFinal[6])

                                        lineFinal.insert(6,re.search("(?<=emaw)[a-zA-Z0-9_]+?(?=_emas)",lineFinal[6]).group(0))
                                        lineFinal[7]=re.sub("\A[a-zA-Z0-9_]+?(?=emas)","",lineFinal[7])

                                        lineFinal.insert(7,re.search("(?<=emas)[a-zA-Z0-9_]+?(?=_emap)",lineFinal[7]).group(0))
                                        lineFinal[8]=re.sub("\A[a-zA-Z0-9_]+?(?=emap)","",lineFinal[8])

                                        lineFinal.insert(8,re.search("(?<=emap)[a-zA-Z0-9_]+?(?=_wabl)",lineFinal[8]).group(0))
                                        lineFinal[9]=re.sub("\A[a-zA-Z0-9_]+?(?=wabl)","",lineFinal[9])

                                        lineFinal.insert(9,re.search("(?<=wabl)[a-zA-Z0-9_]+?(?=_wablm)",lineFinal[9]).group(0))
                                        lineFinal[10]=re.sub("\A[a-zA-Z0-9_]+?(?=wablm)","",lineFinal[10])

                                        lineFinal.insert(10,re.search("(?<=wablm)[a-zA-Z0-9_]+?(?=_rawl)",lineFinal[10]).group(0))
                                        lineFinal[11]=re.sub("\A[a-zA-Z0-9_]+?(?=rawl)","",lineFinal[11])

                                        lineFinal.insert(11,re.search("(?<=rawl)[a-zA-Z0-9_]+?(?=_rawlm)",lineFinal[11]).group(0))
                                        lineFinal[12]=re.sub("\A[a-zA-Z0-9_]+?(?=rawlm)","",lineFinal[12])

                                        lineFinal.insert(12,re.search("(?<=rawlm)[a-zA-Z0-9_]+?(?=_ken)",lineFinal[12]).group(0))
                                        lineFinal[13]=re.sub("\A[a-zA-Z0-9_]+?(?=ken)","",lineFinal[13])

                                        self.vminAutoData[len(self.vminAutoData)-1].extend(lineFinal)
                                        self.allLines[len(self.allLines)-1].extend(lineFinal)

                            if(match==0):
                                self.throwawayData.append(lineFinal)
                            match=0
                except AttributeError as error:
                    exc_type, exc_obj, tb = sys.exc_info()
                    print("------------ .txt line "+str(line_number)+" was not able to create due to:")
                    exc_type, exc_obj, tb = sys.exc_info()
                    lineno = tb.tb_lineno
                    print("-------- codeline was on "+str(lineno))
                    print("-------- line was"+lineTemp)
                    self.lineError+=1



    def genFullCSV(self, filePath="default"):
        #opens output file
        self.makeDir(filePath)
        with open(filePath+"/fullOutput.csv", "w") as out_file:
            #writes csv file from list
            writer = csv.writer(out_file)
            writer.writerows(self.allLines)

    def genMetaCSV(self, filePath="default"):
        #opens output file
        self.makeDir(filePath)
        with open(filePath+"/metaOutput.csv", "w") as out_file:
            #writes csv file from list
            writer = csv.writer(out_file)
            writer.writerows(self.meta)

    def genThrowawayCSV(self, filePath="default"):
        #opens output file
        self.makeDir(filePath)
        with open(filePath+"/throwawayOutput.csv", "w") as out_file:
            #writes csv file from list
            writer = csv.writer(out_file)
            writer.writerows(self.throwawayData)
            throwawayDataSize=len(self.throwawayData)
            if(throwawayDataSize>0):
                print("file \""+filePath+"\".txt has "+str(throwawayDataSize)+" unrecognized lines")

    def genPinsCSV(self, filePath="default"):
        #opens output file
        self.makeDir(filePath)
        with open(filePath+"/pinsOutput.csv", "w") as out_file:
            #writes csv file from list
            writer = csv.writer(out_file)
            writer.writerows(self.pinsData)

    def genLeakageCSV(self, filePath="default"):
        #opens output file
        self.makeDir(filePath)
        with open(filePath+"/leakageOutput.csv", "w") as out_file:
            #writes csv file from list
            writer = csv.writer(out_file)
            writer.writerows(self.leakageData)

    def genStdVminCSV(self, filePath="default"):
        #opens output file
        self.makeDir(filePath)
        with open(filePath+"/vminStdOutput.csv", "w") as out_file:
            #writes csv file from list
            writer = csv.writer(out_file)
            writer.writerows(self.vminStdData)

    def genMemCSV(self, filePath="default"):
        #opens output file
        self.makeDir(filePath)
        with open(filePath+"/memYdOutput.csv", "w") as out_file:
            #writes csv file from list
            writer = csv.writer(out_file)
            writer.writerows(self.memYdData)

    def genAutoVminCSV(self, filePath="default"):
        #opens output file
        self.makeDir(filePath)
        with open(filePath+"/vminAutoOutput.csv", "w") as out_file:
            #writes csv file from list
            writer = csv.writer(out_file)
            writer.writerows(self.vminAutoData)

    def makeDir(self,path):
        if not os.path.exists(path):
            os.makedirs(path)

    def makeAllCSVs(self, fileInput="default.txt",folderName="default"):
        self.genLines(fileInput)
        self.makeDir(folderName)
        self.genFullCSV(folderName)
        self.genMetaCSV(folderName)
        self.genThrowawayCSV(folderName)
        self.genPinsCSV(folderName)
        self.genLeakageCSV(folderName)
        self.genStdVminCSV(folderName)
        self.genMemCSV(folderName)
        self.genAutoVminCSV(folderName)

        if(self.lineError>0):
            raise AttributeError(str(self.lineError))

#instance = test1_()
#instance.makeAllCSVs("102_TT_25C.txt","tempfile")
