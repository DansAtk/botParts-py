import sys
import os
import pathlib
import shutil

import sqlite3
import pytz
import calendar
from datetime import *

import config
from core.util import *
from core.commandM import command, request_queue

mSelf = sys.modules[__name__]
includes = {}
config.register(mSelf)
DB = config.database

class place:
    def __init__(self, ID, NAME=None, TRIGGER=':', TZ=None):
        self.id = ID
        self.name = NAME
        self.trigger = TRIGGER
        self.tz = TZ

    def now(self):
        if self.tz:
            return datetime.now(pytz.timezone(self.tz))
        
        else:
            return getTime()

def getPlace(placeID):
    if checkDB():
        conn = sqlite3.connect(DB)
        cursor = conn.cursor()
        cursor.execute(
                "SELECT name, trigger, tz FROM places WHERE id = ?",
                (placeID,)
                )
        result = cursor.fetchone()
        conn.close()
        
        if result:
            thisPlace = place(placeID)
            thisPlace.name = result[0]
            thisPlace.trigger = result[1]
            thisPlace.tz = result[2]

            return thisPlace
        
        else:
            return None

def tryGetOnePlace(placeString):
    thisPlace = None

    try:
        thisPlace = getPlace(int(placeString))

    except ValueError:
        searchResults = searchPlacebyName(placeString)
        
        if searchResults:
            if len(searchResults) == 1:
                thisPlace = searchResults[0]
    
    return thisPlace

def addPlace(profile):
    if checkDB():
        conn = sqlite3.connect(DB)
        cursor = conn.cursor()
        cursor.execute(
                "INSERT INTO places"
                "(id, name, trigger, tz) "
                "VALUES (?, ?, ?, ?)",
                (profile.id, profile.name, profile.trigger, profile.tz)
                )
        conn.commit()
        conn.close()

def removePlace(profile):
    if checkDB():
        conn = sqlite3.connect(DB)
        conn.execute("PRAGMA foreign_keys = 1")
        cursor = conn.cursor()
        cursor.execute(
                "DELETE FROM places "
                "WHERE id = ?",
                (profile.id,)
                )
        conn.commit()
        conn.close()

def updatePlace(profile):
    thisPlace = getPlace(profile.id)

    if thisPlace:
        if profile.name:
            thisPlace.name = profile.name
        if profile.trigger:
            thisPlace.trigger = profile.trigger
        if profile.tz:
            thisPlace.tz = profile.tz
        
        if checkDB():
            conn = sqlite3.connect(DB)
            cursor = conn.cursor()
            cursor.execute(
                    "UPDATE places SET "
                    "name = ?, trigger = ?, tz = ? "
                    "WHERE id = ?",
                    (thisPlace.name, thisPlace.trigger, thisPlace.tz, thisPlace.id)
                    )
            conn.commit()
            conn.close()

def searchPlacebyName(searchString):
    if checkDB():
        conn = sqlite3.connect(DB)
        cursor = conn.cursor()
        cursor.execute(
                "SELECT id "
                "FROM places "
                "WHERE name LIKE ?",
                ('%{}%'.format(searchString),)
                )
        search = cursor.fetchall()
        conn.close()

        if len(search) > 0:
            foundPlaces = []
            for result in search:
                thisPlace = getPlace(result[0])
                foundPlaces.append(thisPlace)

            return foundPlaces

        else:
            return None

def searchPlacebyTimezone(searchString):
    if checkDB():
        conn = sqlite3.connect(DB)
        cursor = conn.cursor()
        cursor.execute(
                "SELECT id "
                "FROM places "
                "WHERE tz LIKE ?",
                ('%{}%'.format(searchString),)
                )
        search = cursor.fetchall()
        conn.close()

        if len(search) > 0:
            foundPlaces = []
            for result in search:
                thisPlace = getPlace(result[0])
                foundPlaces.append(thisPlace)

            return foundPlaces

        else:
            return None

def registerCommands():
    global addPlaceC
    addPlaceC = command('place', addC)
    addPlaceC.description = 'Builds a place from parameters, then adds it to the database.'
    addPlaceC.instruction = 'Specify place attributes using \'Attribute=Value\' with each separated by a space. \'id\' is required.'
    addPlaceC.function = 'addPlaceF'
    addPlaceC.parent_module = mSelf
    global removePlaceC
    removePlaceC = command('place', removeC)
    removePlaceC.description = 'Removes a place from the database.'
    removePlaceC.instruction = 'Specify a place.'
    removePlaceC.function = 'removePlaceF'
    removePlaceC.parent_module = mSelf
    global editPlaceC
    editPlaceC = command('place', editC)
    editPlaceC.description = 'Updates an existing place with new attributes.'
    editPlaceC.instruction = 'First specify a place. Then, specify new attributes using \'Attribute=Value\' with each separated by a space.'
    editPlaceC.function = 'editPlaceF'
    editPlaceC.parent_module = mSelf
    global showPlaceC
    showPlaceC = command('place', showC)
    showPlaceC.description = 'Displays detailed information about a single place.'
    showPlaceC.instruction = 'Specify a place.'
    showPlaceC.function = 'showPlaceF'
    showPlaceC.parent_module = mSelf
    global listPlaceC
    listPlaceC = command('place', listC)
    listPlaceC.description = 'Lists all places in the database.'
    listPlaceC.function = 'listPlaceF'
    listPlaceC.parent_module = mSelf
    global findPlaceC
    findPlaceC = command('place', findC)
    findPlaceC.description = 'Searches for places meeting the given criteria.'
    findPlaceC.instruction = 'Specify a parameter.'
    findPlaceC.parent_module = mSelf
    global findPlaceNameC
    findPlaceNameC = command('name', findPlaceC)
    findPlaceNameC.description = 'Searches for places with names matching the given query.'
    findPlaceNameC.instruction = 'Specify a name or nickname.'
    findPlaceNameC.function = 'findPlaceNameF'
    global findPlaceTimezoneC
    findPlaceTimezoneC = command('timezone', findPlaceC)
    findPlaceTimezoneC.description = 'Searches for places with timezones matching the given query.'
    findPlaceTimezoneC.instruction = 'Specify a timezone.'
    findPlaceTimezoneC.function = 'findPlaceTimezoneF'

def addPlaceF(inputData, content):
    placeData = []
    placeDetails = content

    for p in range(0, len(placeDetails)):
        if '=' in placeDetails[p]:
            placeData.append(placeDetails[p].split('='))

    placeDict = {}

    for q in placeData:
        placeDict.update({q[0] : q[1]})

    goodProfile = False
    
    if 'id' in placeDict.keys():
        if placeDict['id'].startswith('"') and placeDict['id'].endswith('"'):
            newPlace = place(int(placeDict['id'][1:-1]))
            goodProfile = True

            if 'name' in placeDict.keys():
                if placeDict['name'].startswith('"') and placeDict['name'].endswith('"'):
                    newPlace.name = placeDict['name'][1:-1]
                else:
                    goodProfile = False

            if 'tz' in placeDict.keys():
                if placeDict['tz'].startswith('"') and placeDict['tz'].endswith('"'):
                    thisTZ = tryGetOneTimezone(placeDict['tz'][1:-1])
                    if thisTZ:
                        newPlace.tz = thisTZ
                    else:
                        goodProfile = False
                else:
                    goodProfile = False

            if 'trigger' in placeDict.keys():
                if placeDict['trigger'].startswith('"') and placeDict['trigger'].endswith('"'):
                    newPlace.trigger = placeDict['trigger'][1:-1]
                else:
                    goodProfile = False

    if goodProfile:
        addPlace(newPlace)
        config.outQ.put(f'Added place {newPlace.name}.')

    else:
        config.outQ.put('Invalid attribute(s).')

def removePlaceF(inputData, content):
    thisThread = request_queue(inputData, filter_channel=True, filter_user=True)
    thisQ = thisThread['queue']
    placeString = content[0]
    thisPlace = tryGetOnePlace(placeString)

    if thisPlace:
        config.outQ.put(f'{thisThread["tag"]}> Remove place {thisPlace.name}({thisPlace.id})? ({thisThread["tag"]}> y/N)')
        rawResponse = thisQ.get()
        response = rawResponse.content

        if response.lower() == 'y':
            removePlace(thisPlace)
            config.outQ.put('Place removed.')

        else:
            config.outQ.put('Cancelled.')

    else:
        config.outQ.put('Place not found.')

def editPlaceF(inputData, content):
    placeData = []

    placeString = content[0]
    placeDetails = content[1:]

    thisPlace = tryGetOnePlace(placeString)
    
    if thisPlace:
        editPlace = place(thisPlace.id)

        for p in range(0, len(placeDetails)):
            if '=' in placeDetails[p]:
                placeData.append(placeDetails[p].split('='))

        placeDict = {}

        for q in placeData:
            placeDict.update({q[0] : q[1]})
    
        goodProfile = False
            
        if 'name' in placeDict.keys():
            if placeDict['name'].startswith('"') and placeDict['name'].endswith('"'):
                editPlace.name = placeDict['name'][1:-1]
                goodProfile = True
            else:
                goodProfile = False

        if 'tz' in placeDict.keys():
            if placeDict['tz'].startswith('"') and placeDict['tz'].endswith('"'):
                thisTZ = tryGetOneTimezone(placeDict['tz'][1:-1])
                if thisTZ:
                    editPlace.tz = thisTZ
                    goodProfile = True
                else:
                    goodProfile = False
            else:
                goodProfile = False

        if 'trigger' in placeDict.keys():
            if placeDict['trigger'].startswith('"') and placeDict['trigger'].endswith('"'):
                editPlace.trigger = placeDict['trigger'][1:-1]
                goodProfile = True
            else:
                goodProfile = False

        if goodProfile:
            updatePlace(editPlace)
            config.outQ.put(f'Updated place {thisPlace.name}.')

        else:
            config.outQ.put('Invalid attribute(s).')

    else:
        config.outQ.put('Place not found.')

def showPlaceF(inputData, content):
    placeString = ' '.join(content)
    thisPlace = tryGetOnePlace(placeString)

    if thisPlace:
        output_text = ''
        output_text += (f'Name = {thisPlace.name}\n')
        output_text += (f'ID = {thisPlace.id}\n')
        output_text += (f'Trigger = {thisPlace.trigger}\n')
        output_text += (f'Timezone = {thisPlace.tz}')

        config.outQ.put(output_text)

    else:
        config.outQ.put('Place not found.')

def listPlaceF(inputData):
    if checkDB():
        conn = sqlite3.connect(DB)
        cursor = conn.cursor()
        cursor.execute(
                "SELECT id FROM places"
                )
        results = cursor.fetchall()
        conn.close()

        output_text = ''

        for i, each in enumerate(results):
            if i:
                output_text += '\n'
    
            thisPlace = getPlace(each[0])
            output_text += thisPlace.name

        config.outQ.put(output_text)

def findPlaceNameF(inputData, content):
    placeString = ' '.join(content)
    results = searchPlacebyName(placeString)

    if results:
        output_text = ''
        if len(results) == 1:
            output_text += 'One place found:\n'

        else:
            output_text += f'{len(results)} places found:\n'

        for i, each in enumerate(results):
            if i:
                output_text += '\n'
    
            output_text += each.name

        config.outQ.put(output_text)

    else:
        config.outQ.put('No places found!')
        
def findPlaceTimezoneF(inputData, content):
    timezoneString = ' '.join(content)
    results = searchPlacebyTimezone(timezoneString)

    if results:
        output_text = ''
        if len(results) == 1:
            output_text += 'One place found:\n'

        else:
            output_text += f'{len(results)} places found:\n'

        for i, each in enumerate(results):
            if i:
                output_text += '\n'
    
            output_text += each.name

        config.outQ.put(output_text)

    else:
        config.outQ.put('No places found!')

if __name__ == "__main__":
    print("No main.")
else:
    registerCommands()
