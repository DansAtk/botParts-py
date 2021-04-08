import sys
import os
import pathlib
import shutil

import sqlite3
import pytz
import calendar
from datetime import *

from core import config
from core.commandM import command

mSelf = sys.modules[__name__]
includes = {}
config.imports.append(__name__)

class user:
    def __init__(self, ID, NAME=None, TZ='US/Eastern', BOTRANK=None, BDAY=None, COUNTRY=None, POINTS=None):
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
            "SELECT nick, color, localrank
            FROM serverusers
            WHERE userid = ? AND serverid = ?",
            (self.id, serverid)
            )
            
        result = cursor.fetchone()
        conn.close()

        if result:
            self.serverid = serverid
            self.nick = result[0]
            self.color = result[1]
            self.localrank = result[2]
        else:
            print('No record found.')
    
    def goesby(self, serverid):
        useName = ''

        if serverid != self.serverid:
            self.decorate(serverid)

        if self.nick:
            useName = self.nick
        else:
            useName = self.name

        return useName
            
def getUser(userid, serverid=None):
    DB = config.database

    if DB.exists():
        conn = sqlite3.connect(DB)
        cursor = conn.cursor()
        cursor.execute(
                "SELECT name, tz, botrank, bday, country, points
                FROM users
                WHERE id = ?",
                (userid,)
                )
        result = cursor.fetchone()

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
            print('user not found')

            return None

def addUser(profile):
    DB = config.database
    if DB.exists():
        conn = sqlite3.connect(DB)
        cursor = conn.cursor()
        cursor.execute(
                "INSERT INTO users(
                id, name, botrank, country, tz, bday, points)
                VALUES (?, ?, ?, ?, ?, ?, ?)",
                (profile.id, profile.name, profile.botrank,
                    profile.country, profile.tz, profile.bday, profile.points)
                )
        conn.commit()
        conn.close()

        addUserAlias(profile)

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
        if DB.exists():
            conn = sqlite3.connect(DB)
            cursor = conn.cursor()
            cursor.execute(
                    "UPDATE users SET
                    name = ?, botrank = ?, country = ?, tz = ?, bday = ?, points = ?
                    WHERE id = ?",
                    (thisUser.name, thisUser.botrank, thisUser.country, thisUser.tz, thisUser.bday, thisUser.points, thisUser.id)
                    )
            conn.commit()
            conn.close()

def searchUserbyName(searchstring, serverid=None):
    DB = config.database
    if DB.exists():
        conn = sqlite3.connect(DB)
        cursor = conn.cursor()

        if serverid:
            cursor.execute(
                    "SELECT users.id
                    FROM users JOIN serverusers ON users.id = serverusers.userid
                    WHERE (users.name LIKE ?) OR (serverusers.serverid = ? AND serverusers.nick LIKE ?)",
                    ('%{}%'.format(searchstring), serverid, '%{}%'.format(searchstring))
                    )
        else:
            cursor.execute(
                    "SELECT id
                    FROM users
                    WHERE name LIKE ?",
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
    if DB.exists():
        conn = sqlite3.connect(DB)
        cursor = conn.cursor()
        cursor.execute(
                "SELECT id
                FROM users
                WHERE country LIKE ?",
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

def searchUserbyTZ(searchstring, serverid=None):
    DB = config.database
    if DB.exists():
        conn = sqlite3.connect(DB)
        cursor = conn.cursor()
        cursor.execute(
                "SELECT id
                FROM users
                WHERE tz LIKE ?",
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

def searchUserbyBDay(searchstring, serverid=None):
    DB = config.database
    if DB.exists():
        conn = sqlite3.connect(DB)
        cursor = conn.cursor()
        cursor.execute(
                "SELECT id
                FROM users
                WHERE bday = ?",
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

def searchUserbyColor(searchstring, serverid):
    DB = config.database
    if DB.exists():
        conn = sqlite3.connect(DB)
        cursor = conn.cursor()
        cursor.execute(
                "SELECT userid
                FROM serverusers
                WHERE serverid = ? AND color = ?",
                (serverid, searchstring)
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

class server:
    def __init__(self, ID, NAME=None, TRIGGER='!', TZ='US/Eastern'):
        self.id = ID
        self.name = NAME
        self.trigger = TRIGGER
        self.tz = TZ

def getServer(serverid):
    DB = config.database
    if DB.exists():
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
            print('Server not found!')
            
            return None

def addServer(profile):
    DB = config.database
    if DB.exists():
        conn = sqlite3.connect(DB)
        cursor = conn.cursor()
        cursor.execute(
                "INSERT INTO servers(
                id, name, trigger, tz)
                VALUES (?, ?, ?, ?)",
                (profile.id, profile.name, profile.trigger, profile.tz)
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
        if DB.exists():
            conn = sqlite3.connect(DB)
            cursor = conn.cursor()
            cursor.execute(
                    "UPDATE servers SET
                    name = ?, trigger = ?, tz = ?
                    WHERE id = ?",
                    (thisServer.name, thisServer.trigger, thisServer.tz, thisServer.id)
                    )
            conn.commit()
            conn.close()

def searchServerbyName(searchstring):
    DB = config.database
    if DB.exists():
        conn = sqlite3.connect(DB)
        cursor = conn.cursor()
        cursor.execute(
                "SELECT id
                FROM servers
                WHERE name LIKE ?",
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

def searchServerbyTZ(searchstring):
    DB = config.database
    if DB.exists():
        conn = sqlite3.connect(DB)
        cursor = conn.cursor()
        cursor.execute(
                "SELECT id
                FROM servers
                WHERE tz LIKE ?",
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

def getUserAlias(userid, serverid):
    DB = config.database

    if DB.exists():
        thisUser = user(userid)
        thisUser.decorate(serverid)

        if thisUser.serverid:

            return thisUser

        else:
            print('User alias not found')

            return None

def addUserAlias(profile):
    if profile.serverid:
        if getServer(profile.serverid):
            DB = config.database
            if DB.exists():
                conn = sqlite3.connect(DB)
                cursor = conn.cursor()
                cursor.execute(
                        "INSERT INTO serverusers(
                        userid, serverid, nick, color, localrank)
                        VALUES (?, ?, ?, ?, ?)",
                        (profile.id, profile.serverid, profile.nick, profile.color, profile.localrank)
                        )
                conn.commit()
                conn.close()

def updateUserAlias(profile):
    thisUser = getUserAlias(profile.id, profile.serverid)

    if thisUser:
        if profile.nick:
            thisUser.nick = profile.nick
        if profile.color:
            thisUser.color = profile.color
        if profile.localrank:
            thisUser.localrank = profile.localrank

        DB = config.database
        if DB.exists():
            conn = sqlite3.connect(DB)
            cursor = conn.cursor()
            cursor.execute(
                    "UPDATE serverusers SET
                    nick = ?, color = ?, localrank = ?
                    WHERE userid = ? AND serverid = ?",
                    (thisUser.nick, thisUser.color, thisUser.localrank, thisUser.id, thisUser.serverid)
                    )
            conn.commit()
            conn.close()

def getTime(reference=None):
    if reference:
        return datetime.datetime.now(pytz.timezone(reference.tz))
    else:
        return datetime.datetime.now(pytz.timezone('US/Eastern'))

def searchTZ(userinput):
    foundTZ = []
    
    for timezone in pytz.all_timezones:
        if userinput in timezone:
            foundTZ.append(timezone)

    if len(foundTZ) > 0:
        return foundTZ
    
    else:
        return None

def init():
    global databaseC
    databaseC = command('database', mSelf)
    databaseC.description = 'Commands for managing the bot\'s database. Alone, displays information about the database\'s current state.'
    databaseC.function = 'databaseF'
    global databaseSetupC
    databaseSetupC = command('setup', databaseC)
    databaseSetupC.description = 'Initializes the database. If the database already exists, it can be reinitialized or reconfigured, based on imported modules.'
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
    addC.function = 'addF'
    global addUserC
    addUserC = command('user', addC)
    addUserC.description = 'Builds a user from parameters, then adds it to the database.'
    addUserC.function = 'addUserF'
    global addServerC
    addServerC = command('server', addC)
    addServerC.description = 'Builds a server from parameters, then adds it to the database.'
    addServerC.function = 'addServerF'
    global addColorC
    addColorC = command('color', addC)
    addColorC.description = 'Adds a color with the given name and code to the database.'
    addColorC.function = 'addColorF'
    global removeC
    removeC = command('remove', mSelf)
    removeC.description = 'Used to remove existing objects from the database.'
    removeC.function = 'removeF'
    global removeUserC
    removeUserC = command('user', removeC)
    removeUserC.description = 'Removes a user from the database.'
    removeUserC.function = 'removeUserF'
    global removeServerC
    removeServerC = command('server', removeC)
    removeServerC.description = 'Removes a server from the database.'
    removeServerC.function = 'removeServerF'
    global removeColorC
    removeColorC = command('color', removeC)
    removeColorC.description = 'Removes a color from the database.'
    removeColorC.function = 'removeColorF'
    global showC
    showC = command('show', mSelf)
    showC.description = 'Displays detailed information about database objects.'
    showC.function = 'showF'
    global showUserC
    showUserC = command('user', showC)
    showUserC.description = 'Displays detailed information about the user with the given ID. Usage: \'show user ID#\''
    showUserC.function = 'showUserF'
    global showServerC
    showServerC = command('server', showC)
    showServerC.description = 'Displays detailed information about the server with the given ID. Usage: \'show server ID#\''
    showServerC.function = 'showServerF'
    global showColorC
    showColorC = command('server', showC)
    showColorC.description = 'Displays detailed information about the color with the given name or code. Usage: \'show color NAME/#CODE\''
    showColorC.function = 'showColorF'
    global listC
    listC = command('list', mSelf)
    listC.description = 'Lists all objects of the given type currently in the database.'
    listC.function = 'listF'
    global listUserC
    listUserC = command('user', listC)
    listUserC.description = 'Lists all users in the database.'
    listUserC.function = 'listUserF'
    global listUserAliasC
    listUserAliasC = command('alias', listUserC)
    listUserAliasC.description = 'Lists all of a user\'s aliases across all servers. Specify a user ID.'
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
    listTimezoneC.description = 'Lists all available time zones.'
    listTimezoneC.function = 'listTimezoneF'
    global timeC
    timeC = command('time', mSelf)
    timeC.description = 'Displays the current time.'
    timeC.function = 'timeF'
    global timeForC
    timeForC = command('for', timeC)
    timeForC.description = 'Displays the time in a specific user\'s time zone.'
    timeForC.function = 'timeForF'
    global timeZonesC
    timeZonesC = command('zones', timeC)
    timeZonesC.description = 'Lists all available time zones.'
    timeZonesC.function = 'listTimezoneF'
    global findC
    findC = command('find', mSelf)
    findC.description = 'Searches for objects meeting the given criteria.'
    findC.function = 'findF'
    global findUserC
    findUserC = command('user', findC)
    findUserC.description = 'Searches for users meeting the given criteria.'
    findUserC.function = 'findUserF'
    global findUserNameC
    findUserNameC = command('name', findUserC)
    findUserNameC.description = 'Searches for users with names and/or nicknames matching the given query.'
    findUserNameC.function = 'findUserNameF'
    global findUserCountryC
    findUserCountryC = command('country', findUserC)
    findUserCountryC.description = 'Searches for users with countries matching the given query.'
    findUserCountryC.function = 'findUserCountryF'
    global findUserTimezoneC
    findUserTimezoneC = command('timezone', findUserC)
    findUserTimezoneC.description = 'Searches for users with timezones matching the given query.'
    findUserTimezoneC.function = 'findUserTimezoneF'
    global findUserBirthdayC
    findUserBirthdayC = command('birthday', findUserC)
    findUserBirthdayC.description = 'Searches for users with birthdays matching the given query.'
    findUserBirthdayC.function = 'findUserBirthdayF'
    global findUserColorC
    findUserColorC = command('color', findUserC)
    findUserColorC.description = 'Searches for users with colors matching the given query.'
    findUserColorC.function = 'findUserColorF'
    global findServerC
    findServerC = command('server', findC)
    findServerC.description = 'Searches for servers meeting the given criteria.'
    findServerC.function = 'findServerF'
    global findServerNameC
    findServerNameC = command('name', findServerC)
    findServerNameC.description = 'Searches for servers with names matching the given query.'
    findServerNameC.function = 'findServerNameF'
    global findServerTimezoneC
    findServerTimezoneC = command('timezone', findServerC)
    findServerTimezoneC.description = 'Searches for servers with timezones matching the given query.'
    findServerTimezoneC.function = 'findServerTimezoneF'
    global findTimezoneC
    findTimezoneC = command('timezone' findC)
    findTimezoneC.description = 'Searches for timezones with names matching the given query.'
    findTimezoneC.function = 'findTimezoneF'
    global findColorC
    findColorC = command('color', findC)
    findColorC.description = 'Searches for colors with names matching the given query.'
    findColorC.function = 'findColorF'

def databaseF():
    print(databaseC.help() + '\n')
    listF()
    print()
    checkF()

def databaseSetupF():
    return None

def databaseDeleteF():
    return None

def databaseBackupF():
    DB = config.database
    if DB.exists():
        oFile = backup()
        print('Database backed up to \'{backupname}\'.'.format(backupname=oFile.name))

    else:
        print('Database not found!')

def addF():
    return None

def addUserF(*userinput):
    userdata = []

    for p in range(0, len(userinput)):
        userdata.append(userinput[p].split('='))

    userDict = {}

    for q in userdata:
        userDict.update({q[0] : q[1]})

    if 'id' in userDict.keys():
        newUser = user(userDict['id'])

        if 'name' in userDict.keys():
            newUser.name = userDict['name']

        if 'tz' in userDict.keys():
            newUser.tz = userDict['tz']

        if 'botrank' in userDict.keys():
            newUser.botrank = userDict['botrank']

        if 'bday' in userDict.keys():
            newUser.bday = userDict['bday']

        if 'country' in userDict.keys():
            newUser.country = userDict['country']

        if 'points' in userDict.keys():
            newUser.points = userDict['points']

        if 'serverid' in userDict.keys():
            newUser.serverid = userDict['serverid']

            if 'nick' in userDict.keys():
                newUser.nick = userDict['nick']

            if 'color' in userDict.keys():
                newUser.color = userDict['color']

            if 'localrank' in userDict.keys():
                newUser.localrank = userDict['localrank']

        addUser(newUser)


def addServerF():
    return None

def addColorF():
    return None

def removeF():
    return None

def removeUserF():
    return None

def removeServerF():
    return None

def removeColorF():
    return None

def showF():
    return None

def showUserF():
    return None

def showServerF():
    return None

def showColorF():
    return None

def listF():
    return None

def listUserF():
    return None

def listUserAliasF():
    return None

def listServerF():
    return None

def listColorF():
    return None

def listTimezoneF():
    for value in pytz.all_timezones:
        print(value)

def timeF():
    return None

def timeForF(userinput):
# Check if user inputted a valid ID
    thisUser = getUser(userinput)
    if not thisUser:
# If not, check if it is a name
        searchResults = searchUserbyName(userinput)
        
        if len(searchResults) > 0:
            if len(searchResults) == 1:
                thisUser = searchResults[0]
            else:
                print('Multiple matching users found. Be more specific.')
        else:
            print('No matching users found.')
    
    if thisUser:
        print('The current time for {uname} in the {tzone} timezone is {now}.'.format(thisUser.goesby(), thisUser.tz, getTime(thisUser)))

def findF():
    return None

def findUserF():
    return None

def findUserNameF():
    return None

def findUserCountryF():
    return None

def findUserTimezoneF():
    return None

def findUserBirthdayF():
    return None

def findUserColorF():
    return None

def findServerF():
    return None

def findServerNameF():
    return None

def findServerTimezoneF():
    return None

def findTimezoneF():
    return None

def findColorF():
    return None

def initialize():
    if not config.dataPath.exists():
        pathlib.path.mkdir(config.dataPath)

    DB = config.database

    try:
        doInit = False
        if DB.exists():
            response = input('Database already exists. Re-initialize? This will empty the database. <y/N> ')
            if response.lower() == 'y':
                thisDB.unlink()
                doInit = True
            else:
                print('Canceled.')
        else:
            doInit = True
        
        if doInit:
            conn = sqlite3.connect(DB)
            cursor = conn.cursor()
            cursor.execute("
                    CREATE TABLE info(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    key TEXT,
                    value TEXT
                    )")
            cursor.execute("INSERT INTO info(key, value) VALUES (?, ?)",
                    ('dbversion', config.settings['dbversion']))
            print('Configuring for multiple users...')
            cursor.execute("
                    CREATE TABLE users(
                    id INTEGER PRIMARY KEY,
                    name TEXT,
                    botrank INTEGER DEFAULT '0',
                    country TEXT,
                    tz TEXT DEFAULT 'US/Eastern',
                    bday TEXT,
                    points INTEGER DEFAULT '0'
                    )")
            print('Configuring for multiple servers...')
            cursor.execute("
                    CREATE TABLE servers(
                    id TEXT NOT NULL PRIMARY KEY,
                    name TEXT,
                    trigger TEXT
                    )")
            cursor.execute("
                    CREATE TABLE serverusers(
                    userid TEXT NOT NULL,
                    serverid TEXT NOT NULL,
                    PRIMARY KEY(userid, serverid),
                    FOREIGN KEY(userid) REFERENCES users(id)
                        ON DELETE CASCADE ON UPDATE NO ACTION,
                    FOREIGN KEY(serverid) REFERENCES servers(id)
                        ON DELETE CASCADE ON UPDATE NO ACTION,
                    color TEXT,
                    nick TEXT,
                    localrank TEXT
                    )")
            conn.commit()
            conn.close()

            for module in config.imports:
                if hasattr(sys.modules[module], 'dbinit'):
                    sys.modules[module].dbinit(DB)

            print('Database initialized.')

    except:
        print(sys.exc_info()[0])
        #print('Error.')

def backup():
    timestamp = (datetime.now()).strftime("%Y%m%d%H%M%S%f")
    
    if not config.backupPath.exists():
        pathlib.path.mkdir(config.backupPath)

    backupFile = config.backupPath / ('{dbname}_backup_{code}.db'.format(dbname=config.database, code=timestamp))
    
    shutil.copy2(config.database, backupFile)

    return backupFile

def cleanup():
    databaseBackupF()

if __name__ == "__main__":
    print("No main.")
else:
    init()
