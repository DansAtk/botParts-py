import sys
import os
import pathlib
import shutil

import sqlite3

import config
from core.commands import command, request_queue
from core import utils
from core import users
from core import places

mSelf = sys.modules[__name__]
includes = {}
config.register(mSelf)
DB = config.database

class alias:
    def __init__(self, USER, PLACE, NICK=None):
        self.user = USER
        self.place = PLACE
        self.nick = NICK

def getAlias(userid, placeid):
    if utils.checkDB():
        conn = sqlite3.connect(DB)
        cursor = conn.cursor()
        cursor.execute(
                "SELECT userid, placeid, nick "
                "FROM aliases "
                "WHERE userid = ? AND placeid = ?",
                (userid, placeid)
                )
        result = cursor.fetchone()
        conn.close()
        
        if result:
            thisAlias = alias(result[0], result[1], result[2])

            return thisAlias

        else:
            return None

def addAlias(profile):
    if users.getUser(profile.user):
        if places.getPlace(profile.place):
            if utils.checkDB():
                conn = sqlite3.connect(DB)
                cursor = conn.cursor()
                cursor.execute(
                        "INSERT INTO aliases "
                        "(userid, placeid, nick) "
                        "VALUES (?, ?, ?)",
                        (profile.user, profile.place, profile.nick)
                        )
                conn.commit()
                conn.close()

def removeAlias(userid, placeid):
    if utils.checkDB():
        conn = sqlite3.connect(DB)
        conn.execute("PRAGMA foreign_keys = 1")
        cursor = conn.cursor()
        cursor.execute(
                "DELETE FROM aliases "
                "WHERE userid = ? AND placeid = ?",
                (userid, placeid)
                )
        conn.commit()
        conn.close()

def updateAlias(profile):
    thisAlias = getAlias(profile.user, profile.place)

    if thisAlias:
        if profile.nick:
            thisAlias.nick = profile.nick

            if utils.checkDB():
                conn = sqlite3.connect(DB)
                cursor = conn.cursor()
                cursor.execute(
                        "UPDATE aliases SET "
                        "nick = ? "
                        "WHERE userid = ? AND serverid = ?",
                        (thisAlias.nick,)
                        )
                conn.commit()
                conn.close()

def searchAliasbyPlace(placeid):
    if utils.checkDB():
        conn = sqlite3.connect(DB)
        cursor = conn.cursor()
        cursor.execute(
                "SELECT userid, placeid "
                "FROM aliases "
                "WHERE placeid = ?",
                (placeid,)
                )
        search = cursor.fetchall()
        conn.close()

        if len(search) > 0:
            foundAliases = []
            for result in search:
                thisAlias = getAlias(result[0], result[1])
                foundAliases.append(thisAlias)

            return foundAliases

        else:
            return None

def searchAliasbyUser(userid):
    if utils.checkDB():
        conn = sqlite3.connect(DB)
        cursor = conn.cursor()
        cursor.execute(
                "SELECT userid, placeid "
                "FROM aliases "
                "WHERE userid = ?",
                (userid,)
                )
        search = cursor.fetchall()
        conn.close()

        if len(search) > 0:
            foundAliases = []
            for result in search:
                thisAlias = getAlias(result[0], result[1])
                foundAliases.append(thisAlias)

            return foundAliases

        else:
            return None

def searchAliasbyNick(nickString):
    if utils.checkDB():
        conn = sqlite3.connect(DB)
        cursor = conn.cursor()
        cursor.execute(
                "SELECT userid, placeid "
                "FROM aliases "
                "WHERE nick LIKE ?",
                ('%{}%'.format(nickString),)
                )
        search = cursor.fetchall()
        conn.close()

        if len(search) > 0:
            foundAliases = []
            for result in search:
                thisAlias = getAlias(result[0], result[1])
                foundAliases.append(thisAlias)

            return foundAliases

        else:
            return None

def dbinit():
    try:
        conn = sqlite3.connect(DB)
        cursor = conn.cursor()
        config.debugQ.put('Configuring for aliases...')
        cursor.execute(
                "CREATE TABLE aliases("
                "userid INTEGER NOT NULL, placeid INTEGER NOT NULL, nick TEXT, "
                "PRIMARY KEY(userid, placeid), "
                "FOREIGN KEY(userid) REFERENCES users(id) ON DELETE CASCADE ON UPDATE NO ACTION, "
                "FOREIGN KEY(placeid) REFERENCES places(id) ON DELETE CASCADE ON UPDATE NO ACTION)"
                )
        conn.commit()
        conn.close()
        config.debugQ.put('Success!')

    except:
        config.debugQ.put('Unable to configure aliases table!')

def registerCommands():
    global addAliasC
    addAliasC = command('alias', utils.addC)
    addAliasC.description = 'Builds an alias from parameters, then adds it to the database.'
    addAliasC.instruction = 'First specify a user and server. Then, specify alias attributes using \'Attribute=Value\' with each separated by a space.'
    addAliasC.function = 'addAliasF'
    addAliasC.parent_module = mSelf
    global removeAliasC
    removeAliasC = command('alias', utils.removeC)
    removeAliasC.description = 'Removes an alias from the database.'
    removeAliasC.instruction = 'Specify a user and server.'
    removeAliasC.function = 'removeAliasF'
    removeAliasC.parent_module = mSelf
    global editAliasC
    editAliasC = command('alias', utils.editC)
    editAliasC.description = 'Updates an existing alias with new attributes.'
    editAliasC.instruction = 'First specify a user and server. Then, specify new attributes using \'Attribute=Value\' with each separated by a space.'
    editAliasC.function = 'editAliasF'
    editAliasC.parent_module = mSelf
    global showAliasC
    showAliasC = command('alias', utils.showC)
    showAliasC.description = 'Displays detailed information about a specific alias.'
    showAliasC.instruction = 'Specify a user and place.'
    showAliasC.function = 'showAliasF'
    showAliasC.parent_module = mSelf
    global listAliasC
    listAliasC = command('alias', utils.listC)
    listAliasC.description = 'Lists all known aliases.'
    listAliasC.function = 'listAliasF'
    listAliasC.parent_module = mSelf
    global listUserAliasC
    listUserAliasC = command('alias', users.listUserC)
    listUserAliasC.description = 'Lists all aliases associated with a specific user.'
    listUserAliasC.instruction = 'Specify a user.'
    listUserAliasC.function = 'listUserAliasF'
    listUserAliasC.parent_module = mSelf
    global listPlaceAliasC
    listPlaceAliasC = command('alias', places.listPlaceC)
    listPlaceAliasC.description = 'Lists all aliases associated with a specific place.'
    listPlaceAliasC.instruction = 'Specify a place.'
    listPlaceAliasC.function = 'listPlaceAliasF'
    listPlaceAliasC.parent_module = mSelf

def addAliasF(inputData, content):
    aliasData = []

    userString = content[0]
    placeString = content[1]
    aliasDetails = content[2:]


    thisUser = users.tryGetOneUser(userString)
    thisPlace = places.tryGetOnePlace(placeString)

    if thisUser and thisPlace:
        thisAlias = getAlias(int(thisUser.id), int(thisPlace.id))

        if not thisAlias:
            newAlias = alias(thisUser.id, thisPlace.id)

            goodProfile = True

            for p in range(0, len(aliasDetails)):
                if '=' in aliasDetails[p]:
                    aliasData.append(aliasDetails[p].split('='))

            aliasDict = {}

            for q in aliasData:
                aliasDict.update({q[0] : q[1]})
    
            if 'nick' in aliasDict.keys():
                if aliasDict['nick'].startswith('"') and aliasDict['nick'].endswith('"'):
                    newAlias.nick = aliasDict['nick'][1:-1]
                else:
                    goodProfile = False

            if goodProfile:
                addAlias(newAlias)
                config.outQ.put(f'Added alias for {thisUser.name} in {thisPlace.name}.')

            else:
                config.outQ.put('Invalid attribute(s).')

        else:
            config.outQ.put('Alias already exists.')

    else:
        config.outQ.put('User and/or place not found.')

def removeAliasF(inputData, content):
    thisThread = request_queue(inputData, filter_channel=True, filter_user=True)
    userString = content[0]
    placeString = content[1]

    thisUser = users.tryGetOneUser(userString)
    thisPlace = places.tryGetOnePlace(placeString)

    if thisUser and thisPlace:
        thisAlias = getAlias(thisUser.id, thisPlace.id)

        if thisAlias:
            config.outQ.put(f'{thisThread["tag"]}> Remove alias for {thisUser.name}({thisUser.id}) in {thisPlace.name}({thisPlace.id})? ({thisThread["tag"]}> y/N)')
            rawResponse = thisThread['queue'].get()
            response = rawResponse.content

            if response.lower() == 'y':
                removeAlias(thisAlias)
                config.outQ.put('Alias removed.')

            else:
                config.outQ.put('Cancelled.')

        else:
            config.outQ.put('Alias not found.')

    else:
        config.outQ.put('User and/or place not found.')

def editAliasF(inputData, content):
    aliasData = []

    userString = content[0]
    placeString = content[1]
    aliasDetails = content[2:]

    thisUser = users.tryGetOneUser(userString)
    thisPlace = places.tryGetOnePlace(placeString)

    if thisUser and thisPlace:
        thisAlias = getAlias(thisUser, thisPlace)

        if thisAlias:
            editAlias = alias(thisUser.id, thisPlace.id)

            for p in range(0, len(aliasDetails)):
                if '=' in aliasDetails[p]:
                    aliasData.append(aliasDetails[p].split('='))

            aliasDict = {}

            for q in aliasData:
                aliasDict.update({q[0] : q[1]})

            goodProfile = False
    
            if 'nick' in aliasDict.keys():
                if aliasDict['nick'].startswith('"') and aliasDict['nick'].endswith('"'):
                    editAlias.nick = aliasDict['nick'][1:-1]
                    goodProfile = True
                else:
                    goodProfile = False

            if goodProfile:
                updateAlias(editAlias)
                config.outQ.put(f'Updated alias for {thisUser.name} in {thisPlace.name}.')

            else:
                config.outQ.put('Invalid attribute(s).')

        else:
            config.outQ.put('Existing alias not found.')

    else:
        config.outQ.put('User and/or place not found.')

def showAliasF(inputData, content):
    userString = content[0]
    placeString = content[1]

    thisUser = users.tryGetOneUser(userString)
    thisPlace = places.tryGetOnePlace(placeString)

    if thisUser and thisPlace:
        thisAlias = getAlias(thisUser.id, thisPlace.id)

        if thisAlias:
            output_text = ''
            output_text += (f'User = {thisUser.name}\n')
            output_text += (f'Place = {thisPlace.name}\n')
            output_text += (f'Nickname = {thisAlias.nick}')

            config.outQ.put(output_text)

        else:
            config.outQ.put('No alias found.')

    else:
        config.outQ.put('User and/or place not found.')

def listAliasF(inputData):
    if utils.checkDB():
        conn = sqlite3.connect(DB)
        cursor = conn.cursor()
        cursor.execute(
                "SELECT userid, placeid, nick FROM aliases"
                )
        results = cursor.fetchall()
        conn.close()

        output_text = ''

        for i, each in enumerate(results):
            if i:
                output_text += '\n'
    
            thisUser = users.getUser(each[0])
            thisPlace = places.getPlace(each[1])
            thisAlias = getAlias(each[0], each[1])
            output_text += f'{thisUser.name} - {thisPlace.name} - {thisAlias.nick}'

            config.outQ.put(output_text)

def listUserAliasF(inputData, content):
    userString = ' '.join(content)
    thisUser = users.tryGetOneUser(userString)

    if thisUser:
        if utils.checkDB():
            conn = sqlite3.connect(DB)
            cursor = conn.cursor()
            cursor.execute(
                    "SELECT placeid FROM aliases "
                    "WHERE userid = ?",
                    (thisUser.id,)
                    )
            results = cursor.fetchall()
            conn.close()

            output_text = ''

            for i, each in enumerate(results):
                if i:
                    output_text += '\n'
        
                thisPlace = places.getPlace(each[0])
                output_text += thisPlace.name

            config.outQ.put(output_text)

    else:
        config.outQ.put('User not found.')

def listPlaceAliasF(inputData, content):
    placeString = ' '.join(content)
    thisPlace = places.tryGetOnePlace(placeString)

    if thisPlace:
        if utils.checkDB():
            conn = sqlite3.connect(DB)
            cursor = conn.cursor()
            cursor.execute(
                    "SELECT userid FROM aliases "
                    "WHERE placeid = ?",
                    (thisPlace.id,)
                    )
            results = cursor.fetchall()
            conn.close()

            output_text = ''

            for i, each in enumerate(results):
                if i:
                    output_text += '\n'
        
                thisUser = users.getUser(each[0])
                output_text += thisUser.name

            config.outQ.put(output_text)

    else:
        config.outQ.put('Place not found.')

if __name__ == "__main__":
    print("No main.")
else:
    registerCommands()
