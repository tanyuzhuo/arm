import csv
import re

class test1_:
    #adds file and init. variables
    def input(self, fileInput='104_TT_150C.txt'):
        self.fileName=fileInput
        self.fileLinesNo = sum(1 for line in open(fileInput))
        self.lineLeakageStart = -1
        self.lineLeakageEnd = -1

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
        lineTemp = re.sub("[\s](TOTAL)[\s](TEST)[\s](TIME)[\s]", " TOTAL_TEST_TIME ", lineTemp)

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

    def genLines(self):
        #open file
        with open(self.fileName, 'r') as in_file:
            #output list
            self.allLines = []
            self.meta = []
            self.throwawayData = []
            self.pinsData = []
            self.leakageData = []
            self.vminData = []

            pinsOn = 0
            firstLeakageFlag=0
            firstVminFlag=0
            counter=0
            for line_number, line in enumerate(in_file, 1):

                #removes inital and final whitespace
                lineTemp = line.strip()
                #santizes the lines
                lineTemp = self.sanitize(lineTemp, line_number)
                #splits on commas
                lineFinal = lineTemp.split(",")
                if(re.search("\ASITE",lineTemp)):
                    counter+=1
                    self.allLines.append(lineFinal)
                if(not re.search("^$",lineTemp)):
                    #appends to an array and returns it class wide
                    self.allLines.append(lineFinal)

                    #checks if running times
                    if(counter > 1):
                        self.meta.append(lineFinal)
                    else:
                        #checks if it is a pin data line
                        if(re.search("\ATSTNum,Pin,Chn",lineTemp) or (len(lineFinal) is 10) or (len(lineFinal) is 11)):
                            if(not (lineFinal[0]=="TstNum")):
                                if(lineFinal[9] != "(F)"):
                                    lineFinal.insert(9,"(P)")
                            self.pinsData.append(lineFinal)
                        if(re.search("\Atb_leakage_",lineTemp)):
                            if(firstLeakageFlag is 0):
                                pinsOn=0
                                firstLeakageFlag = 1
                                tempList = ["Test_Number","Testing_Item","Test","Range"]
                                self.leakageData.append(tempList)

                            lineFinal.insert(1,re.search("[a-zA-Z0-9_]+(?=_leakage)",lineFinal[1]).group(0))
                            lineFinal[2]=re.sub("[a-zA-Z0-9_]+(?=_leakage)","",lineFinal[2])
                            self.leakageData.append(lineFinal)
                        if(re.search("\A[0-9]+,tb_sc_yd_vmin_shm",lineTemp) or re.search("\Ashmoo_bsmin_vec_stdcell_",lineTemp)):
                            if(firstVminFlag is 0):
                                firstVminFlag = 1
                                tempList = ["Test_Type","Testing_Item","Test_Type","Range","Value"]
                                self.vminData.append(tempList)
                            if(re.search("\Ashmoo_bsmin_vec_stdcell_",lineTemp)):
                                for i in range(len(lineFinal)):
                                    self.vminData[len(self.vminData)-1].append(lineFinal[i])
                            else:
                                self.vminData.append(lineFinal)
                        else:
                            self.throwawayData.append(lineFinal)
                else:
                    self.throwawayData.append(lineFinal)




    def genFullCSV(self, fileOutput="fullOutput.csv"):
        #opens output file
        with open(fileOutput, "w") as out_file:
            #writes csv file from list
            writer = csv.writer(out_file)
            writer.writerows(self.allLines)

    def genMetaCSV(self, fileOutput="metaOutput.csv"):
        #opens output file
        with open(fileOutput, "w") as out_file:
            #writes csv file from list
            writer = csv.writer(out_file)
            writer.writerows(self.meta)

    def genThrowawayCSV(self, fileOutput="ThrowawayOutput.csv"):
        #opens output file
        with open(fileOutput, "w") as out_file:
            #writes csv file from list
            writer = csv.writer(out_file)
            writer.writerows(self.throwawayData)

    def genPinsCSV(self, fileOutput="pinsOutput.csv"):
        #opens output file
        with open(fileOutput, "w") as out_file:
            #writes csv file from list
            writer = csv.writer(out_file)
            writer.writerows(self.pinsData)

    def genLeakageCSV(self, fileOutput="leakageOutput.csv"):
        #opens output file
        with open(fileOutput, "w") as out_file:
            #writes csv file from list
            writer = csv.writer(out_file)
            writer.writerows(self.leakageData)

    def genVminCSV(self, fileOutput="vminOutput.csv"):
        #opens output file
        with open(fileOutput, "w") as out_file:
            #writes csv file from list
            writer = csv.writer(out_file)
            writer.writerows(self.vminData)

test1 = test1_()
test1.input()
test1.genLines()
test1.genFullCSV()
test1.genMetaCSV()
test1.genThrowawayCSV()
test1.genPinsCSV()
test1.genLeakageCSV()
test1.genVminCSV()
