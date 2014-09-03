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


def getShortestLongestAvNr(distanceList):
    shortest = distanceList[0]
    longest = distanceList[0]
    total = 0
    for distance in distanceList:
        total += distance
        if distance > longest:
            longest = distance
        if distance < shortest:
            shortest = distance
    average = total/float(len(distanceList))
    return str(shortest) + ',' + str(longest) + ',' + str(average) + ',' + str(len(distanceList))



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
    #return which ever is not the problem
    elif coords1:
        km = loc2
    elif coords2:
        km = loc1

    return km






def retrieveWorkTowns(wList):
    myLocs = []
    positions = wList.split('|')
    for pos in positions:
        loc = pos.split('*')[0]
        if not 'UNKNOWN' in loc and not loc == 'OR':
            myLocs.append(loc)
    return myLocs


def find_shortestDist_andId(startLoc, loc):
    sIds = startLoc.split('#')
   
    sName = sIds.pop(0)
    eIds = loc.split('#')
    eName = eIds.pop(0)
    sDist = 10000000000000000
    myId = ''
    #if original has no geoLoc info, return next location
    if 'NOGEOID' in sIds:
        return [0, loc]
    #if next loc has no Geo Information, skip it
    if 'NOGEOID' in eIds:
        return [0, startLoc]
    for loc1 in sIds:
        loc1 = loc1.split('*OR*')[0]
        if not 'NOGEOID' in loc1:
            if int(loc1) > 2000:
                for loc2 in eIds:
                    loc2 = loc2.split('*OR*')[0]
                    if loc2 > 2000:
                        distance = calculateDistance(loc1, loc2)
                        if isinstance(distance, float):
                        
                            if distance < sDist:
                                sDist = distance
                                myId = eName + '#' + loc2
                        else:
                            #if distance is not float, it returns the location that did not cause the problem
                            if sDist == 10000000000000000:
                                if distance == loc:
                                
                                    myId = startLoc
                                elif distance == loc2:
                                    myId = loc
    if sDist == 10000000000000000:
        #print startLoc,loc
        return [0,myId]
    return [sDist, myId]


def calculateTravelings(locList):
    
    mySpecCase = False
    if 'Bremen#2944390' in locList and 'Pijnacker#2748591' in locList:
        mySpecCase = True
    startLoc = locList.pop(0)
    totaldistance = 0
    for loc in locList:
        if mySpecCase:
            print totaldistance, startLoc, loc
        lname = loc.split('#')[0]
        shortDistId = find_shortestDist_andId(startLoc, loc)
        if 'Bremen' in startLoc and 'Pijnacker' in loc:
            print shortDistId
        #mySpecCase = True
        if 'Pijnacker' in startLoc and 'Naaldwijk' in loc:
            print shortDistId
        #set loc to new location as used in distance calculation
        if shortDistId[1]:
            startLoc = shortDistId[1]
        
        distance = shortDistId[0]
        if mySpecCase:
            print totaldistance, distance
        totaldistance += distance
        if mySpecCase:
            print totaldistance
    return totaldistance

initiate_geoDict()

birthDecades = {}
deathDecades = {}

tot_traveled = []

for line in my_input:
    info = line.split('\t')
    if len(info) < 11:
        print 'Error: Something wrong with entry', line
    else:
        locList = []
        #first location: birth or baptize
        #second: work locations
        #third: death or funeral locations (report if very different)
        startLoc = info[2]
        if not 'UNKNOWN' in startLoc:
            
            locList.append(startLoc)
        #if no birthlocation, but baptize location is known, we start there
        elif not 'UNKNOWN' in info[4]:
            locList.append(info[4])
        workLocList = info[11]
        workLocs = retrieveWorkTowns(workLocList)
        for wLoc in workLocs:
            locList.append(wLoc)

        #location of death
        endLoc = info[6]
        if not 'UNKNOWN' in endLoc:
            locList.append(endLoc)
        #if place of death is unknown but place of funeral is not...
        elif not 'UNKNOWN' in info[8]:
            locList.append(info[8])

        traveled = calculateTravelings(locList)

        tot_traveled.append(traveled)
        bDate = info[1]
        bDecade = ''
        if not 'UNKNOWN' in bDate:
            bDecade = bDate[0] + bDate[1] + bDate[2] + '0'
        elif not 'UNKNOWN' in info[3]:
            bDate = info[3]
            bDecade = bDate[0] + bDate[1] + bDate[2] + '0'

        if bDecade:
            if bDecade in birthDecades:
                birthDecades[bDecade].append(traveled)
            else:
                birthDecades[bDecade] = [traveled]


        dDate = info[5]
        dDecade = ''
        if not 'UNKNOWN' in dDate:
            dDecade = dDate[0] + dDate[1] + dDate[2] + '0'
        elif not 'UNKNOWN' in info[7]:
            dDate = info[7]
            dDecade = dDate[0] + dDate[1] + dDate[2] + '0'

        if dDecade:
            if dDecade in deathDecades:
                deathDecades[dDecade].append(traveled)
            else:
                deathDecades[dDecade] = [traveled]
            if dDecade == '1570' and traveled > 9572:
                print line
                print locList

myOverallNumbers = getShortestLongestAvNr(tot_traveled)
print myOverallNumbers


birthDecMob = open('mobilityPerBirthDecade.csv','w')
deathDecMob = open('mobilityPerDeathDecade.csv','w')

def add_line_toDecadeFiles(startDate):
    key = str(startDate)
    if key in birthDecades:
        dists = birthDecades.get(key)
        numbers = getShortestLongestAvNr(dists)
        birthDecMob.write(key + ',' + numbers + '\n')
    else:
        birthDecMob.write(key + ',0,0,0,0\n')
    if key in deathDecades:
        dists = deathDecades.get(key)
        numbers = getShortestLongestAvNr(dists)
        deathDecMob.write(key + ',' + numbers + '\n')
    else:
        deathDecMob.write(key + ',0,0,0,0\n')




startDate = 1500


while startDate < 1900:
    add_line_toDecadeFiles(startDate)
    startDate += 10


deathDecMob.close()
birthDecMob.close()