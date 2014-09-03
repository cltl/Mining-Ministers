#!/usr/bin/python
# -*- coding: utf-8 -*-


from math import radians, cos, sin, asin, sqrt
import operator

my_input = open('priest_info_all_ids.tsv','r')


tot = 0

birthCount = 0
bapCount = 0
birthUnknown = 0
bDates = []

dCount = 0
fCount = 0
deathUnknown = 0

dDates = []

eCount = 0
eDates = []

vCount = 0
vDates = []

fjCount = 0
fjDates = []

fjAges = []
eAges = []
dAges = []

fjAgePerDecade = {}

def retrieve_first(jobInfo):
    parts = jobInfo.split('|')
    for part in parts:
        if '*' in part:
            jobDate = part.split('*')[1]
            if not 'yyyy' in jobDate and not 'UNKNOWN' in jobDate and not 'OR' in jobDate:
                date = jobDate
                return date

def birthEarlierInYear(birthPs, lPs):
    if len(birthPs) == 1 or len(lPs) == 1:
        return True
    bMonth = birthPs[1]
    lMonth = lPs[1]
    if 'mm' in bMonth:
        #default
        if 'mm' in lMonth:
            return True
        else:
            if int(lMonth) > 6:
                return True
            else:
                return False
    else:
        if 'mm' in lMonth:
            if int(bMonth) < 7:
                return True
            else:
                return False
        else:
            if int(bMonth) > int(lMonth):
                return False
            elif int(lMonth) > int(bMonth):
                return True
            else:
                if len(lPs) == 2 or len(birthPs) == 2:
                    return True
                if 'dd' in birthPs:
                    if 'dd' in lPs:
                        return True
                    elif int(lPs[2]) > 15:
                        return False
                    else:
                        return True
                else:
                    if 'dd' in lPs:
                        if int(birthPs[2]) > 15:
                            return False
                        else:
                            return True
                    else:
                        if int(birthPs[2]) > int(lPs[2]):
                            return False
                        else:
                            return True

def calculateAge(birth, later):
    bParts = birth.rstrip('\n').split('-')
    lParts = later.rstrip('\n').split('-')
    bYear = bParts[0]
    lYear = lParts[0]

    age = int(lYear) - int(bYear)
    if not birthEarlierInYear(bParts, lParts):
        age += 1
    return age


def getAveragesAndExtremes(ageList):

    tot_age = 0
    youngest = 500
    oldest = 0

    for age in ageList:
        tot_age += age
        if age < youngest:
            youngest = age
        if age > oldest:
            oldest = age

    av = float(tot_age)/float(len(ageList))

    return [av, youngest, oldest]



def earlier_date(date1, date2):
    d1 = date1.split('-')
    d2 = date2.split('-')
    if int(d1[0]) > int(d2[0]):
        return date2
    elif int(d2[0]) > int(d1[0]):
        return date1
    elif len(d1) > 1 and len(d2) > 1:
        #we care mainly about the year anyway...
        if 'mm' in date1 or 'mm' in date2:
            return date1
        elif int(d1[1]) > int(d2[1]):
            return  date2
        elif int(d2[1]) > int(d1[1]):
            return  date1
        elif len(d1) > 2 and len(d2) > 2:
            if 'dd' in date1 or 'dd' in date2:
                return date1
            elif int(d1[2]) > int(d2[2]):
                return  date2
            else:
                return date1
        else:
            return date1
    else:
        return date1

def findEarliestDate(dateList):
    earliestDate = '2014-08-25'
    for myDate in dateList:
        earliestDate = earlier_date(earliestDate, myDate)
    return earliestDate

def findLatestDate(dateList):
    latestDate = '0000-00-00'
    for myDate in dateList:
        earlier = earlier_date(latestDate, myDate)
        if latestDate == earlier:
            latestDate = myDate
    return latestDate

def getDecade(date):
    decade = ''
    year = date.split('-')[0]
    if not len(year) + 4:
        print year
    else:
        decade = year[0] + year[1] + year[2] + '0'
    return decade


def createDecadeDict(dateList):
    decDict = {}
    
    for date in dateList:
        decade = getDecade(date)
        if decade:
            if decade in decDict:
                decDict[decade] += 1
            else:
                decDict[decade] = 1
    return decDict

for line in my_input:
    info = line.split('\t')
    if len(info) < 11:
        print 'Error: Something wrong with entry', line
    else:
        tot += 1
        bDate = info[1]
        if not 'UNKNOWN' in bDate:
            birthCount += 1
        else:
            bDate = info[3]
            if not 'UNKNOWN' in bDate:
                bapCount += 1
            else:
                bDate = ''
                birthUnknown += 1
        if bDate:
            bDates.append(bDate)
        dDate = info[5]
        if not 'UNKNOWN' in dDate:
            dCount += 1
        else:
            dDate = info[7]
            if not 'UNKNOWN' in dDate:
                fCount += 1
            else:
                dDate = ''
                deathUnknown += 1
        if dDate:
            dDates.append(dDate)
        eDate = info[9]
        if not 'UNKNOWN' in eDate:
            eCount += 1
            eDates.append(eDate)
        else:
            eDate = ''
        vDate = info[10]
        if not 'UNKNOWN' in vDate:
            vCount += 1
            vDates.append(vDate)
        else:
            vDate = ''
        jobInfo = info[11]

        firstJob = retrieve_first(jobInfo)
        if firstJob:
            fjCount += 1
            fjDates.append(firstJob)

        if dDate == '11667':
            print line

        if bDate:
            if firstJob:
                beginAge = calculateAge(bDate, firstJob)
                #starting earlier than 12 is given required education extremely unlikely (maybe even raise this?), only person to start after 100, supposedly started at the age of 125 and died at age 149
                if 12 < beginAge < 100:
                    fjAges.append(beginAge)
                    decade = firstJob[0] + firstJob[1] + firstJob[2] + '0'
                    if not decade in fjAgePerDecade:
                        fjAgePerDecade[decade] = [beginAge]
                    else:
                        fjAgePerDecade[decade].append(beginAge)
                        #if beginAge > 60:
#print line
            if eDate:
                retireAge = calculateAge(bDate, eDate)
                if 0 < retireAge:
                    eAges.append(retireAge)
            if dDate:
                ultimateAge = calculateAge(bDate, dDate)
                if 125 > ultimateAge > 12:
                    dAges.append(ultimateAge)


oldestPriest = findEarliestDate(bDates)
youngestPriest = findLatestDate(bDates)

print 'Earliest birthdate:', oldestPriest
print 'Latest birthdate:', youngestPriest

firstToStart = findEarliestDate(fjDates)
lastToStart = findLatestDate(fjDates)

print 'Earliest job starting date:', firstToStart
print 'Latest job starting date:', lastToStart

firstExpelled = findEarliestDate(vDates)
lastExpelled = findLatestDate(vDates)

print 'First time expelled:', firstExpelled
print 'Last time expelled:', lastExpelled

firstRetirement = findEarliestDate(eDates)
lastRetirement = findLatestDate(eDates)

print 'First retirement:', firstRetirement
print 'Last retirement:', lastRetirement

firstDeath = findEarliestDate(dDates)
lastDeath = findLatestDate(dDates)

print 'First death:', firstDeath
print 'Last death:', lastDeath


fJFigs = getAveragesAndExtremes(fjAges)

print 'Average age starting:', fJFigs[0]
print 'Youngest known starting age', fJFigs[1]
print 'Oldest known starting age', fJFigs[2]


eFigs = getAveragesAndExtremes(eAges)

print 'Average age retiring:', eFigs[0]
print 'Youngest known retirement age', eFigs[1]
print 'Oldest known retirement age', eFigs[2]


dFigs = getAveragesAndExtremes(dAges)

print 'Average age dying:', dFigs[0]
print 'Youngest known dying age', dFigs[1]
print 'Oldest known dying age', dFigs[2]

birthDecades = createDecadeDict(bDates)
bDfile = open('birthPerDec.csv','w')
firstJobDecades = createDecadeDict(fjDates)
fjDfile = open('firstJobPerDec.csv','w')
expelDecades = createDecadeDict(vDates)
eDfile = open('expelPerDec.csv','w')
retireDecades = createDecadeDict(eDates)
rDfile = open('retirePerDec.csv','w')
deathDecades = createDecadeDict(dDates)
dDfile = open('deathPerDec.csv','w')

startDate = 1500

avfjDfile = open('avFirstJobPerDec.csv','w')

myDicts = [birthDecades, firstJobDecades, expelDecades, retireDecades, deathDecades]
myFiles = [bDfile, fjDfile, eDfile, rDfile, dDfile ]

def add_line_toDecadeFiles(startDate):
    key = str(startDate)
    for index in range(len(myDicts)):
        myD = myDicts[index]
        myF = myFiles[index]
        if key in myD:
            myF.write(key + ',' + str(myD.get(key)) + '\n')
        else:
            myF.write(key + ',0\n')
    #create averageAge per decade
    if key in fjAgePerDecade:
        ageList = fjAgePerDecade.get(key)
        afjdFigs = getAveragesAndExtremes(ageList)
        avfjDfile.write(key + ',' + str(afjdFigs[1]) + ',' + str(afjdFigs[2]) + ',' + str(afjdFigs[0]) + ',' + str(len(ageList)) + '\n')
    else:
        avfjDfile.write(key + ',-,-,-,0\n')

while startDate < 1900:
    add_line_toDecadeFiles(startDate)
    startDate += 10

bDfile.close()
fjDfile.close()
eDfile.close()
rDfile.close()
dDfile.close()
avfjDfile.close()







