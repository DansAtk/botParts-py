import sys
import os
import pathlib
import shutil

import sqlite3

import config
from core.commands import command, verifyCommand
from core import utils
from core import users
from core import places
from core import aliases
from core import groups

mSelf = sys.modules[__name__]
includes = {}
config.register(mSelf)
DB = config.database

class perm:
    def __init__(self, COMMAND, VALUE=0, TYPE=None, TARGET=None, ID=None):
        self.command = COMMAND
        self.value = VALUE
        self.type = TYPE
        self.target = TARGET
        self.id = ID

def getPerm(permid):
    if utils.checkDB():
        conn = sqlite3.connect(DB)
        cursor = conn.cursor()
        cursor.execute(
                "SELECT command, value, userid, placeid, aliasid, groupid "
                "FROM perms "
                "WHERE rowid = ?",
                (permid,)
                )
        result = cursor.fetchone()
        conn.close()

        if result:
            thisPerm = perm(result[0], result[1], ID=permid)
            if result[2]:
                thisPerm.type = 'user'
                thisPerm.target = result[2]
            if result[3]:
                thisPerm.type = 'place'
                thisPerm.target = result[3]
            if result[4]:
                thisPerm.type = 'alias'
                thisPerm.target = result[4]
            if result[5]:
                thisPerm.type = 'group'
                thisPerm.target = result[5]
            else:
                thisPerm.type = 'command'

            return thisPerm
        else:
            return None

def getPermbyType(profile):
    thisPerm = None

    if profile.type = 'command':
        thisPerm = getCommandPerm(profile.command)
    elif profile.type = 'user':
        thisPerm = getUserPerm(profile.command, profile.target)
    elif profile.type = 'place':
        thisPerm = getPlacePerm(profile.command, profile.target)
    elif profile.type = 'alias':
        thisPerm = getAliasPerm(profile.command, profile.target)
    elif profile.type = 'group':
        thisPerm = getGroupPerm(profile.command, profile.target)

    return thisPerm

def getCommandPerm(thisCommand):
    if utils.checkDB():
        conn = sqlite3.connect(DB)
        cursor = conn.cursor()
        cursor.execute(
                "SELECT rowid "
                "FROM perms "
                "WHERE command = ? AND userid IS NULL AND placeid IS NULL AND aliasid IS NULL AND groupid IS NULL",
                (thisCommand,)
                )
        result = cursor.fetchone()
        conn.close()

        if result:
            thisPerm = getPerm(result)
            return thisPerm
        else:
            return None

def getUserPerm(thisCommand, userid):
    if utils.checkDB():
        conn = sqlite3.connect(DB)
        cursor = conn.cursor()
        cursor.execute(
                "SELECT rowid "
                "FROM perms "
                "WHERE command = ? AND userid = ?",
                (thisCommand, userid)
                )
        result = cursor.fetchone()
        conn.close()

        if result:
            thisPerm = getPerm(result)
            return thisPerm
        else:
            return None

def getPlacePerm(thisCommand, placeid):
    if utils.checkDB():
        conn = sqlite3.connect(DB)
        cursor = conn.cursor()
        cursor.execute(
                "SELECT value "
                "FROM perms "
                "WHERE command = ? AND placeid = ?",
                (thisCommand, placeid)
                )
        result = cursor.fetchone()
        conn.close()

        if result:
            thisPerm = getPerm(result)
            return thisPerm
        else:
            return None

def getAliasPerm(thisCommand, aliasid):
    if utils.checkDB():
        conn = sqlite3.connect(DB)
        cursor = conn.cursor()
        cursor.execute(
                "SELECT value "
                "FROM perms "
                "WHERE command = ? AND aliasid = ?",
                (thisCommand, aliasid)
                )
        result = cursor.fetchone()
        conn.close()

        if result:
            thisPerm = getPerm(result)
            return thisPerm
        else:
            return None

def getGroupPerm(thisCommand, groupid):
    if utils.checkDB():
        conn = sqlite3.connect(DB)
        cursor = conn.cursor()
        cursor.execute(
                "SELECT value "
                "FROM perms "
                "WHERE command = ? AND groupid = ?",
                (thisCommand, groupid)
                )
        result = cursor.fetchone()
        conn.close()

        if result:
            thisPerm = getPerm(result)
            return thisPerm
        else:
            return None

def getCombinedPerm(inputData, thisCommand):
    userPerm = getUserPerm(thisCommand, inputData.user.id)
    placePerm = getPlacePerm(thisCommand, inputData.place.id)
    
    thisAlias = aliases.getAlias(inputData.user.id, inputData.place.id)
    if thisAlias:
        aliasPerm = getAliasPerm(thisCommand, thisAlias.id)

    groupPerm = getGroupPerm(thisCommand, thisGroup.id)

def addPermbyType(profile):
    if profile.type = 'command':
        addCommandPerm(profile)
    elif profile.type = 'user':
        addUserPerm(profile)
    elif profile.type = 'place':
        addPlacePerm(profile)
    elif profile.type = 'alias':
        addAliasPerm(profile)
    elif profile.type = 'group':
        addGroupPerm(profile)

def addCommandPerm(profile):
    if utils.checkDB():
        conn = sqlite3.connect(DB)
        cursor = conn.cursor()
        cursor.execute(
                "INSERT INTO perms"
                "(command, value) "
                "VALUES (?, ?)",
                (profile.command, profile.value)
                )
        conn.commit()
        conn.close()

def addUserPerm(profile):
    if utils.checkDB():
        conn = sqlite3.connect(DB)
        cursor = conn.cursor()
        cursor.execute(
                "INSERT INTO perms"
                "(command, userid, value) "
                "VALUES (?, ?, ?)",
                (profile.command, profile.target, profile.value)
                )
        conn.commit()
        conn.close()

def addPlacePerm(profile):
    if utils.checkDB():
        conn = sqlite3.connect(DB)
        cursor = conn.cursor()
        cursor.execute(
                "INSERT INTO perms"
                "(command, placeid, value) "
                "VALUES (?, ?, ?)",
                (profile.command, profile.target, profile.value)
                )
        conn.commit()
        conn.close()

def addAliasPerm(profile):
    if thisAlias:
        if utils.checkDB():
            conn = sqlite3.connect(DB)
            cursor = conn.cursor()
            cursor.execute(
                    "INSERT INTO perms"
                    "(command, aliasid, value) "
                    "VALUES (?, ?, ?)",
                    (profile.command, profile.target, profile.value)
                    )
            conn.commit()
            conn.close()

def addGroupPerm(profile):
    if utils.checkDB():
        conn = sqlite3.connect(DB)
        cursor = conn.cursor()
        cursor.execute(
                "INSERT INTO perms"
                "(command, groupid, value) "
                "VALUES (?, ?, ?)",
                (profile.command, profile.target, profile.value)
                )
        conn.commit()
        conn.close()

def removePerm(permid):
    if utils.checkDB():
        conn = sqlite3.connect(DB)
        conn.execute("PRAGMA foreign_keys = 1")
        cursor = conn.cursor()
        cursor.execute(
                "DELETE FROM perms "
                "WHERE id = ?",
                (permid,)
                )
        conn.commit()
        conn.close()

def removePermbyType(profile):
    if profile.type = 'command':
        removeCommandPerm(profile)
    elif profile.type = 'user':
        removeUserPerm(profile)
    elif profile.type = 'place':
        removePlacePerm(profile)
    elif profile.type = 'alias':
        removeAliasPerm(profile)
    elif profile.type = 'group':
        removeGroupPerm(profile)

def removeUserPerm(profile):
    if utils.checkDB():
        conn = sqlite3.connect(DB)
        conn.execute("PRAGMA foreign_keys = 1")
        cursor = conn.cursor()
        cursor.execute(
                "DELETE FROM perms "
                "WHERE command = ? AND userid = ?",
                (profile.command, profile.target,)
                )
        conn.commit()
        conn.close()

def removePlacePerm(profile):
    if utils.checkDB():
        conn = sqlite3.connect(DB)
        conn.execute("PRAGMA foreign_keys = 1")
        cursor = conn.cursor()
        cursor.execute(
                "DELETE FROM perms "
                "WHERE command = ? AND placeid = ?",
                (profile.command, profile.target)
                )
        conn.commit()
        conn.close()

def removeAliasPerm(profile):
    if utils.checkDB():
        conn = sqlite3.connect(DB)
        conn.execute("PRAGMA foreign_keys = 1")
        cursor = conn.cursor()
        cursor.execute(
                "DELETE FROM perms "
                "WHERE command = ? AND aliasid = ?",
                (profile.command, profile.target)
                )
        conn.commit()
        conn.close()
        
def removeGroupPerm(profile):
    if utils.checkDB():
        conn = sqlite3.connect(DB)
        conn.execute("PRAGMA foreign_keys = 1")
        cursor = conn.cursor()
        cursor.execute(
                "DELETE FROM perms "
                "WHERE command = ? AND groupid = ?",
                (profile.command, profile.target)
                )
        conn.commit()
        conn.close()

def updatePerm(profile):
    thisPerm = getPerm(profile.id)

    if thisPerm:
        if profile.value != thisPerm.value:
            if utils.checkDB():
                conn = sqlite3.connect(DB)
                cursor = conn.cursor()
                cursor.execute(
                        "UPDATE perms "
                        "SET value = ? "
                        "WHERE rowid = ?",
                        (profile.value, profile.id)
                        )
                conn.commit()
                conn.close()

def dbinit():
    try:
        conn = sqlite3.connect(DB)
        cursor = conn.cursor()
        config.debugQ.put('Configuring for permissions...')
        cursor.execute(
                "CREATE TABLE perms("
                "command TEXT NOT NULL, userid INTEGER, placeid INTEGER, aliasid INTEGER, groupid INTEGER, value INTEGER NOT NULL, "
                "PRIMARY KEY(command, userid, placeid, aliasid, groupid), "
                "FOREIGN KEY(userid) REFERENCES users(id) ON DELETE CASCADE ON UPDATE NO ACTION, "
                "FOREIGN KEY(placeid) REFERENCES places(id) ON DELETE CASCADE ON UPDATE NO ACTION, "
                "FOREIGN KEY(aliasid) REFERENCES aliases(rowid) ON DELETE CASCADE ON UPDATE NO ACTION, "
                "FOREIGN KEY(groupid) REFERENCES groups(id) ON DELETE CASCADE ON UPDATE NO ACTION)"
                )
        conn.commit()
        conn.close()
        config.debugQ.put('Success!')

    except:
        config.debugQ.put('Unable to configure permissions table!')

def registerCommands():
    global addPermC
    addPermC = command('perm', utils.addC)
    addPermC.description = ''
    addPermC.instruction = ''
    addPermC.function = 'addPermF'
    addPermC.parent_module = mSelf
    global removePermC
    removePermC = command('perm', utils.removeC)
    removePermC.description = ''
    removePermC.instruction = ''
    removePermC.function = 'removePermF'
    removePermC.parent_module = mSelf
    global editPermC
    editPermC = command('perm', utils.editC)
    editPermC.description = ''
    editPermC.instruction = ''
    editPermC.function = 'editPermF'
    editPermC.parent_module = mSelf
    global showPermC
    showPermC = command('perm', utils.showC)
    showPermC.description = ''
    showPermC.instruction = ''
    showPermC.function = 'showPermF'
    showPermC.parent_module = mSelf

def addPermF(inputData, content):
    permData = []
    permDetails = content

    for p in range(0, len(permDetails)):
        permData.append(permDetails[p].split('='))

    permDict = {}

    for q in permData:
        permDict.update({q[0] : q[1]})

    goodProfile = False

    if ('command' in permDict.keys()) and ('value' in permDict.keys()):
        if utils.isQuoted(permDict['command']):
            if verifyCommand(permDict['command'][1:-1]):
                thisPerm = perm(permDict['command'][1:-1].lower()))
                goodProfile = True

                if 'value' in permDict.keys():
                    if utils.isQuoted(permDict['value']):
                        thisPerm.value = int(permDict['value'][1:-1])
                    else:
                        goodProfile = False

                if all(x in permDict.keys() for x in ['user', 'place']):
                    if utils.isQuoted(permDict['user']) and utils.isQuoted(permDict['place']):
                        thisUser = users.tryGetOneUser(permDict['user'][1:-1])
                        thisPlace = places.tryGetOnePlace(permDict['place'][1:-1])
                        if thisUser and thisPlace:
                            thisAlias = aliases.getAlias(thisUser.id, thisPlace.id)
                            if thisAlias:
                                thisPerm.type = 'alias'
                                thisPerm.target = thisAlias.id
                            else:
                                goodProfile = False
                        else:
                            goodProfile = False
                    else:
                        goodProfile = False

                elif 'user' in permDict.keys():
                    if utils.isQuoted(permDict['user']):
                        thisUser = users.tryGetOneUser(permDict['user'][1:-1])
                        if thisUser:
                            thisPerm.type = 'user'
                            thisPerm.target = thisUser.id
                        else:
                            goodProfile = False
                    else:
                        goodProfile = False

                elif 'place' in permDict.keys():
                    if utils.isQuoted(permDict['place']):
                        thisPlace = places.tryGetOnePlace(permDict['place'][1:-1])
                        if thisPlace:
                            thisPerm.type = 'place'
                            thisPerm.target = thisPlace.id
                        else:
                            goodProfile = False
                    else:
                        goodProfile = False

                elif 'group' in permDict.keys():
                    if utils.isQuoted(permDict['group']):
                        thisGroup = groups.tryGetOneGroup(permDict['group'][1:-1])
                        if thisGroup:
                            thisPerm.type = 'group'
                            thisPerm.target = thisGroup.id
                        else:
                            goodProfile = False
                    else:
                        goodProfile = False

                else:
                    thisPerm.type = 'command'

    if goodProfile:
        addPermbyType(thisPerm)
        config.outQ.put('Added permission.')
    else:
        config.outQ.put('Invalid attribute(s).')

def removePermF(inputData, content):
    permData = []
    permDetails = content

    for p in range(0, len(permDetails)):
        permData.append(permDetails[p].split('='))

    permDict = {}

    for q in permData:
        permDict.update({q[0] : q[1]})

    goodProfile = False

    if ('command' in permDict.keys()) and ('value' in permDict.keys()):
        if utils.isQuoted(permDict['command']):
            if verifyCommand(permDict['command'][1:-1]):
                thisPerm = perm(permDict['command'][1:-1].lower()))
                goodProfile = True

                if all(x in permDict.keys() for x in ['user', 'place']):
                    if utils.isQuoted(permDict['user']) and utils.isQuoted(permDict['place']):
                        thisUser = users.tryGetOneUser(permDict['user'][1:-1])
                        thisPlace = places.tryGetOnePlace(permDict['place'][1:-1])
                        if thisUser and thisPlace:
                            thisAlias = aliases.getAlias(thisUser.id, thisPlace.id)
                            if thisAlias:
                                thisPerm.type = 'alias'
                                thisPerm.target = thisAlias.id
                            else:
                                goodProfile = False
                        else:
                            goodProfile = False
                    else:
                        goodProfile = False

                elif 'user' in permDict.keys():
                    if utils.isQuoted(permDict['user']):
                        thisUser = users.tryGetOneUser(permDict['user'][1:-1])
                        if thisUser:
                            thisPerm.type = 'user'
                            thisPerm.target = thisUser.id
                        else:
                            goodProfile = False
                    else:
                        goodProfile = False

                elif 'place' in permDict.keys():
                    if utils.isQuoted(permDict['place']):
                        thisPlace = places.tryGetOnePlace(permDict['place'][1:-1])
                        if thisPlace:
                            thisPerm.type = 'place'
                            thisPerm.target = thisPlace.id
                        else:
                            goodProfile = False
                    else:
                        goodProfile = False

                elif 'group' in permDict.keys():
                    if utils.isQuoted(permDict['group']):
                        thisGroup = groups.tryGetOneGroup(permDict['group'][1:-1])
                        if thisGroup:
                            thisPerm.type = 'group'
                            thisPerm.target = thisGroup.id
                        else:
                            goodProfile = False
                    else:
                        goodProfile = False

                else:
                    thisPerm.type = 'command'

    if goodProfile:
        existingPerm = getPermbyType(thisPerm)
        if existingPerm:
            removePerm(existingPerm.id)
            config.outQ.put('Removed permission.')
        else:
            config.outQ.put('Existing permission not found.')
    else:
        config.outQ.put('Invalid attribute(s).')

def editPermF(inputData, content):
    permData = []
    permDetails = content

    for p in range(0, len(permDetails)):
        permData.append(permDetails[p].split('='))

    permDict = {}

    for q in permData:
        permDict.update({q[0] : q[1]})

    goodProfile = False

    if ('command' in permDict.keys()) and ('value' in permDict.keys()):
        if utils.isQuoted(permDict['command']):
            if verifyCommand(permDict['command'][1:-1]):
                thisPerm = perm(permDict['command'][1:-1].lower()))
                goodProfile = True

                if 'value' in permDict.keys():
                    if utils.isQuoted(permDict['value']):
                        thisPerm.value = int(permDict['value'][1:-1])
                    else:
                        goodProfile = False

                if all(x in permDict.keys() for x in ['user', 'place']):
                    if utils.isQuoted(permDict['user']) and utils.isQuoted(permDict['place']):
                        thisUser = users.tryGetOneUser(permDict['user'][1:-1])
                        thisPlace = places.tryGetOnePlace(permDict['place'][1:-1])
                        if thisUser and thisPlace:
                            thisAlias = aliases.getAlias(thisUser.id, thisPlace.id)
                            if thisAlias:
                                thisPerm.type = 'alias'
                                thisPerm.target = thisAlias.id
                            else:
                                goodProfile = False
                        else:
                            goodProfile = False
                    else:
                        goodProfile = False

                elif 'user' in permDict.keys():
                    if utils.isQuoted(permDict['user']):
                        thisUser = users.tryGetOneUser(permDict['user'][1:-1])
                        if thisUser:
                            thisPerm.type = 'user'
                            thisPerm.target = thisUser.id
                        else:
                            goodProfile = False
                    else:
                        goodProfile = False

                elif 'place' in permDict.keys():
                    if utils.isQuoted(permDict['place']):
                        thisPlace = places.tryGetOnePlace(permDict['place'][1:-1])
                        if thisPlace:
                            thisPerm.type = 'place'
                            thisPerm.target = thisPlace.id
                        else:
                            goodProfile = False
                    else:
                        goodProfile = False

                elif 'group' in permDict.keys():
                    if utils.isQuoted(permDict['group']):
                        thisGroup = groups.tryGetOneGroup(permDict['group'][1:-1])
                        if thisGroup:
                            thisPerm.type = 'group'
                            thisPerm.target = thisGroup.id
                        else:
                            goodProfile = False
                    else:
                        goodProfile = False

                else:
                    thisPerm.type = 'command'

    if goodProfile:
        existingPerm = getPermbyType(thisPerm)
        if existingPerm:
            thisPerm.id = existingPerm.id
            updatePerm(thisPerm)
            config.outQ.put('Updated permission.')
        else:
            config.outQ.put('Existing permission not found.')
    else:
        config.outQ.put('Invalid attribute(s).')

def showPermF(inputData, content):
    permData = []
    permDetails = content

    for p in range(0, len(permDetails)):
        permData.append(permDetails[p].split('='))

    permDict = {}

    for q in permData:
        permDict.update({q[0] : q[1]})

    goodProfile = False

    if ('command' in permDict.keys()) and ('value' in permDict.keys()):
        if utils.isQuoted(permDict['command']):
            if verifyCommand(permDict['command'][1:-1]):
                thisPerm = perm(permDict['command'][1:-1].lower()))
                goodProfile = True

                if all(x in permDict.keys() for x in ['user', 'place']):
                    if utils.isQuoted(permDict['user']) and utils.isQuoted(permDict['place']):
                        thisUser = users.tryGetOneUser(permDict['user'][1:-1])
                        thisPlace = places.tryGetOnePlace(permDict['place'][1:-1])
                        if thisUser and thisPlace:
                            thisAlias = aliases.getAlias(thisUser.id, thisPlace.id)
                            if thisAlias:
                                thisPerm.type = 'alias'
                                thisPerm.target = thisAlias.id
                            else:
                                goodProfile = False
                        else:
                            goodProfile = False
                    else:
                        goodProfile = False

                elif 'user' in permDict.keys():
                    if utils.isQuoted(permDict['user']):
                        thisUser = users.tryGetOneUser(permDict['user'][1:-1])
                        if thisUser:
                            thisPerm.type = 'user'
                            thisPerm.target = thisUser.id
                        else:
                            goodProfile = False
                    else:
                        goodProfile = False

                elif 'place' in permDict.keys():
                    if utils.isQuoted(permDict['place']):
                        thisPlace = places.tryGetOnePlace(permDict['place'][1:-1])
                        if thisPlace:
                            thisPerm.type = 'place'
                            thisPerm.target = thisPlace.id
                        else:
                            goodProfile = False
                    else:
                        goodProfile = False

                elif 'group' in permDict.keys():
                    if utils.isQuoted(permDict['group']):
                        thisGroup = groups.tryGetOneGroup(permDict['group'][1:-1])
                        if thisGroup:
                            thisPerm.type = 'group'
                            thisPerm.target = thisGroup.id
                        else:
                            goodProfile = False
                    else:
                        goodProfile = False

                else:
                    thisPerm.type = 'command'

    if goodProfile:
        existingPerm = getPermbyType(thisPerm)
        if existingPerm:
            output_text = ''
            output_text += f'ID: {existingPerm.id}\n'
            output_text += f'Command: {existingPerm.command}\n'
            output_text += f'Type: {existingPerm.type}\n'
            output_text += f'Target: {existingPerm.target}\n'
            output_text += f'Value: {existingPerm.value}'
            config.outQ.put(output_text)
        else:
            config.outQ.put('Existing permission not found.')
    else:
        config.outQ.put('Invalid attribute(s).')

if __name__ == "__main__":
    print("No main.")
else:
    registerCommands()
