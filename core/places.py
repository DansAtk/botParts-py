import sys
import os
import pathlib
import shutil

import sqlite3
import pytz
from datetime import *

import config
from core.commands import command, request_queue
from core import utils

mSelf = sys.modules[__name__]
includes = {}
config.register(mSelf)
DB = config.database

class place:
    def __init__(self, ID, NAME=None, TRIGGER=':', TZ=None, PARENT=None):
        self.id = ID
        self.name = NAME
        self.trigger = TRIGGER
        self.tz = TZ
        self.parent = PARENT

    def now(self):
        if self.tz:
            return datetime.now(pytz.timezone(self.tz))
        
        else:
            return getTime()

def getPlace(placeID):
    if utils.checkDB():
        conn = sqlite3.connect(DB)
        cursor = conn.cursor()
        cursor.execute(
                "SELECT name, trigger, tz, parent FROM places WHERE id = ?",
                (placeID,)
                )
        result = cursor.fetchone()
        conn.close()
        
        if result:
            thisPlace = place(placeID)
            thisPlace.name = result[0]
            thisPlace.trigger = result[1]
            thisPlace.tz = result[2]
            thisPlace.parent = result[3]

            return thisPlace
        
        else:
            return None

def getPlaceRoot(placeID):
    root = getPlace(placeID)

    while root.parent:
        root = getPlace(root.parent)

    return root

def getPlaceChildren(placeID):
    if utils.checkDB():
        conn = sqlite3.connect(DB)
        cursor = conn.cursor()
        cursor.execute(
                "SELECT id "
                "FROM places "
                "WHERE parent = ?",
                (placeID,)
                )
        results = cursor.fetchall()
        conn.close()

        if len(results) > 0:
            foundChildren = []
            for each in results:
                thisPlace = getPlace(result[0])
                foundChildren.append(thisPlace)

            return foundChildren

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
    if utils.checkDB():
        conn = sqlite3.connect(DB)
        cursor = conn.cursor()
        cursor.execute(
                "INSERT INTO places"
                "(id, name, trigger, tz, parent) "
                "VALUES (?, ?, ?, ?, ?)",
                (profile.id, profile.name, profile.trigger, profile.tz, profile.parent)
                )
        conn.commit()
        conn.close()

def removePlace(profile):
    if utils.checkDB():
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

    children = getPlaceChildren(profile.id)
    
    for child in children:
        removePlace(child)

def updatePlace(profile):
    thisPlace = getPlace(profile.id)

    if thisPlace:
        if profile.name:
            thisPlace.name = profile.name
        if profile.trigger:
            thisPlace.trigger = profile.trigger
        if profile.tz:
            thisPlace.tz = profile.tz
        if profile.parent:
            thisPlace.parent = profile.parent
        
        if utils.checkDB():
            conn = sqlite3.connect(DB)
            cursor = conn.cursor()
            cursor.execute(
                    "UPDATE places SET "
                    "name = ?, trigger = ?, tz = ?, parent = ? "
                    "WHERE id = ?",
                    (thisPlace.name, thisPlace.trigger, thisPlace.tz, thisPlace.parent, thisPlace.id)
                    )
            conn.commit()
            conn.close()

def searchPlacebyName(searchString):
    if utils.checkDB():
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
    if utils.checkDB():
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

def dbinit():
    try:
        conn = sqlite3.connect(DB)
        cursor = conn.cursor()
        config.debugQ.put('Configuring for places...')
        cursor.execute(
                "CREATE TABLE places("
                "id INTEGER PRIMARY KEY, name TEXT, tz TEXT, trigger TEXT, parent INTEGER)"
                )
        conn.commit()
        conn.close()
        config.debugQ.put('Success!')

    except:
        config.debugQ.put('Unable to configure places table!')

def registerCommands():
    global addPlaceC
    addPlaceC = command('place', utils.addC)
    addPlaceC.description = 'Builds a place from parameters, then adds it to the database.'
    addPlaceC.instruction = 'Specify place attributes using \'Attribute=Value\' with each separated by a space. \'id\' is required.'
    addPlaceC.function = 'addPlaceF'
    addPlaceC.parent_module = mSelf
    global removePlaceC
    removePlaceC = command('place', utils.removeC)
    removePlaceC.description = 'Removes a place from the database.'
    removePlaceC.instruction = 'Specify a place.'
    removePlaceC.function = 'removePlaceF'
    removePlaceC.parent_module = mSelf
    global editPlaceC
    editPlaceC = command('place', utils.editC)
    editPlaceC.description = 'Updates an existing place with new attributes.'
    editPlaceC.instruction = 'First specify a place. Then, specify new attributes using \'Attribute=Value\' with each separated by a space.'
    editPlaceC.function = 'editPlaceF'
    editPlaceC.parent_module = mSelf
    global showPlaceC
    showPlaceC = command('place', utils.showC)
    showPlaceC.description = 'Displays detailed information about a single place.'
    showPlaceC.instruction = 'Specify a place.'
    showPlaceC.function = 'showPlaceF'
    showPlaceC.parent_module = mSelf
    global listPlaceC
    listPlaceC = command('place', utils.listC)
    listPlaceC.description = 'Lists all places in the database.'
    listPlaceC.function = 'listPlaceF'
    listPlaceC.parent_module = mSelf
    global findPlaceC
    findPlaceC = command('place', utils.findC)
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
                    thisTZ = utils.tryGetOneTimezone(placeDict['tz'][1:-1])
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
                thisTZ = utils.tryGetOneTimezone(placeDict['tz'][1:-1])
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
    if utils.checkDB():
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
