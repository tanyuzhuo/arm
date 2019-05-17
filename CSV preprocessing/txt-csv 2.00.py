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
            allLines = []
            throwawayData = []
            pins = []

            pinsOn = 0
            for line_number, line in enumerate(in_file, 1):

                #removes inital and final whitespace
                lineTemp = line.strip()
                #santizes the lines
                lineTemp = self.sanitize(lineTemp, line_number)
                #splits on commas
                lineFinal = lineTemp.split(",")

                if(not re.search("^$",lineTemp)):
                    #appends to an array and returns it class wide
                    lines.append(lineFinal)
                    self.lines=allLines

                    #sets start flag for pins
                    if(re.search("TSTNum,Pin,Chn",lineTemp) or (pinsOn is not 0)):
                        if(re.search("TSTNum,Pin,Chn",lineTemp):
                            pins = 1
                        pins.append[]
                    elif(re.search("\Atb_leakage_low,",lineTemp):
                else:
                    throwawayData.append(lineFinal)




    def genFullCSV(self, fileOutput="fullOutput.csv"):
        #opens output file
        with open(fileOutput, "w") as out_file:
            #writes csv file from list
            writer = csv.writer(out_file)
            writer.writerows(self.lines)

test1 = test1_()
test1.input()
test1.genLines()
test1.genFullCSV()
