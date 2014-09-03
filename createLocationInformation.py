#!/usr/bin/python
# -*- coding: utf-8 -*-

inputfile = open('repertoriumantske.txt','r')

#dictionary of month names and their values for normalization
months = {'jan' : '01', 'febr' : '02', 'maart' : '03', 'april' : '04', 'mei' : '05', 'juni' : '06', 'juli' : '07', 'aug' : '08', 'sept' : '09', 'okt' : '10', 'nov' : '11', 'dec' : '12'}

#dictonary with commonly used abbreviations and alternative (old Dutch) names
provinces = {'ZH' : 'Zuid-Holland', 'Gr' : 'Groningen', 'Fr' : 'Friesland', 'Zld':'Zeeland', 'Gld':'Gelderland', 'NBr' : 'Noord-Brabant', 'Ov': 'Overijssel', 'Dr' : 'Drente', 'Li':'Limburg', 'NH' : 'Noord-Holland', 'Ut':'Utrecht','Palts':'Pfalz','Waals':u'Wallonië', u'Oost-Indië' : u'Indonesië'}

#list of terms that are indicators standardly used in the corpus
#separate check for pred (has several variations), not included here
corpusTerms = ['ca.','Geb.','Gedoopt','overl.','begraven','emer.','ber.','en','in','afgezet', 'neergelegd', 'de']


#list of entries
entries = []


def findPotentialLocations(inString):
    location_parts = inString.split(',')
    for locPart in location_parts:
        my_parts = locPart.split(';')
        for part in my_parts:
            strippedPart = part.lstrip().rstrip()
            tokens = strippedPart.split()
            if len(tokens) == 1:
                return strippedPart
            else:
                if '- en ' in strippedPart:
                    locs = strippedPart.split('- en ')
                    return locs[1]
                else:
                    return strippedPart
    #split on comma or ;
    #remove standard terms


def check_forPotentialLocs(p):
    pLocs = []
    for token in p.split():
        if not token in corpusTerms and not token in months:
            token = cleanToken(token)
            if not token.isdigit():
                if token in provinces:
                    token = provinces.get(token)
                pLocs.append(token)
    return pLocs


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
    token = token.replace('Geb. ','')
    token = token.replace('= ','')
    token = token.replace('Geb ','')

    return token


def extractLocs(potLoc):
    locs = []
    if '#' in potLoc:
        #pure location information between @ and #
        location = potLoc.split('#')[0]
        #some have additional info on location
        if '(' in location:
            ls = location.split('(')
            for l in ls:
                if not ',' in l:
                    lc = l.rstrip(')').lstrip()
                    lc = cleanToken(lc)
                    if lc in provinces:
                        lc = provinces.get(lc)
                    locs.append(lc.rstrip())
                else:
                    for loc in l.split(','):
                        lc = loc.rstrip().lstrip()
                        lc = cleanToken(lc)
                        if lc in provinces:
                            lc = provinces.get(lc)
                        locs.append(lc)
        elif ',' in location:
            for loc in location.split(','):
                lc = loc.rstrip().lstrip()
                lc = cleanToken(lc)
                locs.append(lc)
        else:
            lc = location.rstrip().lstrip()
            lc = findPotentialLocations(lc)
            lc = cleanToken(lc)
            if ' en ' in lc:
                lcs = lc.split(' en ')
                for l in lcs:
                    locs.append(l)
            elif ' bij ' in lc:
                lcs = lc.split(' bij ')
                for l in lcs:
                    locs.append(l)
            locs.append(lc)
      
        parts = potLoc.split('#')
        parts.pop(0)
        for p in parts:
            mypotlocs = check_forPotentialLocs(p)
            for pL in mypotlocs:
                pL = cleanToken(pL)
                locs.append(pL)
    else:
        mypotlocs = check_forPotentialLocs(potLoc)
        for pL in mypotlocs:
            pL = cleanToken(pL)
            locs.append(pL)
    return locs
        #check for additional potential locations after #



def retrieve_potential_locations(infostring):
    
    myLocs = []
    #many locations have form @locname# add those first
    if '@' in infostring:
        potentialLocs = infostring.split('@')
        for potLoc in potentialLocs:
            myLocs = extractLocs(potLoc)
    elif '^' in infostring:
        potentialLocs = infostring.split('^')
        for potLoc in potentialLocs:
            myLocs = extractLocs(potLoc)
    else:
        myLocs = extractLocs(infostring)

    locInEntry = set(myLocs)


    return locInEntry


#file consists of one line, where each entry begins with '>'
for line in inputfile:
    entries = line.split('>')

allLocs = set()
for entry in entries:
    
    entry_parts = entry.split('|')
    if len(entry_parts) > 1:
        #first part is name, we do not want to associate those with locations
        entry_info = entry_parts[1].decode('mac-roman')
        locs = retrieve_potential_locations(entry_info)
        allLocs.update(locs)
    else:
        #just a check what illformed entries look like
        print entry


#go through geonames and see if any of the alternative names is in our set of potential locations
locGeoInfo = {}
geoNamesData = open('../GeoNames/allCountries.txt','r')

for line in geoNamesData:
    line = line.decode('utf-8')
    info = line.split('\t')
    knownNames = []
    if info[1]:
        knownNames.append(info[1])
    if info[2]:
        knownNames.append(info[2])
    additionalNames = info[3].split(',')
    for aN in additionalNames:
        if aN:
            knownNames.append(aN)
    for kN in knownNames:
        if kN in allLocs:
            if kN in locGeoInfo:
                locGeoInfo[kN].append(line)
            else:
                locGeoInfo[kN] = [line]


def startsWithCap(name):
    firstLet = name[0]
    if firstLet.upper() == firstLet:
        return True
    else:
        return False

notInGeo = open('notFoundInGeo.txt','w')
nocapnotInGeo = open('noCapnotFoundInGeo.txt','w')
geoInfo = open('geoLieburgCorpus.txt','w')

print len(allLocs)

for name in allLocs:
    if name:
        if not name in locGeoInfo:
            if not 'pred' in name:
                if startsWithCap(name):
                    notInGeo.write(name.encode('utf-8') + '\n')
                else:
                    nocapnotInGeo.write(name.encode('utf-8') + '\n')
        else:
            geoData = locGeoInfo.get(name)
            geoInput = ''
            for gD in geoData:
                gD = gD.rstrip('\n')
                geoInput += '#####' + gD
            writeOut = name + geoInput + '\n'
            geoInfo.write(writeOut.encode('utf-8'))


