#!/usr/bin/python
# -*- coding: utf-8 -*-

from ftfy import *
from math import radians, cos, sin, asin, sqrt

inputfile = open('repertoriumantske.txt','r')
geoFilename = 'geoLieburgCorpus.txt'
alternative_output = open('alternativepreds.txt', 'w')
my_output = open('priest_info_all_ids.tsv','w')




#dictionary of month names and their values for normalization
months = {'jan' : '01', 'febr' : '02', 'maart' : '03', 'april' : '04', 'mei' : '05', 'juni' : '06', 'juli' : '07', 'aug' : '08', 'sept' : '09', 'okt' : '10', 'nov' : '11', 'dec' : '12'}

#dictonary with commonly used abbreviations and alternative (old Dutch) names
provinces = {'ZH' : 'Zuid-Holland', 'Gr' : 'Groningen', 'Fr' : 'Friesland', 'Zld':'Zeeland', 'Gld':'Gelderland', 'NBr' : 'Noord-Brabant', 'Ov': 'Overijssel', 'Dr' : 'Drente', 'Li':'Limburg', 'NH' : 'Noord-Holland', 'Ut':'Utrecht','Palts':'Pfalz','Waals':u'Wallonië', u'Oost-Indië' : u'Indonesië'}

countryCodes = {'Frankrijk' : 'FR', 'FR' : 'FR'}

#list of terms that are indicators standardly used in the corpus
#separate check for pred (has several variations), not included here

##FIXME: this list should be much longer: see if we can identify these terms automatically
corpusTerms = ['ca.','Geb.','Gedoopt','overl.','begraven','emer.','ber.','en','in','afgezet', 'neergelegd', 'de']


geoDict = {}

geoId2Country = {}

geoId2Coords = {}


#verification files
caFile = open('circaCheck.txt', 'w')
dateChecking = open('dateCheck.txt', 'w')
UpperNotGeo = open('UppercasedNotInGeo.txt','w')
LowerNotGeo = open('LowercasedNotInGeo.txt','w')
LatestLower = open('LowercasedNotInGeo2.txt','w')




def initiate_geoDicts():
    global geoId2Country, geoFile, geoId2Coords, geoDict
    count3 = 0
    geoFile = open(geoFilename, 'r')
    for line in geoFile:
        line = line.decode('utf8')
        parts = line.split('#####')
        
        locName = parts.pop(0)
        infoline = line.replace(locName + '#####', '')
        geoDict[locName] = infoline
        
        for part in parts:
            info = part.split('\t')
            geoId = info[0]
            lat = info[4]
            long = info[5]
            geoId2Coords[geoId] = [lat, long]
            
            country = info[8]
            
            if geoId in geoId2Country:
                if not geoId2Country.get(geoId) == country:
                    print 'Error:', geoId, 'has contradicting information of country',geoId2Country.get('geoId'), country
            else:
                geoId2Country[geoId] = country
    geoFile.close()



def createCountriesWithLoc(geos):
    countryGeo = {}
    
    for geo in geos:
        
        country = geoId2Country.get(geo)
        if country:
            if country in countryGeo:
                countryGeo[country].append(geo)
            else:
                countryGeo[country] = [geo]

    return countryGeo


def apply_heuristics(geoIds, cCode = ''):
    
    geos = geoIds.split('#')
    countryGeo = createCountriesWithLoc(geos)
    if cCode and cCode in countryGeo:
        return countryGeo.get(cCode)
    elif 'NL' in countryGeo:
        return countryGeo.get('NL')
    elif 'BE' in countryGeo:
        return countryGeo.get('BE')
    elif 'DE' in countryGeo:
        return countryGeo.get('DE')
    elif 'FR' in countryGeo:
        return countryGeo.get('FR')
    elif 'ID' in countryGeo:
        return countryGeo.get('ID')
    elif 'SR' in countryGeo:
        return countryGeo.get('SR')
    elif 'MF' in countryGeo:
        return countryGeo.get('MF')
    elif 'GB' in countryGeo:
        return countryGeo.get('GB')
    elif 'BR' in countryGeo:
        return countryGeo.get('BR')
    elif 'FI' in countryGeo:
        return countryGeo.get('FI')



def calculateDistance(loc1, loc2):
    
    
    coords1 = geoId2Coords.get(loc1)
    coords2 = geoId2Coords.get(loc2)
    
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
    return km

def compareDistance(list1, list2):
    '''retrieves coordinates of two lists of geographic locations and returns a list containing the two identifiers of the locations that are geographically closest'''
    shortest = []
    #set shortest dist to more than possible shortest distance on earth
    
    shortest_dist = 50000000
    for loc1 in list1:
        if loc1 and loc1.isdigit():
            for loc2 in list2:
                if loc2 and loc2.isdigit():
                    distance = calculateDistance(loc1, loc2)
                    if distance < shortest_dist:
                        shortest = [loc1, loc2]
                        shortest_dist = distance
  
    return shortest


def identify_overlap_or_closests(geoIds,specIds):
    geoIds = geoIds.split('#')
    
    specIds = specIds.split('#')
    
    countrySpecs = createCountriesWithLoc(specIds)
    countryGeos = createCountriesWithLoc(geoIds)
    
    both = []
    for key in countrySpecs.keys():
        
        if key in countryGeos:
            both.append(key)
    if len(both) == 1:
        geos = countryGeos.get(both[0])
        if len(geos) > 1:
            specs = countrySpecs.get(both[0])
            closest = compareDistance(geos, specs)
        else:
            closest = geos
    else:
        #FIXME: check if these are also lists
        
        closest = compareDistance(geoIds, specIds)
    
    if len(closest) > 0:
        return [closest[0]]
    else:
        newList = []
        for geo in geoIds:
            if geo:
                newList.append(geo)
        return newList


def disambiguateLocation(geoIdsLoc, specification):
    if specification:
        if specification in countryCodes:
            cCode = countryCodes.get(specification)
            
            geoIdList = apply_heuristics(geoIdsLoc, cCode)
        else:
            #fixing a commonly occurring mistake with a hack
            if 'Brabant' in specification and 'Antwerpen' in geoIdsLoc:
                geoIdList = apply_heuristics(geoIdsLoc)
            else:
                specId = get_geoId(specification)
                geoIdList = identify_overlap_or_closests(geoIdsLoc, specId)
                if len(geoIdList) > 1:
                    geoString = ''
                    for g in geoIdList:
                        geoString += g + '#'
                    geoString = geoString.rstrip('#')
                    geoIdList = apply_heuristics(geoString)
    else:
        geoIdList = apply_heuristics(geoIdsLoc)
    cleanedGeoList = []
    if geoIdList:
        for gId in geoIdList:
            if gId.isdigit():
                cleanedGeoList.append(gId)
    else:
        return geoIdList
    return cleanedGeoList


def is_year(inString):
    inString = inString.lstrip('~').rstrip('.<')
    if inString.isdigit():
        myYear = int(inString)
        if 1000 < myYear < 2015:
            return inString
        else:
            return False
    else:
        return False


def is_month(inString):
    global months
    inString = inString.rstrip('.')
    if inString in months:
        return months.get(inString)
    else:
        return False


def is_day(inString):
    if inString.isdigit():
        myDay = int(inString)
        if 0 < myDay < 32:
            return inString
        else:
            return False
    else:
        return False


def convertDate(dateString):
    # print dateString
    dateString = dateString.replace('~','')
    myList = dateString.split()
    date = 'yyyy-mm-dd'
    #reverse the list then check if 1st element is year, 2nd is month, 3rd is day
    #end_token = myList[1].rstrip('.<')
    day = ''
    month = ''
    year = ''
    for token in myList:
        token = token.replace(';','')
        token = token.replace(',','')
        token = token.rstrip('.<')
        if year:
            break
        elif not month:
            day = is_day(token)
            if day:
                date = date.replace('dd', day)
            
            else:
                month = is_month(token)
                if month:
                    date = date.replace('mm',month)
                else:
                    year = is_year(token)
                    if year:
                        date = date.replace('yyyy',year)
                    else:
                        dateChecking.write(token.encode('utf8') + '\n')
        else:
            month = is_month(token)
            if month:
                date = date.replace('mm',month)
            else:
                year = is_year(token)
                if year:
                    date = date.replace('yyyy',year)
                else:
                    dateChecking.write(token.encode('utf8') + '\n')
    
    
    
    return date




def is_loc(inString):
    strippedString = inString.rstrip('.')
    if not is_year(strippedString) and not is_month(strippedString) and not is_day(strippedString):
        if not 'ca.' in inString and not inString == '-':
            return True
        else:
            caFile.write(inString + '\n')
    return False


def cleanToken(token):
    token = token.replace('~','')
    token = token.replace('<','')
    token = token.replace('.','')
    token = token.replace(',','')
    token = token.replace(')','')
    token = token.replace(']','')
    token = token.replace(';','')
    token = token.replace('?','')
    token = token.replace('(','')
    token = token.replace('[','')
    token = token.replace('/','')
    token = token.replace('\\','')
    token = token.replace('"','')
    token = token.replace(':','')
    token = token.replace('= ','')
    token = token.replace('@','')
    token = token.replace('#','')
    token = token.rstrip().lstrip()
    return token



def retrieve_geoIds(geoInfo):
    geoEntries = geoInfo.split('#####')
    geoId = ''
    for gEnt in geoEntries:
        gParts = gEnt.split('\t')
        if not gParts[0] in geoId:
            geoId += '#' + gParts[0]
    return geoId

def get_geoId(place):
    geoId = ''
    if place in geoDict:
        geoInfo = geoDict.get(place)
        geoId = retrieve_geoIds(geoInfo)
    elif place:
        
        geoId = '#NOGEOID'


    return geoId


def createDate(year, month, day):
    date = ''
    if year:
        date += year
    else:
        return 'UNKNOWN'
    if month:
        date += '-' + month
        #we don't do day + year without indicating the month
        if day:
            date += '-' + day

    return date


def average_year(toks):
    if is_year(toks[1]):
        diffYear = int(toks[1]) - int(toks[0])
        if diffYear > 6:
            print toks

        else:
            av = (int(toks[1]) + int(toks[0]))/2
            return str(av)
    elif toks[1].isdigit():
        if int(toks[1]) < 100:
            toks[1] = toks[0][1] + toks[0][2] + toks[1]

            diffYear = int(toks[1]) - int(toks[0])
            if diffYear > 6:
                print toks
            else:
                av = (int(toks[1]) + int(toks[0]))/2
                return str(av)


##FIX ME: ALTERNATIVE DATES SEPARATED BY A SLASH
def retrieveDate(tokens):
    #date is always at the end
    tokens.reverse()
    year = ''
    month = ''
    day = ''
    new_tokens = []
    for token in tokens:
        datetoken = token.rstrip(')').lstrip('(').rstrip(';').rstrip(',')
        if '/' in token:
            token = token.replace('.<','')
            token = token.replace('~','')
            toks = token.split('/')
            if is_year(toks[1]):
                avyear = average_year(toks)
                if avyear:
                    year = avyear
        #check if not finding out a different category
        if datetoken in ['gedoopt', 'begraven','overl.','geb.','emer.','verdreven']:
            break
        if is_year(datetoken):
            if year:
                if 'tot' in tokens:
                    year = is_year(datetoken)
                elif not 'of' in tokens:
                    print tokens, 'more than one year'
            else:
                year = is_year(datetoken)
        elif is_month(datetoken):
            if month:
                if 'tot' in tokens:
                    month = is_month(datetoken)
                elif not 'of' in tokens:
                    print tokens, 'more than one month'
            else:
                month = is_month(datetoken)
        elif is_day(datetoken):
            if day:
                if not 'of' in tokens and not 'tot' in tokens:
                    print tokens, 'more than one day'
            else:
                day = is_day(datetoken)
        elif not datetoken in ('ca.', 'voor', 'begin','na'):
            new_tokens.append(token)
    
    date = createDate(year, month, day)
    new_tokens.reverse()
    new_tokens.append(date)
    return new_tokens


def removeAdditionalIndicators(potLoc):
    if 'bij ' in potLoc:
        potLoc = potLoc.replace('bij ', '')
    if 'verm ' in potLoc:
        potLoc = potLoc.replace('verm ', '')
    if 'verm. ' in potLoc:
        potLoc = potLoc.replace('verm. ', '')
    if 'of ' in potLoc:
        potLoc = potLoc.replace('of ', '')
    if 'in ' in potLoc:
        potLoc = potLoc.replace('in ', '')
    if 'omgeving ' in potLoc:
        potLoc = potLoc.replace('omgeving ', '')
    if 'tot ' in potLoc:
        potLoc = potLoc.replace('tot ', '')

    return potLoc


def print_out_error(placeString, locname):
    if placeString[0].isupper():
        UpperNotGeo.write(placeString.encode('utf8') + ';;;' + locname.encode('utf8') + '\n')
    elif not placeString.isdigit():
        LowerNotGeo.write(placeString.encode('utf8')  + ';;;' + locname.encode('utf8') + '\n')


###FIXME: special cases that go wrong
def getPlaceWithGeo(potLoc, loc_name):
    if 'of ' in potLoc and not 'hof ' in potLoc:
        newPlace = '*OR*'
    else:
        newPlace = ''
    potLoc = removeAdditionalIndicators(potLoc)
    potLoc = cleanToken(potLoc)
    
    newPlace += potLoc
    geoId = get_geoId(potLoc)
    newPlace += geoId
    return newPlace

def identify_Locations(tokens):
    
    loc_name = ''
    place = ''
    for tok in tokens:
        loc_name += tok + ' '
    locString = loc_name.rstrip(' ')
    #check if specification
    if ' of ' in locString or '(of ' in locString:
        parts = locString.split('of ')
    
        for part in parts:
            potLoc = cleanToken(part)
            if is_loc(potLoc):
                newPlace = getPlaceWithGeo(potLoc, loc_name)
                place += newPlace + '*OR*'
        place = place.rstrip('*OR*')
        allLocs = place.split('*OR*')
        if len(allLocs[0].split('#')) > 2 and len(allLocs) > 1:
            loc1 = allLocs[0]
            loc2 = allLocs[1]
            disLocs = disambiguateLocation(loc1, loc2)
            name1 = loc1.split('#')[0]
            if disLocs:
                geoId = ''
                for dl in disLocs:
                    geoId += '#' + dl
                place = name1 + geoId + '*OR*'
        elif len(place.split('#')) > 2:
            disLoc = disambiguateLocation(place, '')
            name = place.split('#')[0]
            if disLoc:
                geoId = ''
                for dl in disLoc:
                    geoId += '#' + dl
                place = name + geoId
    elif '(' in locString:
        parts = locString.split('(')
        mainLoc = parts.pop(0)
        mainLoc = cleanToken(mainLoc)
        if is_loc(mainLoc):
            mainLoc = getPlaceWithGeo(mainLoc, loc_name)
            if len(mainLoc.split('#')) > 2:
                place = mainLoc.split('#')[0]
                specLoc = parts[0].split(')')[0]
                
                if not specLoc == '?':
                    if specLoc in provinces:
                        specLoc = provinces.get(specLoc)
                    if ',' in specLoc:
                        specLoc = specLoc.split(',')[0].rstrip()
                    
                    disLocs = disambiguateLocation(mainLoc, specLoc)
                else:
                    disLocs = disambiguateLocation(mainLoc, '')
                if not disLocs:
                    print mainLoc.encode('utf8'), locString.encode('utf8')
                for dL in disLocs:
                    place += '#' + dL
            else:
                place = mainLoc
#FIXME: we'll go for two options: 1. ignore any entry that has 'of' in it, 2. only take the first of the two

    elif is_loc(locString):
        locString = cleanToken(locString)
        place = getPlaceWithGeo(locString, loc_name)
        
        nameGeos = place.split('#')
        if len(nameGeos) > 2:
            name = nameGeos.pop(0)
            disGeos = disambiguateLocation(place, '')
            
            place = name
            if not disGeos:
                print place, nameGeos
            for geoId in disGeos:
                place += '#' + geoId
    if '#NOGEOID' in place and place[0].islower():
        if len(place.split()) > 1:
            finalString = place.split()[-1]
            if is_loc(finalString) and finalString[0].isupper():
                place = getPlaceWithGeo(finalString, loc_name)
                nameGeos = place.split('#')
                if len(nameGeos) > 2:
                    name = nameGeos.pop(0)
                    disGeos = disambiguateLocation(place, '')
        
                    place = name
                    if not disGeos:
                        print place, nameGeos
                    for geoId in disGeos:
                        place += '#' + geoId
        else:
            LatestLower.write(place.encode('utf8') + '\n')
            place = ''
    return place

def get_dateLocInfo(info, dString):
    info_ps = info.split(dString)
    if len(info_ps) > 1:
        ip = info_ps[1]
        #FIXME: SOME HAVE BOTH BIRTH AND BAPTIZE, THEN MAKE SURE NO MIXUP
        if dString in ['Geb.', 'Gedoopt','gedoopt','emer.']:
            rel_ip = ip.split(';')[0]
            if not ';' in ip and dString in ['Geb.', 'Gedoopt','gedoopt']:
                rel_ip = ip.split('pred')[0]
            if 'overl.' in rel_ip:
                rel_ip = rel_ip.split('overl.')[0]
        
        else:
            rel_ip = ip
        tokens = rel_ip.split()
        #returns tokens with interpreted date as last element
        updatedToks = retrieveDate(tokens)
        date = updatedToks.pop()
        place = identify_Locations(updatedToks)
       
        return [date,place]
    else:
        return ['','']


def get_dateLocInfo_old(info, dString):
    info_ps = info.split(dString)
    if len(info_ps) > 1:
        ip = info_ps[1]
        ipnoloc = ip
        dInfo = ip.split()
        loc_candidate = dInfo[0]
        if 'verm.' in loc_candidate:
            loc_candidate = dInfo[1]
        if is_loc(loc_candidate):
            place = loc_candidate
            if not place == '-':
                place = cleanToken(place)
                geoId = get_geoId(place)
                place += geoId
                ipnoloc = ip.replace(loc_candidate, '')
                if geoId == 'NOGEOID':
                    if place[0].isupper():
                        UpperNotGeo.write(place.encode('utf8') + ';;;' + ip.encode('utf8') + '\n')
                    elif not place.isdigit():
                        LowerNotGeo.write(place.encode('utf8')  + ';;;' + ip.encode('utf8') + '\n')
            else:
                place = ''
        else:
            place = ''
        date = convertDate(ipnoloc)
        return [date, place]
    else:
        return ['','']



def getPriesthoodDates(dateString):
    if ' tot ' in dateString:
        dates = dateString.split('tot')
        bDate = convertDate(dates[0])
        eDate = convertDate(dates[1])
        date = bDate + '*' + eDate
    else:
        date = convertDate(dateString)
    
    return date


def retrievePredicantParts(inputString):
    #cut of irrelevant info
    relevantI = inputString.split(',')[0]
    if '#' in relevantI:
        cityDate = relevantI.split('#')
        location = cityDate[0]
        if '(' in location:
            parts = location.split('(')
            geoLoc = parts[0]
            geoLoc = cleanToken(geoLoc)
            spec = parts[1].rstrip(')')
            
            geoId = get_geoId(geoLoc)
            if len(geoId.split('#')) > 2:
                spec = removeAdditionalIndicators(spec)
                if spec in provinces:
                    spec = provinces.get(spec)
                if not spec == '?':
                    disIds = disambiguateLocation(geoId, spec)
                    
                    geoId = ''
                    for gId in disIds:
                        geoId += '#' + gId
            location += geoId
        else:
            geoId = get_geoId(location)
            if len(geoId.split('#')) > 2:
                geoIdList = disambiguateLocation(geoId, '')
                if not geoIdList:
                    print location, geoId
                geoId = ''
                
                
                for gId in geoIdList:
                    geoId += '#' + gId
        
            location += geoId
            if geoId == '#NOGEOID':
                print location.encode('utf8'), inputString.encode('utf8')
                print_out_error(location, inputString)
        date =  getPriesthoodDates(cityDate[1])
        return location + '*' + date
    else:
        print 'Error: illformed predicant information', inputString
        return False


def retrievePredicantPartsFromIn(job):
    relevantI = job.split(',')[0]
    relevantI = relevantI.split(';')[0]
    parts = relevantI.split()
    location = parts.pop(0)
    #get geoId
    geoId = get_geoId(location)
    location += geoId
    if geoId == '#NOGEOID':
        print_out_error(location, job)
    dateString = ''
    for p in parts:
        dateString += p + ' '
    date = getPriesthoodDates(dateString)
    return location + '*' + date




def get_predicantInfo(info):
    otherInfoCats = ['verdreven','emer','overl','begraven']
    predicant_jobs = []
    if ' pred.' in info:
        #if not info.split(' pred.')[1] == info.split('pred.')[1]:
        #    alternative_output.write(info + '\n')
        if ' pred.' in info:
            preds = info.split('pred.')
            preds.pop(0)
            for predPart in preds:
                if '@' in predPart:
                    predInfo = predPart.split('@')
                    #information starts after first @ sign
                    predInfo.pop(0)
                    for job in predInfo:
                        locDate = retrievePredicantParts(job)
                       
                        if locDate:
                            predicant_jobs.append(locDate)
                        else:
                            print info
                elif ' in ' in predPart:
                    #print 'INININININININ'
                    predInfo = predPart.split(' in ')
                    #information starts after first @ sign
                    predInfo.pop(0)
                    job = predInfo[0]
                    locDate = retrievePredicantPartsFromIn(job)
                    if locDate:
                        predicant_jobs.append(locDate)
                    else:
                        print info
                #for job in predInfo:
                #locDate = retrievePredicantParts(job)
                #predicant_jobs.append(locDate)
                else:
                    #make sure we don't mix up dates with events after the jov
                    for cat in otherInfoCats:
                        if cat in predPart:
                            predPart = predPart.split(cat)[0]
                            #categories are ordered chronologically, we need the first
                            break
                
                    tokens = predPart.split()
                    
                    #returns tokens with interpreted date as last element
                    updatedToks = retrieveDate(tokens)
                    
                    date = updatedToks.pop()
                    
                    place = identify_Locations(updatedToks)
                    locDate = place + '*' + date
                    predicant_jobs.append(locDate)
#alternative_output.write(info.encode('utf8') + '\n')
    elif 'pred.' in info:
        alternative_output.write(info.encode('utf8') + '\n')
    else:
        print 'Uncommon entry\n', info, '\nseems to have no information on where the person was a priest'
    
    return predicant_jobs



#1. get place of birth + GeoName Location, else print out error
#2. get place of death + GeoName Location, else print out error
#3. get other standard formed locations + GeoName, else print out error
#4. print out what remains and find solution for that



def appendDataFrom1List(predList, outline):
    newInfo = ''
    for job in predList:
        newInfo += job.encode('utf8') + '|'
    newInfo = newInfo.rstrip('|')
    outline += newInfo
    return outline


def appendDataFrom2List(myList, myString):
    for tok in myList:
        if tok:
            myString += tok.encode('utf8') + '\t'
        else:
            myString += 'UNKNOWN\t'
    return myString



def getDateInfo(info, dString):
    #variant for categories that only have date (emer. verdreven)
    info_ps = info.split(dString)
    
    
    if len(info_ps) > 1:
        ip = info_ps[1]
        rel_ip = ip.split(';')[0]
    
        tokens = rel_ip.split()
        #returns tokens with interpreted date as last element
        updatedToks = retrieveDate(tokens)
        date = updatedToks.pop()
        
        return date
    else:
        return ''
#list of entries
entries = []


#file consists of one line, where each entry begins with '>'
for line in inputfile:
    entries = line.split('>')

allLocs = set()
count = 0
initiate_geoDicts()


def replace_oldnameIndonesia(info, oi):
    
    oldString = oi.decode('utf8')
    newString = 'Indonesië'.decode('utf8')
    
    info = info.replace(oldString,newString)
    return info

def appendString(infoString, outline):
    if infoString:
        outline += infoString.encode('utf8') + '\t'
    else:
        outline += 'UNKNOWN\t'
    return outline

print len(entries)
for entry in entries:
    count += 1
    entry_parts = entry.split('|')
    if len(entry_parts) > 1:
        #first part is name, we do not want to associate those with locations
        name = entry_parts[0].decode('mac-roman')
        info = entry_parts[1].decode('mac-roman')
        #fix Oost-Indië
        oi = 'Oost-Indië'
        if oi in info.encode('utf8'):
            info = replace_oldnameIndonesia(info, oi)
        if 'Gulik' in info:
            info = info.replace('Gulik','Julich')
        bDate_place = get_dateLocInfo(info, 'Geb.')
        if 'Gedoopt' in info:
            bapDate_place = get_dateLocInfo(info, 'Gedoopt')
        else:
            #if neither is present, this will set baptize date and location to UNKNOWN
            bapDate_place = get_dateLocInfo(info, 'gedoopt')
        dDate_place = get_dateLocInfo(info, 'overl.')
        fDate_place = get_dateLocInfo(info, 'begraven')
        eDate = getDateInfo(info, 'emer.')
        vDate = getDateInfo(info, 'verdreven')
        predInfo = get_predicantInfo(info)
        outline = name.encode('utf8') + '\t'
        outline = appendDataFrom2List(bDate_place, outline)
        outline = appendDataFrom2List(bapDate_place, outline)
        outline = appendDataFrom2List(dDate_place, outline)
        outline = appendDataFrom2List(fDate_place, outline)
        outline = appendString(eDate, outline)
        outline = appendString(vDate, outline)
        outline = appendDataFrom1List(predInfo, outline)
        outline += '\n'
        my_output.write(outline)
#print name.encode('utf8') + '\t' + bDate_place[0].encode('utf8') + '\t' + bDate_place[1].encode('utf8')

#   if count > 500:
#        break
