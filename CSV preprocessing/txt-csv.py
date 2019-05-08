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
        lineTemp = re.sub("TestValue", "TestValue,", lineTemp)
        if((self.lineLeakageStart==-1) or (lineNo<self.lineLeakageStart)):
            matchObj = re.match( ".*", lineTemp, re.M|re.I)
            string = matchObj(1)
            lineTemp = re.sub(".*",string, lineTemp)

        #removes - < : from file
        lineTemp = re.sub("[-]+", "", lineTemp)
        lineTemp = re.sub("<", "", lineTemp)
        lineTemp = re.sub(":", "", lineTemp)

        #appends units on numbers and removes whitespace between
        lineTemp = re.sub("[\s]+(mV)[\s]", "_mV ", lineTemp)
        lineTemp = re.sub("[\s]+(mA)[\s]", "_mA ", lineTemp)
        lineTemp = re.sub("[\s]+(V)[\s]", "_V ", lineTemp)
        lineTemp = re.sub("[\s]+(uA)[\s]", "_uA ", lineTemp)
        lineTemp = re.sub("[\s]+(N)[\s]", "_N ", lineTemp)
        #same as above but checks in case it doesnt end in whitespace
        lineTemp = re.sub("[\s]+(mV)(\Z)", "_mV", lineTemp)
        lineTemp = re.sub("[\s]+(mA)(\Z)", "_mA", lineTemp)
        lineTemp = re.sub("[\s]+(V)(\Z)", "_V", lineTemp)
        lineTemp = re.sub("[\s]+(uA)(\Z)", "_uA", lineTemp)
        lineTemp = re.sub("[\s]+(N)(\Z)", "_N", lineTemp)

        #checks for pass fail and appends
        ##lineTemp = re.sub("[\s]+\(F\)[\s]", "_(F) ", lineTemp)
        ##lineTemp = re.sub("[\s]+\(F\)", "_(F)", lineTemp)
        ##lineTemp = re.sub("[\s]+\(P\)[\s]", "_(P) ", lineTemp)
        ##lineTemp = re.sub("[\s]+\(P\)", "_(P)", lineTemp)

        #removes all space
        lineTemp = re.sub("\s+", ",", lineTemp)
        return lineTemp

    def genLines(self):
        #open file
        with open(self.fileName, 'r') as in_file:
            #output list
            lines = []
            lineStart=-1
            lineEnd=-1
            for line_number, line in enumerate(in_file, 1):
                #removes inital and final whitespace
                lineTemp = line.strip()
                #santizes the lines
                lineTemp = self.sanitize(lineTemp, line_number)
                #splits on commas
                lineFinal = lineTemp.split(",")

                #appends to an array and returns it class wide
                lines.append(lineFinal)
                self.lines=lines

                #gets boundaries of leakage
                if(re.search("leakage",lineTemp)):
                    if(self.lineLeakageStart==-1):
                        self.lineLeakageStart=line_number
                    else:
                        if((self.lineLeakageEnd<line_number) and (line_number<self.fileLinesNo-25)):
                            self.lineLeakageEnd=line_number

    def genFullCSV(self, fileOutput="fullOutput.csv"):
        #opens output file
        with open(fileOutput, "w") as out_file:
            #writes csv file from list
            writer = csv.writer(out_file)
            writer.writerows(self.lines)
    def genPinsCSV(self, fileOutput="pinsOutput.csv"):
        #opens output file
        with open(fileOutput, "w") as out_file:
            #writes csv file from list with range to first line of leakage
            writer = csv.writer(out_file)
            writer.writerows(self.lines[:self.lineLeakageStart-1])

    def genLeakageCSV(self, fileOutput="leakageOutput.csv"):
        #opens output file
        with open(fileOutput, "w") as out_file:
            #writes csv file from list with leakage range
            writer = csv.writer(out_file)
            writer.writerows(self.lines[self.lineLeakageEnd<-1:self.lineLeakageEnd])

test1 = test1_()
test1.input()
test1.genLines()
test1.genFullCSV()
test1.genPinsCSV()
test1.genLeakageCSV()
