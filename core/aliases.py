import sys
import os
import pathlib
import shutil

import sqlite3
import pytz
import calendar
from datetime import *

from core import config
from core.commandM import command, request_queue, imports

mSelf = sys.modules[__name__]
includes = {}
imports.update({__name__ : includes})
DB = config.database

class alias:
    def __init__(self, USER, PLACE, NICK=None):
        self.user = USER
        self.place = PLACE
        self.nick = NICK

def getAlias(userid, placeid):
    if checkDB():
        conn = sqlite3.connect(DB)
        cursor = conn.cursor()
        cursor.execute(
                "SELECT userid, placeid, nick "
                "FROM aliases "
                "WHERE userid = ? AND placeid = ?"
                (userid, placeid)
                )
        result = cursor.fetchone()
        conn.close()
        
        if result:
            thisAlias = alias(result[0], result[1], result[2])

            return thisUser

        else:
            return None

def addAlias(profile):
    if users.getUser(profile.user):
        if places.getPlace(profile.place):
            if checkDB():
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
    if checkDB():
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

            if checkDB():
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
    if checkDB():
        conn = sqlite3.connect(DB)
        cursor = conn.cursor()
        cursor.execute(
                "SELECT userid, placeid, nick "
                "FROM aliases "
                "WHERE placeid = ?",
                (placeid,)
                )
        search = cursor.fetchall()
        conn.close()

        if len(search) > 0:
            foundAliases = []
            for result in search:
                thisAlias = alias(result[0], result[1], result[2])
                foundAliases.append(thisAlias)

            return foundAliases

        else:
            return None

def searchAliasbyUser(userid):
    if checkDB():
        conn = sqlite3.connect(DB)
        cursor = conn.cursor()
        cursor.execute(
                "SELECT userid, placeid, nick "
                "FROM aliases "
                "WHERE userid = ?",
                (userid,)
                )
        search = cursor.fetchall()
        conn.close()

        if len(search) > 0:
            foundAliases = []
            for result in search:
                thisAlias = alias(result[0], result[1], result[2])
                foundAliases.append(thisAlias)

            return foundAliases

        else:
            return None

def registerCommands():
    global addAliasC
    addAliasC = command('alias', addC)
    addAliasC.description = 'Builds an alias from parameters, then adds it to the database.'
    addAliasC.instruction = 'First specify a user and server. Then, specify alias attributes using \'Attribute=Value\' with each separated by a space.'
    addAliasC.function = 'addAliasF'
    global removeAliasC
    removeAliasC = command('alias', removeC)
    removeAliasC.description = 'Removes an alias from the database.'
    removeAliasC.instruction = 'Specify a user and server.'
    removeAliasC.function = 'removeAliasF'
    global editAliasC
    editAliasC = command('alias', editC)
    editAliasC.description = 'Updates an existing alias with new attributes.'
    editAliasC.instruction = 'First specify a user and server. Then, specify new attributes using \'Attribute=Value\' with each separated by a space.'
    editAliasC.function = 'editAliasF'
    global showAliasC
    showAliasC = command('alias', showC)
    showAliasC.description = 'Displays detailed information about a user\'s specific alias on a server.'
    showAliasC.instruction = 'Specify a user and server.'
    showAliasC.function = 'showAliasF'
    global listAliasC
    listAliasC = command('alias', listC)
    listAliasC.description = 'Lists all aliases associated with a specific user or place.'
    listAliasC.instruction = 'Specify a user or place.'
    listAliasC.function = 'listAliasF'

def databaseF(inputData=None):
    config.outQ.put(databaseC.help())

def databaseSetupF(inputData):
    if not config.dataPath.exists():
        config.dataPath.mkdir()

    DB = config.database

    try:
        doInit = False
        if DB.exists():
            thisQ = request_queue(inputData, filter_channel=True, filter_user=True)
            config.outQ.put('Database already exists. Re-initialize? This will empty the database. <y/N> ')
            rawResponse = thisQ.get()
            response = rawResponse.content
            if response.lower() == 'y':
                DB.unlink()
                doInit = True
            else:
                config.outQ.put('Canceled.')
        else:
            doInit = True
        
        if doInit:
            conn = sqlite3.connect(DB)
            cursor = conn.cursor()
            cursor.execute(
                    "CREATE TABLE info("
                    "id INTEGER PRIMARY KEY AUTOINCREMENT, key TEXT, value TEXT)"
                    )
            cursor.execute("INSERT INTO info(key, value) VALUES (?, ?)",
                    ('dbversion', config.settings['dbversion']))
            config.debugQ.put('Configuring for multiple users...')
            cursor.execute(
                    "CREATE TABLE users("
                    "id INTEGER PRIMARY KEY, name TEXT, botrank INTEGER DEFAULT '0', country TEXT, "
                    "tz TEXT DEFAULT 'US/Eastern', bday TEXT, points INTEGER DEFAULT '0')"
                    )
            config.debugQ.put('Configuring for multiple servers...')
            cursor.execute(
                    "CREATE TABLE servers("
                    "id INTEGER PRIMARY KEY, name TEXT, tz TEXT, trigger TEXT)"
                    )
            config.debugQ.put('Configuring for color management...')
            cursor.execute(
                    "CREATE TABLE colors("
                    "id INTEGER PRIMARY KEY, name TEXT, code TEXT)"
                    )
            config.debugQ.put('Configuring for user aliases...')
            cursor.execute(
                    "CREATE TABLE serverusers("
                    "userid INTEGER NOT NULL, serverid INTEGER NOT NULL, color INTEGER, nick TEXT, localrank TEXT, "
                    "PRIMARY KEY(userid, serverid), "
                    "FOREIGN KEY(userid) REFERENCES users(id) ON DELETE CASCADE ON UPDATE NO ACTION, "
                    "FOREIGN KEY(serverid) REFERENCES servers(id) ON DELETE CASCADE ON UPDATE NO ACTION, "
                    "FOREIGN KEY(color) REFERENCES colors(id) ON DELETE SET NULL ON UPDATE NO ACTION)" 
                    )
            conn.commit()
            conn.close()

            for module in imports:
                if hasattr(sys.modules[module], 'dbinit'):
                    sys.modules[module].dbinit(DB)

            config.debugQ.put('Database initialized.')
    
    except:
        config.debugQ.put('An error occurred.')

def databaseDeleteF(inputData):
    thisQ = request_queue(inputData, filter_channel=True, filter_user=True)
    config.outQ.put('Are you sure you want to delete the current database? <y/N> ')
    rawResponse = thisQ.get()
    response = rawResponse.content

    if response.lower() == 'y':
        config.database.unlink()
        config.outQ.put('Database deleted.')

    else:
        config.outQ.put('Cancelled.')

def databaseBackupF(inputData=None):
    if checkDB():
        oFile = backupDB()
        config.debugQ.put(f'Database backed up to \'{oFile.name}\'.')

def addUserF(inputData, content):
    userDetails = content
    userdata = []

    for p in range(0, len(userDetails)):
        if '=' in userDetails[p]:
            userdata.append(userDetails[p].split('='))

    userDict = {}

    for q in userdata:
        userDict.update({q[0] : q[1]})

    goodProfile = False
   
    if 'id' in userDict.keys():
        if userDict['id'].startswith('"') and userDict['id'].endswith('"'):
            newUser = user(int(userDict['id'][1:-1]))

            goodProfile = True

            if 'name' in userDict.keys():
                if userDict['name'].startswith('"') and userDict['name'].endswith('"'):
                    newUser.name = userDict['name'][1:-1]
                else:
                    goodProfile = False

            if 'tz' in userDict.keys():
                if userDict['tz'].startswith('"') and userDict['tz'].endswith('"'):
                    thisTZ = tryGetOneTimezone(userDict['tz'][1:-1])
                    if thisTZ:
                        newUser.tz = thisTZ
                    else:
                        goodProfile = False
                else:
                    goodProfile = False

            if 'botrank' in userDict.keys():
                if userDict['botrank'].startswith('"') and userDict['botrank'].endswith('"'):
                    newUser.botrank = userDict['botrank'][1:-1]
                else:
                    goodProfile = False

            if 'bday' in userDict.keys():
                if userDict['bday'].startswith('"') and userDict['bday'].endswith('"'):
                    newUser.bday = userDict['bday'][1:-1]
                else:
                    goodProfile = False

            if 'country' in userDict.keys():
                if userDict['country'].startswith('"') and userDict['country'].endswith('"'):
                    newUser.country = userDict['country'][1:-1]
                else:
                    goodProfile = False

            if 'points' in userDict.keys():
                if userDict['points'].startswith('"') and userDict['points'].endswith('"'):
                    newUser.points = userDict['points'][1:-1]
                else:
                    goodProfile = False

            if 'serverid' in userDict.keys():
                if userDict['serverid'].startswith('"') and userDict['serverid'].endswith('"'):
                    newUser.serverid = userDict['serverid'][1:-1]

                    if 'nick' in userDict.keys():
                        if userDict['nick'].startswith('"') and userDict['nick'].endswith('"'):
                            newUser.nick = userDict['nick'][1:-1]
                        else:
                            goodProfile = False

                    if 'color' in userDict.keys():
                        if userDict['color'].startswith('"') and userDict['color'].endswith('"'):
                            thisColor = tryGetOneColor(userDict['color'][1:-1])
                            if thisColor:
                                newUser.color = thisColor.id
                            else:
                                goodProfile = False
                        else:
                            goodProfile = False

                    if 'localrank' in userDict.keys():
                        if userDict['localrank'].startswith('"') and userDict['localrank'].endswith('"'):
                            newUser.localrank = userDict['localrank'][1:-1]
                        else:
                            goodProfile = False
                else:
                    goodProfile = False

    if goodProfile:
        addUser(newUser)
        config.outQ.put(f'Added user {newUser.name}.')

    else:
        config.outQ.put('Invalid attribute(s).')


def addUserAliasF(inputData, content):
    aliasdata = []

    userString = content[0]
    serverString = content[1]
    aliasDetails = content[2:]

    thisUser = tryGetOneUser(userString)
    thisServer = tryGetOneServer(serverString)

    if thisUser and thisServer:
        thisAlias = getUserAlias(thisUser, thisServer)

        if thisAlias == None:
            newAlias = user(thisUser.id)
            newAlias.serverid = thisServer.id

            goodProfile = True

            for p in range(0, len(aliasDetails)):
                if '=' in aliasDetails[p]:
                    aliasdata.append(aliasDetails[p].split('='))

            aliasDict = {}

            for q in aliasdata:
                aliasDict.update({q[0] : q[1]})
    
            if 'nick' in aliasDict.keys():
                if aliasDict['nick'].startswith('"') and aliasDict['nick'].endswith('"'):
                    newAlias.nick = aliasDict['nick'][1:-1]
                else:
                    goodProfile = False

            if 'color' in aliasDict.keys():
                if aliasDict['color'].startswith('"') and aliasDict['color'].endswith('"'):
                    thisColor = tryGetOneColor(aliasDict['color'][1:-1])
                    if thisColor:
                        newAlias.color = thisColor.id
                    else:
                        goodProfile = False
                else:
                    goodProfile = False

            if 'localrank' in aliasDict.keys():
                if aliasDict['localrank'].startswith('"') and aliasDict['localrank'].endswith('"'):
                    newAlias.localrank = aliasDict['localrank'][1:-1]
                else:
                    goodProfile = False

            if goodProfile:
                addUserAlias(newAlias)
                config.outQ.put(f'Added user alias for {thisUser.name} in server {thisServer.name}.')

            else:
                config.outQ.put('Invalid attribute(s).')

        else:
            config.outQ.put('User alias already exists.')

    else:
        config.outQ.put('User and/or server not found.')

def addServerF(inputData, content):
    serverdata = []
    serverDetails = content

    for p in range(0, len(serverDetails)):
        if '=' in serverDetails[p]:
            serverdata.append(serverDetails[p].split('='))

    serverDict = {}

    for q in serverdata:
        serverDict.update({q[0] : q[1]})

    goodProfile = False
    
    if 'id' in serverDict.keys():
        if serverDict['id'].startswith('"') and serverDict['id'].endswith('"'):
            newServer = server(int(serverDict['id'][1:-1]))
            goodProfile = True

            if 'name' in serverDict.keys():
                if serverDict['name'].startswith('"') and serverDict['name'].endswith('"'):
                    newServer.name = serverDict['name'][1:-1]
                else:
                    goodProfile = False

            if 'tz' in serverDict.keys():
                if serverDict['tz'].startswith('"') and serverDict['tz'].endswith('"'):
                    thisTZ = tryGetOneTimezone(serverDict['tz'][1:-1])
                    if thisTZ:
                        newServer.tz = thisTZ
                    else:
                        goodProfile = False
                else:
                    goodProfile = False

            if 'trigger' in serverDict.keys():
                if serverDict['trigger'].startswith('"') and serverDict['trigger'].endswith('"'):
                    newServer.trigger = serverDict['trigger'][1:-1]
                else:
                    goodProfile = False

    if goodProfile:
        addServer(newServer)
        config.outQ.put(f'Added server {newServer.name}.')

    else:
        config.outQ.put('Invalid attribute(s).')

def addColorF(inputData, content):
    colordata = []
    colorDetails = content

    for p in range(0, len(colorDetails)):
        if '=' in colorDetails[p]:
            colordata.append(colorDetails[p].split('='))

    colorDict = {}

    for q in colordata:
        colorDict.update({q[0] : q[1]})

    goodProfile = False
    
    if 'id' in colorDict.keys():
        if colorDict['id'].startswith('"') and colorDict['id'].endswith('"'):
            newColor = color(int(colorDict['id'][1:-1]))
            goodProfile = True

            if 'name' in colorDict.keys():
                if colorDict['name'].startswith('"') and colorDict['name'].endswith('"'):
                    newColor.name = colorDict['name'][1:-1]
                else:
                    goodProfile = False

            if 'code' in colorDict.keys():
                if colorDict['code'].startswith('"') and colorDict['code'].endswith('"'):
                    newColor.code = colorDict['code'][1:-1]
                else:
                    goodProfile = False

    if goodProfile:
        addColor(newColor)
        config.outQ.put(f'Added color {newColor.name}.')
    else:
        config.outQ.put('Invalid attribute(s).')

def removeUserF(inputData, content):
    thisQ = request_queue(inputData, filter_channel=True, filter_user=True)
    userString = content[0]
    thisUser = tryGetOneUser(userString)

    if thisUser:
        config.outQ.put(f'Remove user {thisUser.name}({thisUser.id})? <y/N> ')
        rawResponse = thisQ.get()
        response = rawResponse.content

        if response.lower() == 'y':
            removeUser(thisUser)
            config.outQ.put('User removed.')

        else:
            config.outQ.put('Cancelled.')

    else:
        config.outQ.put('User not found.')
        
def removeServerF(inputData, content):
    thisQ = request_queue(inputData, filter_channel=True, filter_user=True)
    serverString = content[0]
    thisServer = tryGetOneServer(serverString)

    if thisServer:
        config.outQ.put(f'Remove server {thisServer.name}({thisServer.id})? <y/N> ')
        rawResponse = thisQ.get()
        response = rawResponse.content

        if response.lower() == 'y':
            removeServer(thisServer)
            config.outQ.put('Server removed.')

        else:
            config.outQ.put('Cancelled.')

    else:
        config.outQ.put('Server not found.')

def removeUserAliasF(inputData, content):
    thisQ = request_queue(inputData, filter_channel=True, filter_user=True)
    userString = content[0]
    serverString = content[1]

    thisUser = tryGetOneUser(userString)
    thisServer = tryGetOneServer(serverString)
    thisAlias = getUserAlias(thisUser, thisServer)

    if thisAlias:
        config.outQ.put(f'Remove alias for user {thisUser.name}({thisUser.id}) on server {thisServer.name}({thisServer.id})? <y/N> ')
        rawResponse = thisQ.get()
        response = rawResponse.content

        if response.lower() == 'y':
            removeUserAlias(thisAlias)
            config.outQ.put('Alias removed.')

        else:
            config.outQ.put('Cancelled.')

    else:
        config.outQ.put('User alias not found.')
 
def removeColorF(inputData, content):
    thisThread = request_queue(inputData, tag=True, filter_channel=True, filter_user=True)
    colorString = content[0]
    thisColor = tryGetOneColor(colorString)

    if thisColor:
        config.outQ.put(f'Remove color {thisColor.name}({thisColor.id})? ({thisThread["tag"]}>y/N)')
        rawResponse = thisThread['queue'].get()
        response = rawResponse.content

        if response.lower() == 'y':
            removeColor(thisColor)
            config.outQ.put('Color removed.')

        else:
            config.outQ.put('Cancelled.')

    else:
        config.outQ.put('Color not found.')

def editUserF(inputData, content):
    userdata = []

    userString = content[0]
    userDetails = content[1:]

    thisUser = tryGetOneUser(userString)

    if thisUser:
        editUser = user(thisUser.id)

        for p in range(0, len(userDetails)):
            if '=' in userDetails[p]:
                userdata.append(userDetails[p].split('='))

        userDict = {}

        for q in userdata:
            userDict.update({q[0] : q[1]})

        goodProfile = False
        
        if 'name' in userDict.keys():
            if userDict['name'].startswith('"') and userDict['name'].endswith('"'):
                editUser.name = userDict['name'][1:-1]
                goodProfile = True
            else:
                goodProfile = False

        if 'tz' in userDict.keys():
            if userDict['tz'].startswith('"') and userDict['tz'].endswith('"'):
                thisTZ = tryGetOneTimezone(userDict['tz'][1:-1])
                if thisTZ:
                    editUser.tz = thisTZ
                    goodProfile = True
                else:
                    goodProfile = False
            else:
                goodProfile = False

        if 'botrank' in userDict.keys():
            if userDict['botrank'].startswith('"') and userDict['botrank'].endswith('"'):
                editUser.botrank = userDict['botrank'][1:-1]
                goodProfile = True
            else:
                goodProfile = False

        if 'bday' in userDict.keys():
            if userDict['bday'].startswith('"') and userDict['bday'].endswith('"'):
                editUser.bday = userDict['bday'][1:-1]
                goodProfile = True
            else:
                goodProfile = False

        if 'country' in userDict.keys():
            if userDict['country'].startswith('"') and userDict['country'].endswith('"'):
                editUser.country = userDict['country'][1:-1]
                goodProfile = True
            else:
                goodProfile = False

        if 'points' in userDict.keys():
            if userDict['points'].startswith('"') and userDict['points'].endswith('"'):
                editUser.points = userDict['points'][1:-1]
                goodProfile = True
            else:
                goodProfile = False

        if goodProfile:
            updateUser(editUser)
            config.outQ.put(f'Updated user {thisUser.name}.')

        else:
            config.outQ.put('Invalid attribute(s).')

    else:
        config.outQ.put('User not found.')

def editServerF(inputData, content):
    serverdata = []

    serverString = content[0]
    serverDetails = content[1:]

    thisServer = tryGetOneServer(serverString)
    
    if thisServer:
        editServer = server(thisServer.id)

        for p in range(0, len(serverDetails)):
            if '=' in serverDetails[p]:
                serverdata.append(serverDetails[p].split('='))

        serverDict = {}

        for q in serverdata:
            serverDict.update({q[0] : q[1]})
    
        goodProfile = False
            
        if 'name' in serverDict.keys():
            if serverDict['name'].startswith('"') and serverDict['name'].endswith('"'):
                editServer.name = serverDict['name'][1:-1]
                goodProfile = True
            else:
                goodProfile = False

        if 'tz' in serverDict.keys():
            if serverDict['tz'].startswith('"') and serverDict['tz'].endswith('"'):
                thisTZ = tryGetOneTimezone(serverDict['tz'][1:-1])
                if thisTZ:
                    editServer.tz = thisTZ
                    goodProfile = True
                else:
                    goodProfile = False
            else:
                goodProfile = False

        if 'trigger' in serverDict.keys():
            if serverDict['trigger'].startswith('"') and serverDict['trigger'].endswith('"'):
                editServer.trigger = serverDict['trigger'][1:-1]
                goodProfile = True
            else:
                goodProfile = False

        if goodProfile:
            updateServer(editServer)
            config.outQ.put(f'Updated server {thisServer.name}.')

        else:
            config.outQ.put('Invalid attribute(s).')

    else:
        config.outQ.put('Server not found.')

def editUserAliasF(inputData, content):
    aliasdata = []

    userString = content[0]
    serverString = content[1]
    aliasDetails = content[2:]

    thisUser = tryGetOneUser(userString)
    thisServer = tryGetOneServer(serverString)

    if thisUser and thisServer:
        thisAlias = getUserAlias(thisUser, thisServer)

        if thisAlias:
            editAlias = user(thisUser.id)
            editAlias.serverid = thisServer.id

            for p in range(0, len(aliasDetails)):
                if '=' in aliasDetails[p]:
                    aliasdata.append(aliasDetails[p].split('='))

            aliasDict = {}

            for q in aliasdata:
                aliasDict.update({q[0] : q[1]})

            goodProfile = False
    
            if 'nick' in aliasDict.keys():
                if aliasDict['nick'].startswith('"') and aliasDict['nick'].endswith('"'):
                    editAlias.nick = aliasDict['nick'][1:-1]
                    goodProfile = True
                else:
                    goodProfile = False

            if 'color' in aliasDict.keys():
                if aliasDict['color'].startswith('"') and aliasDict['color'].endswith('"'):
                    thisColor = tryGetOneColor(aliasDict['color'][1:-1])
                    if thisColor:
                        editAlias.color = thisColor.name
                        goodProfile = True
                    else:
                        goodProfile = False
                else:
                    goodProfile = False

            if 'localrank' in aliasDict.keys():
                if aliasDict['localrank'].startswith('"') and aliasDict['localrank'].endswith('"'):
                    editAlias.localrank = aliasDict['localrank'][1:-1]
                    goodProfile = True
                else:
                    goodProfile = False

            if goodProfile:
                updateUserAlias(editAlias)
                config.outQ.put(f'Updated user alias for {thisUser.name} in server {thisServer.name}.')

            else:
                config.outQ.put('Invalid attribute(s).')

        else:
            config.outQ.put('Existing alias not found.')

    else:
        config.outQ.put('User and/or server not found.')

def editColorF(inputData, content):
    colordata = []

    colorString = content[0]
    colorDetails = content[1:]

    thisColor = tryGetOneColor(colorString)

    if thisColor:
        editColor = color(thisColor.id)

        for p in range(0, len(colorDetails)):
            if '=' in colorDetails[p]:
                colordata.append(colorDetails[p].split('='))

        colorDict = {}

        for q in colordata:
            colorDict.update({q[0] : q[1]})
    
        goodProfile = False
    
        if 'name' in colorDict.keys():
            if colorDict['name'].startswith('"') and colorDict['name'].endswith('"'):
                editColor.name = colorDict['name']
                goodProfile = True
            else:
                goodProfile = False

        if 'code' in colorDict.keys():
            if colorDict['code'].startswith('"') and colorDict['code'].endswith('"'):
                editColor.code = colorDict['code']
                goodProfile = True
            else:
                goodProfile = False

        if goodProfile:
            updateColor(editColor)
            config.outQ.put(f'Updated color {thisColor.name}.')

        else:
            config.outQ.put('Invalid attribute(s).')

    else:
        config.outQ.put('Color not found.')

def showUserF(inputData, content):
    userString = ' '.join(content)
    thisUser = tryGetOneUser(userString)

    if thisUser:
        output_text = ''
        output_text += (f'Name = {thisUser.name}\n')
        output_text += (f'ID = {thisUser.id}\n')
        output_text += (f'Country = {thisUser.country}\n')
        output_text += (f'Timezone = {thisUser.tz}\n')
        output_text += (f'Birthday = {thisUser.bday}\n')
        output_text += (f'Bot Rank = {thisUser.botrank}\n')
        output_text += ('\n')
        output_text += ('User aliases:')

        config.outQ.put(output_text)
        listUserAliasF(inputData, content)

    else:
        config.outQ.put('User not found.')

def showUserAliasF(inputData, content):
    userString = content[0]
    serverString = ' '.join(content[1:])

    thisUser = tryGetOneUser(userString)
    thisServer = tryGetOneServer(serverString)

    if thisUser and thisServer:
        thisAlias = getUserAlias(thisUser, thisServer)

        if thisAlias:
            output_text = ''
            output_text += (f'User = {thisUser.name}\n')
            output_text += (f'Server = {thisServer.name}\n')
            output_text += (f'Nickname = {thisAlias.nick}\n')
            output_text += (f'Color = {thisAlias.color}\n')
            output_text += (f'Local Rank = {thisAlias.localrank}')

            config.outQ.put(output_text)

        else:
            config.outQ.put('No alias found.')

    else:
        config.outQ.put('User and/or server not found.')

def showServerF(inputData, content):
    serverString = ' '.join(content)
    thisServer = tryGetOneServer(serverString)

    if thisServer:
        output_text = ''
        output_text += (f'Name = {thisServer.name}\n')
        output_text += (f'ID = {thisServer.id}\n')
        output_text += (f'Trigger = {thisServer.trigger}\n')
        output_text += (f'Timezone = {thisServer.tz}')

        config.outQ.put(output_text)

    else:
        config.outQ.put('Server not found.')

def showColorF(inputData, content):
    colorString = ' '.join(content)
    thisColor = tryGetOneColor(colorString)

    if thisColor:
        output_text = ''
        output_text += (f'Name = {thisColor.name}\n')
        output_text += (f'ID = {thisColor.id}\n')
        output_text += (f'Code = {thisColor.code}')

    else:
        config.outQ.put('Color not found.')

def listUserF(inputData):
    DB = config.database
    if checkDB():
        conn = sqlite3.connect(DB)
        cursor = conn.cursor()
        cursor.execute(
                "SELECT id FROM users"
                )
        results = cursor.fetchall()
        conn.close()

        output_text = ''

        for i, each in enumerate(results):
            if i:
                output_text += '\n'
        
            thisUser = getUser(each[0])
            output_text += thisUser.name

        config.outQ.put(output_text)

def listUserAliasF(inputData, content):
    userString = ' '.join(content)
    thisUser = tryGetOneUser(userString)

    if thisUser:
        DB = config.database
        if checkDB():
            conn = sqlite3.connect(DB)
            cursor = conn.cursor()
            cursor.execute(
                    "SELECT serverid FROM serverusers "
                    "WHERE userid = ?",
                    (thisUser.id,)
                    )
            results = cursor.fetchall()
            conn.close()

            output_text = ''

            for i, each in enumerate(results):
                if i:
                    output_text += '\n'
        
                thisServer = getServer(each[0])
                output_text += thisServer.name

            config.outQ.put(output_text)

    else:
        config.outQ.put('User not found.')

def listServerF(inputData):
    DB = config.database
    if checkDB():
        conn = sqlite3.connect(DB)
        cursor = conn.cursor()
        cursor.execute(
                "SELECT id FROM servers"
                )
        results = cursor.fetchall()
        conn.close()

        output_text = ''

        for i, each in enumerate(results):
            if i:
                output_text += '\n'
    
            thisServer = getServer(each[0])
            output_text += thisServer.name

        config.outQ.put(output_text)

def listColorF(inputData):
    DB = config.database
    if checkDB():
        conn = sqlite3.connect(DB)
        cursor = conn.cursor()
        cursor.execute(
                "SELECT id FROM colors"
                )
        results = cursor.fetchall()
        conn.close()

        output_text = ''

        for i, each in enumerate(results):
            if i:
                output_text += '\n'
    
            thisColor = getColor(each[0])
            output_text += thisColor.name

        config.outQ.put(output_text)

def listTimezoneF(inputData):
    output_text = ''

    for i, each in enumerate(pytz.all_timezones):
        if i:
            output_text += '\n'

        output_text += each

    config.outQ.put(output_text)

def timeF(inputData):
    config.outQ.put(f'The current time is {getTime()}.')

def timeForF(inputData, content):
    userString = ' '.join(content)
    thisUser = tryGetOneUser(userString)

    if thisUser:
        config.outQ.put(f'The current time for {thisUser.goesby()} in the {thisUser.tz} timezone is {thisUser.now()}.')

    else:
        config.outQ.put('Unknown user.')

def findUserNameF(inputData, content):
    userString = ' '.join(content)
    results = searchUserbyName(userString)
    if results:
        output_text = ''
        if len(results) == 1:
            output_text += 'One user found:\n'

        else:
            output_text += f'{len(results)} users found:\n'

        for i, each in enumerate(results):
            if i:
                output_text += '\n'
    
            output_text += each.name

        config.outQ.put(output_text)

    else:
        config.outQ.put('No users found!')

def findUserCountryF(inputData, content):
    countryString = ' '.join(content)
    results = searchUserbyCountry(countryString)
    if results:
        output_text = ''
        if len(results) == 1:
            output_text += 'One user found:\n'

        else:
            output_text += f'{len(results)} users found:\n'

        for i, each in enumerate(results):
            if i:
                output_text += '\n'
    
            output_text += each.name

        config.outQ.put(output_text)

    else:
        config.outQ.put('No users found!')
        
def findUserTimezoneF(inputData, content):
    timezoneString = ' '.join(content)
    results = searchUserbyTimezone(timezoneString)

    if results:
        output_text = ''
        if len(results) == 1:
            output_text += 'One user found:\n'

        else:
            output_text += f'{len(results)} users found:\n'

        for i, each in enumerate(results):
            if i:
                output_text += '\n'
    
            output_text += each.name

        config.outQ.put(output_text)

    else:
        config.outQ.put('No users found!')
        
def findUserBirthdayF(inputData, content):
    birthdayString = ' '.join(content)
    results = searchUserbyBirthday(birthdayString)

    if results:
        output_text = ''
        if len(results) == 1:
            output_text += 'One user found:\n'

        else:
            output_text += f'{len(results)} users found:\n'

        for i, each in enumerate(results):
            if i:
                output_text += '\n'
    
            output_text += each.name

        config.outQ.put(output_text)

    else:
        config.outQ.put('No users found!')
        
def findUserColorF(inputData, content):
    serverString = content[0]
    colorString = ' '.join(content[1])
    thisServer = tryGetOneServer(serverString)
    thisColor = tryGetOneColor(colorString)

    if thisServer:
        if thisColor:
            results = searchUserbyColor(thisColor, thisServer)

            if results:
                output_text = ''
                if len(results) == 1:
                    output_text += 'One user found:\n'

                else:
                    output_text += f'{len(results)} users found:\n'

                for i, each in enumerate(results):
                    if i:
                        output_text += '\n'
    
                    output_text += each.name

                config.outQ.put(output_text)

            else:
                config.outQ.put('No users found!')
        
        else:
            config.outQ.put('Unknown color.')

    else:
        config.outQ.put('Unknown server.')

def findServerNameF(inputData, content):
    serverString = ' '.join(content)
    results = searchServerbyName(serverString)

    if results:
        output_text = ''
        if len(results) == 1:
            output_text += 'One server found:\n'

        else:
            output_text += f'{len(results)} servers found:\n'

        for i, each in enumerate(results):
            if i:
                output_text += '\n'
    
            output_text += each.name

        config.outQ.put(output_text)

    else:
        config.outQ.put('No servers found!')
        
def findServerTimezoneF(inputData, content):
    timezoneString = ' '.join(content)
    results = searchServerbyTimezone(timezoneString)

    if results:
        output_text = ''
        if len(results) == 1:
            output_text += 'One server found:\n'

        else:
            output_text += f'{len(results)} servers found:\n'

        for i, each in enumerate(results):
            if i:
                output_text += '\n'
    
            output_text += each.name

        config.outQ.put(output_text)

    else:
        config.outQ.put('No servers found!')

def findTimezoneF(inputData, content):
    timezoneString = ' '.join(content)
    results = searchTimezonebyName(timezoneString)
    
    if results:
        output_text = ''
        if len(results) == 1:
            output_text += 'One timezone found:\n'

        else:
            output_text += f'{len(results)} timezones found:\n'

        for i, each in enumerate(results):
            if i:
                output_text += '\n'
    
            output_text += each

        config.outQ.put(output_text)

    else:
        config.outQ.put('No timezones found!')

def findColorF(inputData, content):
    colorString = ' '.join(content)
    results = searchColorbyName(colorString)

    if results:
        output_text = ''
        if len(results) == 1:
            output_text += 'One color found:\n'

        else:
            output_text += f'{len(results)} colors found:\n'

        for i, each in enumerate(results):
            if i:
                output_text += '\n'
    
            output_text += each.name

        config.outQ.put(output_text)

    else:
        config.outQ.put('No colors found!')

if __name__ == "__main__":
    print("No main.")
else:
    registerCommands()
