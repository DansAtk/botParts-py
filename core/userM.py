import sys
import sqlite3
import pytz
import datetime
import calendar

from core import config
from core.commandM import command
from core import databaseM

mSelf = sys.modules[__name__]
includes = {}
config.imports.append(__name__)

class user:
    def __init__(self, ID='0', NAME='', NICK='', TZ='US/Eastern', RANK=0, COLOR='', BDAY='', COUNTRY='', POINTS=0):
        self.id = ID 
        self.name = NAME
        self.tz = TZ
        self.time = ''
        self.rank = RANK
        self.nick = NICK
        self.color = COLOR
        self.bday = BDAY
        self.country = COUNTRY
        self.points = POINTS

    def now(self):
        self.time = datetime.datetime.now(pytz.timezone(self.tz))
        return self.time

    def goesby(self):
        useName = ''
        if len(self.nick) > 0:
            useName = self.nick
        else:
            useName = self.name
        return useName

    def fill(self, DBname):
        DB = databaseM.getDB(DBname)
        if DB:
            conn = sqlite3.connect(DB)
            cursor = conn.cursor()
            cursor.execute("SELECT name, nick, tz, rank, color, bday, country, points FROM users WHERE id = ?", (self.id,))
            result = cursor.fetchone()
            conn.close()
            if not result:
                print('user not found')
            if result:
                self.name = result[0]
                self.nick = result[1]
                self.tz = result[2]
                self.rank = result[3]
                self.color = result[4]
                self.bday = result[5]
                self.country = result[6]
                self.points = result[7]

def getUser(ID, DBname):
    thisUser = user(ID)
    thisUser.fill(DBname)
    return thisUser

def init():
    global userC
    userC = command('user', mSelf)
    userC.description = 'Used to create, remove and manipulate user profiles.'
    userC.function = 'userF'
    global buildC
    buildC = command('build', userC)
    buildC.description = 'Builds a user object from parameters, then adds it to the database.'
    buildC.function = 'buildF'
    global timeC
    timeC = command('time', mSelf)
    timeC.description = 'Displays the current time.'
    timeC.function = 'timeF'
    global forC
    forC = command('for', timeC)
    forC.description = 'Displays the time in a specific user\'s time zone.'
    forC.function = 'timeforF'
    global zoneC
    zoneC = command('zone', timeC)
    zoneC.description = 'For configuring time zones.'
    zoneC.function = 'timezoneF'
    global listC
    listC = command('list', zoneC)
    listC.description = 'Lists all available time zones.'
    listC.function = 'timezonelistF'

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

def addUser(profile, DBname):
    DB = databaseM.getF(DBname)
    if DB:
        conn = sqlite3.connect(DB)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users(id, name, nick, rank, country, tz, color, bday, points) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (profile.id, profile.name, profile.nick, profile.rank, profile.country, profile.tz, profile.color, profile.bday, profile.points))
        conn.commit()
        conn.close()

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
    print('Configuring for multiple users...')
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE users(id INTEGER PRIMARY KEY, name TEXT, nick TEXT, rank INTEGER DEFAULT '0', country TEXT, tz TEXT DEFAULT 'US/Eastern', color INTEGER DEFAULT '0', bday TEXT, points INTEGER DEFAULT '0', isbanned INTEGER DEFAULT '0', active INTEGER)")
    print('\'users\' table created.')
    conn.commit()
    conn.close()

if __name__ == "__main__":
    print("No main.")
else:
    init()
