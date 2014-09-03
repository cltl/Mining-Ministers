#!/usr/bin/python
# -*- coding: utf-8 -*-


from math import radians, cos, sin, asin, sqrt
import operator

my_input = open('priest_info_all_ids.tsv','r')



geoId2Coords = {}
geoFilename = 'geoLieburgCorpus.txt'

def initiate_geoDict():
    global geoFilename, geoId2Coords
    geoFile = open(geoFilename, 'r')
    for line in geoFile:
        line = line.decode('utf8')
        parts = line.split('#####')
        
        parts.pop(0)
        for part in parts:
            info = part.split('\t')
            geoId = info[0]
            lat = info[4]
            long = info[5]
            geoId2Coords[geoId] = [lat, long]
    
    geoFile.close()





def getOtherInfo(birthLoc, infoList):
    
    otherLocs = []
    for info in infoList:
        if not info == birthLoc and '#' in info:
            pInfo = info.split('#')
            for gId in pInfo:
                if gId.isdigit():
                    if int(gId) > 2000:
                        otherLocs.append(gId)
    return otherLocs

def calculateDistance(loc1, loc2):
    
    
    coords1 = geoId2Coords.get(loc1)
    coords2 = geoId2Coords.get(loc2)
    if coords1 and coords2:
        lat1 = float(coords1[0])
        long1 = float(coords1[1])
    
        lat2 = float(coords2[0])
        long2 = float(coords2[1])
    
        long1, lat1, long2, lat2 = map(radians, [long1, lat1, long2, lat2])
    
    
        dlon = long2 - long1
        dlat = lat2 - lat1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
    
        # 6367 km is the radius of the Earth
        km = 6367 * c
    elif coords1:
        #if coords2 is problem: we can ignore it
        km = 0
    elif coords2:
        #if coords1 is the problem, it should not be the one to provide the final distance
        km = 5000000
    return km




def calculateAveDis(loc, locList):
    totalDistance = 0
    totalLocs = 0
    for cLoc in locList:
        distance = calculateDistance(loc, cLoc)
        totalDistance += distance
        totalLocs += 1
    if totalLocs > 0:
        avDist = totalDistance/float(totalLocs)
    else:
        avDist = 0
    return avDist
    #get coords location
    #for loc in locList, get coords, calculate distance
    #return average

def disambiguateLoc(birthLoc, infoList):
    bLocCands = birthLoc.split('#')
    locName = bLocCands.pop(0)
    otherLocs = getOtherInfo(birthLoc, infoList)
    #start with distance bigger than possible
    smallestDistance = 500000
    bestLoc = ''
    for bLoc in bLocCands:
        if bLoc.isdigit():
            avDist = calculateAveDis(bLoc, otherLocs)
            if avDist < smallestDistance:
                smallestDistance = avDist
                bestLoc = bLoc
    locName += '#' + bestLoc
    return locName

initiate_geoDict()





birthCount = 0
bapCount = 0
noBirthInfo = 0
deathCount = 0
funeralCount = 0
lastWorkPlace = 0
noDeathInfo = 0

birthLocs = []
deathLocs = []
distances = []

aCount = 0

myLargestDistance = 0
distantCities = ''

for line in my_input:
    info = line.split('\t')
    if len(info) < 11:
        print 'Error: Something wrong with entry', line
    else:
        birthLoc = info[2]
        birthFound = ''
        if not 'UNKNOWN' in birthLoc:
            birthCount += 1
            if birthLoc.count('#') == 1:
                birthLocs.append(birthLoc)
            else:
                birthLoc = disambiguateLoc(birthLoc, info)
                birthLocs.append(birthLoc)
            birthFound = birthLoc
        elif not 'UNKNOWN' in info[4]:
            bapLoc = info[4]
            bapCount += 1
            if bapLoc.count('#') == 1:
                birthLocs.append(bapLoc)
            else:
                bapLoc = disambiguateLoc(bapLoc, info)
                birthLocs.append(bapLoc)
            birthFound = bapLoc
        else:
            noBirthInfo += 1
        deathLoc = info[6]
        deathFound = ''
        if not 'UNKNOWN' in deathLoc:
            if 'Amsterdam' in deathLoc:
                aCount += 1
            deathCount += 1
            if deathLoc.count('#') == 1:
                deathLocs.append(deathLoc)
            else:
                deathLoc = disambiguateLoc(deathLoc, info)
                deathLocs.append(deathLoc)
            deathFound = deathLoc
        elif not 'UNKNOWN' in info[8]:
            funeralCount += 1
            funLoc = info[8]
            if funLoc.count('#') == 1:
                deathLocs.append(funLoc)
            else:
                funLoc = disambiguateLoc(funLoc, info)
                deathLocs.append(funLoc)
            deathFound = funLoc
        else:
            workInfo = info[11]
            latestWork = workInfo.split('|')[-1]
            lWorkLoc = latestWork.split('*')[0]
            if lWorkLoc.count('#') == 0:
                noDeathInfo += 1
            elif lWorkLoc.count('#') == 1:
                lastWorkPlace += 1
                deathLocs.append(lWorkLoc)
                deathFound = lWorkLoc
            else:
                lWorkLoc = disambiguateLoc(lWorkLoc, info)
                deathLocs.append(lWorkLoc)
                deathFound = lWorkLoc
                lastWorkPlace += 1


        if deathFound and birthFound:
            dId = deathFound.split('#')[1]
            bId = birthFound.split('#')[1]
            if dId.isdigit() and bId.isdigit():
                bDeathDistance = calculateDistance(bId, dId)
                if bDeathDistance > myLargestDistance:
                    myLargestDistance = bDeathDistance
                    distantCities = birthFound + '-' + deathFound
                distances.append(bDeathDistance)

print myLargestDistance, distantCities
#print len(birthLocs), birthCount, bapCount, noBirthInfo
#print len(deathLocs), deathCount, funeralCount, noDeathInfo

print aCount, 'died in Amsterdam'
#create dictionaries with stats
birthDict = {}
for bLoc in birthLocs:
    if bLoc in birthDict:
        birthDict[bLoc] += 1
    else:
        birthDict[bLoc] = 1


deathDict = {}
for dLoc in deathLocs:
    if dLoc in deathDict:
        deathDict[dLoc] += 1
    else:
        deathDict[dLoc] = 1


#get Distance stats
largestDist = 0
totDist = 0
zeroKM = 0
for myDist in distances:
    if myDist == 0:
        zeroKM += 1
    totDist += myDist
    if myDist > largestDist:
        largestDist = myDist
dNumb = len(distances)
averageDistance = largestDist/float(dNumb)

print 'Found distance between birth and death for', dNumb
print 'Largest distance', largestDist
print 'Average distance', averageDistance
print zeroKM, 'priests died in their place of birth '

boutfile = open('birthLocStats.tsv','w')

for k, v in sorted(birthDict.iteritems(), key=operator.itemgetter(1), reverse=True):
    boutfile.write(k + '\t\t' + str(v) + '\n')

boutfile.close()
doutfile = open('deathLocStats.tsv','w')

for k, v in sorted(deathDict.iteritems(), key=operator.itemgetter(1), reverse=True):
    doutfile.write(k + '\t\t' + str(v) + '\n')

doutfile.close()





