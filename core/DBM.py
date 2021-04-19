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
imports.append(__name__)

class user:
    def __init__(self, ID, NAME=None, TZ=None, BOTRANK=None, BDAY=None, COUNTRY=None, POINTS=None):
        self.id = ID 
        self.name = NAME
        self.tz = TZ
        self.botrank = BOTRANK
        self.bday = BDAY
        self.country = COUNTRY
        self.points = POINTS
        self.serverid = None
        self.nick = None
        self.color = None
        self.localrank = None

    def decorate(self, serverid):
        self.serverid = None
        self.nick = None
        self.color = None
        self.localrank = None

        conn = sqlite3.connect(config.database)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT nick, color, localrank "
            "FROM serverusers "
            "WHERE userid = ? AND serverid = ?",
            (self.id, serverid)
            )
            
        result = cursor.fetchone()
        conn.close()

        if result:
            self.serverid = serverid
            self.nick = result[0]
            self.color = result[1]
            self.localrank = result[2]
    
    def goesby(self, serverid=None):
        useName = ''

        if serverid:
            self.decorate(serverid)

        if self.nick:
            useName = self.nick
        else:
            useName = self.name

        return useName

    def now(self):
        if self.tz:
            return datetime.now(pytz.timezone(self.tz))
        
        else:
            return getTime()
            
def getUser(userid, serverid=None):
    DB = config.database

    if checkDB():
        conn = sqlite3.connect(DB)
        cursor = conn.cursor()
        cursor.execute(
                "SELECT name, tz, botrank, bday, country, points "
                "FROM users "
                "WHERE id = ?",
                (userid,)
                )
        result = cursor.fetchone()
        conn.close()

        if result:
            thisUser = user(userid)
            thisUser.name = result[0]
            thisUser.tz = result[1]
            thisUser.botrank = result[2]
            thisUser.bday = result[3]
            thisUser.country = result[4]
            thisUser.points = result[5]
            
            if serverid:
                thisUser.decorate(serverid)

            return thisUser

        else:
            return None

def tryGetOneUser(userstring):
    thisUser = None

    try:
        thisUser = getUser(int(userstring))

    except ValueError:
        searchResults = searchUserbyName(userstring)
        
        if searchResults:
            if len(searchResults) == 1:
                thisUser = searchResults[0]
    
    return thisUser

def addUser(profile):
    DB = config.database
    if checkDB():
        conn = sqlite3.connect(DB)
        cursor = conn.cursor()
        cursor.execute(
                "INSERT INTO users"
                "(id, name, botrank, country, tz, bday, points) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)",
                (profile.id, profile.name, profile.botrank,
                    profile.country, profile.tz, profile.bday, profile.points)
                )
        conn.commit()
        conn.close()

        addUserAlias(profile)

def removeUser(profile):
    DB = config.database
    if checkDB():
        conn = sqlite3.connect(DB)
        conn.execute("PRAGMA foreign_keys = 1")
        cursor = conn.cursor()
        cursor.execute(
                "DELETE FROM users "
                "WHERE id = ?",
                (profile.id,)
                )
        conn.commit()
        conn.close()

def updateUser(profile):
    thisUser = getUser(profile.id)

    if thisUser:
        if profile.name:
            thisUser.name = profile.name
        if profile.botrank:
            thisUser.botrank = profile.botrank
        if profile.country:
            thisUser.country = profile.country
        if profile.tz:
            thisUser.tz = profile.tz
        if profile.bday:
            thisUser.bday = profile.bday
        if profile.points:
            thisUser.points = profile.points
        
        DB = config.database
        if checkDB():
            conn = sqlite3.connect(DB)
            cursor = conn.cursor()
            cursor.execute(
                    "UPDATE users SET "
                    "name = ?, botrank = ?, country = ?, tz = ?, bday = ?, points = ? "
                    "WHERE id = ?",
                    (thisUser.name, thisUser.botrank, thisUser.country, thisUser.tz, thisUser.bday, thisUser.points, thisUser.id)
                    )
            conn.commit()
            conn.close()

def searchUserbyName(searchstring, serverid=None):
    DB = config.database
    if checkDB():
        conn = sqlite3.connect(DB)
        cursor = conn.cursor()

        if serverid:
            cursor.execute(
                    "SELECT users.id "
                    "FROM users JOIN serverusers ON users.id = serverusers.userid "
                    "WHERE (users.name LIKE ?) OR (serverusers.serverid = ? AND serverusers.nick LIKE ?)",
                    ('%{}%'.format(searchstring), serverid, '%{}%'.format(searchstring))
                    )
        else:
            cursor.execute(
                    "SELECT id "
                    "FROM users "
                    "WHERE name LIKE ?",
                    ('%{}%'.format(searchstring),)
                    )

        search = cursor.fetchall()
        conn.close()

        if len(search) > 0:
            foundUsers = []
            for result in search:
                thisUser = getUser(result[0], serverid)
                foundUsers.append(thisUser)

            return foundUsers

        else:
            return None

def searchUserbyCountry(searchstring, serverid=None):
    DB = config.database
    if checkDB():
        conn = sqlite3.connect(DB)
        cursor = conn.cursor()
        cursor.execute(
                "SELECT id "
                "FROM users "
                "WHERE country LIKE ?",
                ('%{}%'.format(searchstring),)
                )
        search = cursor.fetchall()
        conn.close()

        if len(search) > 0:
            foundUsers = []
            for result in search:
                thisUser = getUser(result[0], serverid)
                foundUsers.append(thisUser)

            return foundUsers

        else:
            return None

def searchUserbyTimezone(searchstring, serverid=None):
    DB = config.database
    if checkDB():
        conn = sqlite3.connect(DB)
        cursor = conn.cursor()
        cursor.execute(
                "SELECT id "
                "FROM users "
                "WHERE tz LIKE ?",
                ('%{}%'.format(searchstring),)
                )
        search = cursor.fetchall()
        conn.close()

        if len(search) > 0:
            foundUsers = []
            for result in search:
                thisUser = getUser(result[0], serverid)
                foundUsers.append(thisUser)

            return foundUsers

        else:
            return None

def searchUserbyBirthday(searchstring, serverid=None):
    DB = config.database
    if checkDB():
        conn = sqlite3.connect(DB)
        cursor = conn.cursor()
        cursor.execute(
                "SELECT id "
                "FROM users "
                "WHERE bday = ?",
                (searchstring,)
                )
        search = cursor.fetchall()
        conn.close()

        if len(search) > 0:
            foundUsers = []
            for result in search:
                thisUser = getUser(result[0], serverid)
                foundUsers.append(thisUser)

            return foundUsers

        else:
            return None

def searchUserbyColor(searchColor, searchServer):
    DB = config.database
    if checkDB():
        conn = sqlite3.connect(DB)
        cursor = conn.cursor()
        cursor.execute(
                "SELECT userid "
                "FROM serverusers "
                "WHERE serverid = ? AND color = ?",
                (searchServer.id, searchColor.id)
                )
        search = cursor.fetchall()
        conn.close()

        if len(search) > 0:
            foundUsers = []
            for result in search:
                thisUser = getUser(result[0], searchServer.id)
                foundUsers.append(thisUser)

            return foundUsers

        else:
            return None

def searchUserbyServer(searchServer):
    DB = config.database
    if checkDB():
        conn = sqlite3.connect(DB)
        cursor = conn.cursor()
        cursor.execute(
                "SELECT userid "
                "FROM serverusers "
                "WHERE serverid = ?",
                (searchServer.id,)
                )
        search = cursor.fetchall()
        conn.close()

        if len(search) > 0:
            foundUsers = []
            for result in search:
                thisUser = getUser(result[0], searchServer.id)
                foundUsers.append(thisUser)

            return foundUsers

        else:
            return None

class server:
    def __init__(self, ID, NAME=None, TRIGGER='!', TZ=None):
        self.id = ID
        self.name = NAME
        self.trigger = TRIGGER
        self.tz = TZ

    def now(self):
        if self.tz:
            return datetime.now(pytz.timezone(self.tz))
        
        else:
            return getTime()

def getServer(serverid):
    DB = config.database
    if checkDB():
        conn = sqlite3.connect(DB)
        cursor = conn.cursor()
        cursor.execute(
                "SELECT name, trigger, tz FROM servers WHERE id = ?",
                (serverid,)
                )
        result = cursor.fetchone()
        conn.close()
        
        if result:
            thisServer = server(serverid)
            thisServer.name = result[0]
            thisServer.trigger = result[1]
            thisServer.tz = result[2]

            return thisServer
        
        else:
            return None

def tryGetOneServer(serverstring):
    thisServer = None

    try:
        thisServer = getServer(int(serverstring))

    except ValueError:
        searchResults = searchServerbyName(serverstring)
        
        if searchResults:
            if len(searchResults) == 1:
                thisServer = searchResults[0]
    
    return thisServer

def addServer(profile):
    DB = config.database
    if checkDB():
        conn = sqlite3.connect(DB)
        cursor = conn.cursor()
        cursor.execute(
                "INSERT INTO servers"
                "(id, name, trigger, tz) "
                "VALUES (?, ?, ?, ?)",
                (profile.id, profile.name, profile.trigger, profile.tz)
                )
        conn.commit()
        conn.close()

def removeServer(profile):
    DB = config.database
    if checkDB():
        conn = sqlite3.connect(DB)
        conn.execute("PRAGMA foreign_keys = 1")
        cursor = conn.cursor()
        cursor.execute(
                "DELETE FROM servers "
                "WHERE id = ?",
                (profile.id,)
                )
        conn.commit()
        conn.close()

def updateServer(profile):
    thisServer = getServer(profile.id)

    if thisServer:
        if profile.name:
            thisServer.name = profile.name
        if profile.trigger:
            thisServer.trigger = profile.trigger
        if profile.tz:
            thisServer.tz = profile.tz
        
        DB = config.database
        if checkDB():
            conn = sqlite3.connect(DB)
            cursor = conn.cursor()
            cursor.execute(
                    "UPDATE servers SET "
                    "name = ?, trigger = ?, tz = ? "
                    "WHERE id = ?",
                    (thisServer.name, thisServer.trigger, thisServer.tz, thisServer.id)
                    )
            conn.commit()
            conn.close()

def searchServerbyName(searchstring):
    DB = config.database
    if checkDB():
        conn = sqlite3.connect(DB)
        cursor = conn.cursor()
        cursor.execute(
                "SELECT id "
                "FROM servers "
                "WHERE name LIKE ?",
                ('%{}%'.format(searchstring),)
                )
        search = cursor.fetchall()
        conn.close()

        if len(search) > 0:
            foundServers = []
            for result in search:
                thisServer = getServer(result[0])
                foundServers.append(thisServer)

            return foundServers

        else:
            return None

def searchServerbyTimezone(searchstring):
    DB = config.database
    if checkDB():
        conn = sqlite3.connect(DB)
        cursor = conn.cursor()
        cursor.execute(
                "SELECT id "
                "FROM servers "
                "WHERE tz LIKE ?",
                ('%{}%'.format(searchstring),)
                )
        search = cursor.fetchall()
        conn.close()

        if len(search) > 0:
            foundServers = []
            for result in search:
                thisServer = getServer(result[0])
                foundServers.append(thisServer)

            return foundServers

        else:
            return None

def searchServerbyUser(searchUser):
    DB = config.database
    if checkDB():
        conn = sqlite3.connect(DB)
        cursor = conn.cursor()
        cursor.execute(
                "SELECT serverid "
                "FROM serverusers "
                "WHERE userid = ?",
                (searchUser.id,)
                )
        search = cursor.fetchall()
        conn.close()

        if len(search) > 0:
            foundServers = []
            for result in search:
                thisServer = getServer(result[0])
                foundServers.append(thisServer)

            return foundServers

        else:
            return None

def getUserAlias(userprofile, serverprofile):
    DB = config.database

    if checkDB():
        thisUser = user(userprofile.id)
        thisUser.decorate(serverprofile.id)

        if thisUser.serverid:
            return thisUser

        else:
            return None

def addUserAlias(profile):
    if profile.serverid:
        if getServer(profile.serverid):
            DB = config.database
            if checkDB():
                conn = sqlite3.connect(DB)
                cursor = conn.cursor()
                cursor.execute(
                        "INSERT INTO serverusers"
                        "(userid, serverid, nick, color, localrank) "
                        "VALUES (?, ?, ?, ?, ?)",
                        (profile.id, profile.serverid, profile.nick, profile.color, profile.localrank)
                        )
                conn.commit()
                conn.close()

def removeUserAlias(userprofile, serverprofile):
    DB = config.database
    if checkDB():
        conn = sqlite3.connect(DB)
        conn.execute("PRAGMA foreign_keys = 1")
        cursor = conn.cursor()
        cursor.execute(
                "DELETE FROM serverusers "
                "WHERE userid = ? AND serverid = ?",
                (userprofile.id, serverprofile.id)
                )
        conn.commit()
        conn.close()

def updateUserAlias(profile):
    thisServer = tryGetOneServer(profile.serverid)
    thisAlias = getUserAlias(profile, thisServer)

    if thisAlias:
        if profile.nick:
            thisAlias.nick = profile.nick
        if profile.color:
            thisAlias.color = profile.color
        if profile.localrank:
            thisAlias.localrank = profile.localrank

        DB = config.database
        if checkDB():
            conn = sqlite3.connect(DB)
            cursor = conn.cursor()
            cursor.execute(
                    "UPDATE serverusers SET "
                    "nick = ?, color = ?, localrank = ? "
                    "WHERE userid = ? AND serverid = ?",
                    (thisAlias.nick, thisAlias.color, thisAlias.localrank, thisAlias.id, thisAlias.serverid)
                    )
            conn.commit()
            conn.close()

def getTime():
    return datetime.now(pytz.timezone('US/Eastern'))

def getTimezone(tzname):
    return tryGetOneTimezone(tzname)

def tryGetOneTimezone(timezonestring):
    thisTimezone = None

    searchResults = searchTimezonebyName(timezonestring)

    if searchResults:
        if len(searchResults) == 1:
            thisTimezone = searchResults[0]

    return thisTimezone

def searchTimezonebyName(userinput):
    foundTZ = []
    
    for timezone in pytz.all_timezones:
        if userinput.lower() in timezone.lower():
            foundTZ.append(timezone)

    if len(foundTZ) > 0:
        return foundTZ
    
    else:
        return None

class color:
    def __init__(self, ID, NAME=None, CODE=None):
        self.id = ID
        self.name = NAME
        self.code = CODE

def getColor(colorid):
    DB = config.database
    if checkDB():
        conn = sqlite3.connect(DB)
        cursor = conn.cursor()
        cursor.execute(
                "SELECT name, code FROM colors WHERE id = ?",
                (colorid,)
                )
        result = cursor.fetchone()
        conn.close()
        
        if result:
            thisColor = color(colorid)
            thisColor.name = result[0]
            thisColor.code = result[1]

            return thisColor
        
        else:
            return None

def tryGetOneColor(colorstring):
    thisColor = None

    try:
        thisColor = getColor(int(colorstring))

    except ValueError:
        searchResults = searchColorbyName(colorstring)
        
        if searchResults:
            if len(searchResults) == 1:
                thisColor = searchResults[0]
    
    return thisColor

def addColor(profile):
    DB = config.database
    if checkDB():
        conn = sqlite3.connect(DB)
        cursor = conn.cursor()
        cursor.execute(
                "INSERT INTO colors"
                "(id, name, code) "
                "VALUES (?, ?, ?)",
                (profile.id, profile.name, profile.code)
                )
        conn.commit()
        conn.close()

def removeColor(profile):
    DB = config.database
    if checkDB():
        conn = sqlite3.connect(DB)
        conn.execute("PRAGMA foreign_keys = 1")
        cursor = conn.cursor()
        cursor.execute(
                "DELETE FROM colors "
                "WHERE id = ?",
                (profile.id,)
                )
        conn.commit()
        conn.close()

def updateColor(profile):
    thisColor = getColor(profile.id)

    if thisColor:
        if profile.name:
            thisColor.name = profile.name
        if profile.code:
            thisColor.code = profile.code
        
        DB = config.database
        if checkDB():
            conn = sqlite3.connect(DB)
            cursor = conn.cursor()
            cursor.execute(
                    "UPDATE colors SET "
                    "name = ?, code = ? "
                    "WHERE id = ?",
                    (thisColor.name, thisColor.code, thisColor.id)
                    )
            conn.commit()
            conn.close()

def searchColorbyName(searchstring):
    DB = config.database
    if checkDB():
        conn = sqlite3.connect(DB)
        cursor = conn.cursor()
        cursor.execute(
                "SELECT id "
                "FROM colors "
                "WHERE name LIKE ?",
                ('%{}%'.format(searchstring),)
                )
        search = cursor.fetchall()
        conn.close()

        if len(search) > 0:
            foundColors = []
            for result in search:
                thisColor = getColor(result[0])
                foundColors.append(thisColor)

            return foundColors

        else:
            return None

def checkDB():
    DB = config.database

    if DB.exists():
        return True

    else:
        config.debugQ.put('Database not found.')
        return False

def backupDB():
    if checkDB():
        timestamp = (datetime.now()).strftime("%Y%m%d%H%M%S%f")
    
        if not config.backupPath.exists():
            config.backupPath.mkdir()

        backupFile = config.backupPath / ('{dbname}_backup_{code}.db'.format(dbname=config.database.stem, code=timestamp))
    
        shutil.copy2(config.database, backupFile)

        return backupFile

def cleanup():
    databaseBackupF()

def registerCommands():
    global databaseC
    databaseC = command('database', mSelf)
    databaseC.description = 'Commands for managing the bot\'s database.'
    databaseC.instruction = 'Specify a parameter. Alone, displays information about the database\'s current state.'
    databaseC.function = 'databaseF'
    global databaseSetupC
    databaseSetupC = command('setup', databaseC)
    databaseSetupC.description = 'Initializes the database. If the database already exists, it can be reinitialized.'
    databaseSetupC.function = 'databaseSetupF'
    global databaseDeleteC
    databaseDeleteC = command('delete', databaseC)
    databaseDeleteC.description = 'Deletes the database.' 
    databaseDeleteC.function = 'databaseDeleteF'
    global databaseBackupC
    databaseBackupC = command('backup', databaseC)
    databaseBackupC.description = 'Creates a backup of the database.'
    databaseBackupC.function = 'databaseBackupF'
    global addC
    addC = command('add', mSelf)
    addC.description = 'Used to create new objects in the database.'
    addC.instruction = 'Specify a parameter.'
    global addUserC
    addUserC = command('user', addC)
    addUserC.description = 'Builds a user from parameters, then adds it to the database.'
    addUserC.instruction = 'Specify user attributes using \'Attribute=Value\' with each separated by a space. \'id\' is required.'
    addUserC.function = 'addUserF'
    global addUserAliasC
    addUserAliasC = command('alias', addUserC)
    addUserAliasC.description = 'Builds a user alias from parameters, then adds it to the database.'
    addUserAliasC.instruction = 'First specify a user and server. Then, specify alias attributes using \'Attribute=Value\' with each separated by a space.'
    addUserAliasC.function = 'addUserAliasF'
    global addServerC
    addServerC = command('server', addC)
    addServerC.description = 'Builds a server from parameters, then adds it to the database.'
    addServerC.instruction = 'Specify server attributes using \'Attribute=Value\' with each separated by a space. \'id\' is required.'
    addServerC.function = 'addServerF'
    global addColorC
    addColorC = command('color', addC)
    addColorC.description = 'Adds a color with the given name and code to the database.'
    addColorC.instruction = 'Specify color attributes using \'Attribute=Value\' with each separated by a space.'
    addColorC.function = 'addColorF'
    global removeC
    removeC = command('remove', mSelf)
    removeC.description = 'Used to remove existing objects from the database.'
    removeC.instruction = 'Specify a parameter.'
    global removeUserC
    removeUserC = command('user', removeC)
    removeUserC.description = 'Removes a user from the database.'
    removeUserC.instruction = 'Specify a user.'
    removeUserC.function = 'removeUserF'
    global removeUserAliasC
    removeUserAliasC = command('alias', removeUserC)
    removeUserAliasC.description = 'Removes a user alias from the database.'
    removeUserAliasC.instruction = 'Specify a user and server.'
    removeUserAliasC.function = 'removeUserAliasF'
    global removeServerC
    removeServerC = command('server', removeC)
    removeServerC.description = 'Removes a server from the database.'
    removeServerC.instruction = 'Specify a server.'
    removeServerC.function = 'removeServerF'
    global removeColorC
    removeColorC = command('color', removeC)
    removeColorC.description = 'Removes a color from the database.'
    removeColorC.instruction = 'Specify a color.'
    removeColorC.function = 'removeColorF'
    global editC
    editC = command('edit', mSelf)
    editC.description = 'Updates existing objects with new attributes.'
    editC.instruction = 'Specify a parameter.'
    global editUserC
    editUserC = command('user', editC)
    editUserC.description = 'Updates an existing user with new attributes.'
    editUserC.instruction = 'First specify a user. Then, specify new attributes using \'Attribute=Value\' with each separated by a space.'
    editUserC.function = 'editUserF'
    global editUserAliasC
    editUserAliasC = command('alias', editUserC)
    editUserAliasC.description = 'Updates an existing user alias with new attributes.'
    editUserAliasC.instruction = 'First specify a user and server. Then, specify new attributes using \'Attribute=Value\' with each separated by a space.'
    editUserAliasC.function = 'editUserAliasF'
    global editServerC
    editServerC = command('server', editC)
    editServerC.description = 'Updates an existing server with new attributes.'
    editServerC.instruction = 'First specify a server. Then, specify new attributes using \'Attribute=Value\' with each separated by a space.'
    editServerC.function = 'editServerF'
    global editColorC
    editColorC = command('color', editC)
    editColorC.description = 'Updates an existing color with new attributes.'
    editColorC.instruction = 'First specify a color. Then, specify new attributes using \'Attribute=Value\' with each separated by a space.'
    editColorC.function = 'editColorF'
    global showC
    showC = command('show', mSelf)
    showC.description = 'Displays detailed information about database objects.'
    showC.instruction = 'Specify a parameter.'
    global showUserC
    showUserC = command('user', showC)
    showUserC.description = 'Displays detailed information about a single user.'
    showUserC.instruction = 'Specify a user.'
    showUserC.function = 'showUserF'
    global showUserAliasC
    showUserAliasC = command('alias', showUserC)
    showUserAliasC.description = 'Displays detailed information about a user\'s specific alias on a server.'
    showUserAliasC.instruction = 'Specify a user and server.'
    showUserAliasC.function = 'showUserAliasF'
    global showServerC
    showServerC = command('server', showC)
    showServerC.description = 'Displays detailed information about a single server.'
    showServerC.instruction = 'Specify a server.'
    showServerC.function = 'showServerF'
    global showColorC
    showColorC = command('color', showC)
    showColorC.description = 'Displays detailed information about a single color.'
    showColorC.instruction = 'Specify a color.'
    showColorC.function = 'showColorF'
    global listC
    listC = command('list', mSelf)
    listC.description = 'Lists all objects of the given type currently in the database.'
    listC.instruction = 'Specify a parameter.'
    global listUserC
    listUserC = command('user', listC)
    listUserC.description = 'Lists all users in the database.'
    listUserC.function = 'listUserF'
    global listUserAliasC
    listUserAliasC = command('alias', listUserC)
    listUserAliasC.description = 'Lists all of a user\'s aliases across all servers in the database.'
    listUserAliasC.instruction = 'Specify a user.'
    listUserAliasC.function = 'listUserAliasF'
    global listServerC
    listServerC = command('server', listC)
    listServerC.description = 'Lists all servers in the database.'
    listServerC.function = 'listServerF'
    global listColorC
    listColorC = command('color', listC)
    listColorC.description = 'Lists all colors in the database.'
    listColorC.function = 'listColorF'
    global listTimezoneC
    listTimezoneC = command('timezone', listC)
    listTimezoneC.description = 'Lists all available timezones.'
    listTimezoneC.function = 'listTimezoneF'
    global timeC
    timeC = command('time', mSelf)
    timeC.description = 'Displays the current time.'
    timeC.function = 'timeF'
    global timeForC
    timeForC = command('for', timeC)
    timeForC.description = 'Displays the time in a specific user\'s timezone.'
    timeForC.instruction = 'Specify a user.'
    timeForC.function = 'timeForF'
    global timeZonesC
    timeZonesC = command('zones', timeC)
    timeZonesC.description = 'Lists all available timezones.'
    timeZonesC.function = 'listTimezoneF'
    global findC
    findC = command('find', mSelf)
    findC.description = 'Searches for objects meeting the given criteria.'
    findC.instruction = 'Specify a parameter.'
    global findUserC
    findUserC = command('user', findC)
    findUserC.description = 'Searches for users meeting the given criteria.'
    findUserC.instruction = 'Specify a parameter.'
    global findUserNameC
    findUserNameC = command('name', findUserC)
    findUserNameC.description = 'Searches for users with names and/or nicknames matching the given query.'
    findUserNameC.instruction = 'Specify a name or nickname.'
    findUserNameC.function = 'findUserNameF'
    global findUserCountryC
    findUserCountryC = command('country', findUserC)
    findUserCountryC.description = 'Searches for users with countries matching the given query.'
    findUserCountryC.instruction = 'Specify a country.'
    findUserCountryC.function = 'findUserCountryF'
    global findUserTimezoneC
    findUserTimezoneC = command('timezone', findUserC)
    findUserTimezoneC.description = 'Searches for users with timezones matching the given query.'
    findUserTimezoneC.instruction = 'Specify a timezone.'
    findUserTimezoneC.function = 'findUserTimezoneF'
    global findUserBirthdayC
    findUserBirthdayC = command('birthday', findUserC)
    findUserBirthdayC.description = 'Searches for users with birthdays matching the given query.'
    findUserBirthdayC.instruction = 'Specify a birthday in format DD-MM.'
    findUserBirthdayC.function = 'findUserBirthdayF'
    global findUserColorC
    findUserColorC = command('color', findUserC)
    findUserColorC.description = 'Searches for users with colors matching the given query.'
    findUserColorC.instruction = 'Specify a color.'
    findUserColorC.function = 'findUserColorF'
    global findServerC
    findServerC = command('server', findC)
    findServerC.description = 'Searches for servers meeting the given criteria.'
    findServerC.instruction = 'Specify a parameter.'
    global findServerNameC
    findServerNameC = command('name', findServerC)
    findServerNameC.description = 'Searches for servers with names matching the given query.'
    findServerNameC.instruction = 'Specify a name or nickname.'
    findServerNameC.function = 'findServerNameF'
    global findServerTimezoneC
    findServerTimezoneC = command('timezone', findServerC)
    findServerTimezoneC.description = 'Searches for servers with timezones matching the given query.'
    findServerTimezoneC.instruction = 'Specify a timezone.'
    findServerTimezoneC.function = 'findServerTimezoneF'
    global findTimezoneC
    findTimezoneC = command('timezone', findC)
    findTimezoneC.description = 'Searches for timezones with names matching the given query.'
    findTimezoneC.instruction = 'Specify the name of a timezone.'
    findTimezoneC.function = 'findTimezoneF'
    global findColorC
    findColorC = command('color', findC)
    findColorC.description = 'Searches for colors with names matching the given query.'
    findColorC.instruction = 'Specify the name of a color.'
    findColorC.function = 'findColorF'

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
