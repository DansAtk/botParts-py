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


>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

def init():
    global databaseC
    databaseC = command('database', mSelf)
    databaseC.description = 'Commands for managing the bot\'s database. Alone, displays information about the database\'s current state.'
    databaseC.function = 'databaseF'
    global setupC
    setupC = command('setup', databaseC)
    setupC.description = 'Initializes the database. If the database already exists, it can be reinitialized or reconfigured, based on imported modules.'
    setupC.function = 'setupF'
    global deleteC
    deleteC = command('delete', databaseC)
    deleteC.description = 'Deletes the database.' 
    deleteC.function = 'deleteF'
    global backupC
    backupC = command('backup', databaseC)
    backupC.description = 'Creates a backup of the database.'
    backupC.function = 'backupF'
    global userC
    userC = command('user', mSelf)
    userC.description = 'Used to create, remove and manipulate user profiles.'
    userC.function = 'userF'
    global addC
    addC = command('add', userC)
    addC.description = 'Builds a user from parameters, then adds it to the database.'
    addC.function = 'addF'
    global timeC
    timeC = command('time', mSelf)
    timeC.description = 'Displays the current time.'
    timeC.function = 'timeF'
    global forC
    forC = command('for', timeC)
    forC.description = 'Displays the time in a specific user\'s time zone.'
    forC.function = 'timeforF'
    global zoneC
    zonesC = command('zones', timeC)
    zonesC.description = 'Lists all available time zones.'
    zonesC.function = 'zonesF'
    global listC
    listC = command('list', zoneC)
    listC.description = 'Lists all available time zones.'
    listC.function = 'timezonelistF'

def databaseF():
    print(databaseC.help() + '\n')
    listF()
    print()
    checkF()

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

def backupF():
    DB = config.database
    if DB.exists():
        oFile = backup()
        print('Database backed up to \'{backupname}\'.'.format(backupname=oFile.name))

    else:
        print('Database not found!')

def cleanup():
    backupF()

if __name__ == "__main__":
    print("No main.")
else:
    init()


>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def timeforF(userinput=''):
    if len(userinput) > 1:
        timeUser = getUser(userinput[0], userinput[1])
        print(timeUser.now())

    else:
        print('Please specify at least a user ID and a database name.')

def timezonelistF():
    for value in pytz.all_timezones:
        print(value)

#def userCF(message):
#    if len(message) > 0:
#        print(user.paramError(message))
#    else:
#        print(user.help())


def buildF(*userinput):
    newUser = user()
    userdata = []

    for p in range(0, len(userinput)):
        print(p)
        userdata.append(userinput[p].split('='))

    userDict = {}

    for q in userdata:
        userDict.update({q[0] : q[1]})

    if 'id' in userDict.keys():
        newUser.id = userDict['id']

    if 'name' in userDict.keys():
        newUser.name = userDict['name']

    if 'nick' in userDict.keys():
        newUser.nick = userDict['nick']

    if 'tz' in userDict.keys():
        newUser.tz = userDict['tz']

    if 'rank' in userDict.keys():
        newUser.rank = userDict['rank']

    if 'color' in userDict.keys():
        newUser.color = userDict['color']

    if 'bday' in userDict.keys():
        newUser.bday = userDict['bday']

    if 'country' in userDict.keys():
        newUser.country = userDict['country']

    if 'points' in userDict.keys():
        newUser.points = userDict['points']

    if 'database' in userDict.keys():
        addUser(newUser, userDict['database'])

    return newUser

def dbinit(DB):

if __name__ == "__main__":
    print("No main.")
else:
    init()
