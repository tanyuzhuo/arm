import csv
import re

#open file
with open('104_TT_150C.txt', 'r') as in_file:
    #old code keeping temp.
        #replaces whitespace with comma and removes front and back whitespace
        #stripped = (re.sub("(\s+<\s+|\s+)(?!(mV|uA|N\s))", ",", line.strip()) for line in in_file)

        #splits each line into list
        #lines = (line.split(",") for line in stripped if line)

    #output list
    lines = []
    for line in in_file:
        #removes inital and final whitespace
        lineTemp = line.strip()

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
        lineTemp = re.sub("[\s]+\(F\)[\s]", "_(F) ", lineTemp)
        lineTemp = re.sub("[\s]+\(F\)", "_(F)", lineTemp)
        lineTemp = re.sub("[\s]+\(P\)[\s]", "_(P) ", lineTemp)
        lineTemp = re.sub("[\s]+\(P\)", "_(P)", lineTemp)

        lineTemp = re.sub("\s+", ",", lineTemp)
        lineFinal = (lineTemp.split(","))
        lines.append(lineFinal)

    #opens output file
    with open("test.csv", "w") as out_file:
        #writes csv file from list
        writer = csv.writer(out_file)
        writer.writerow(('title', 'intro'))
        writer.writerows(lines)
