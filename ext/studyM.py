import sys
import sqlite3
from datetime import *

from core import config
from core.commandM import command, imports
from core import DBM

mSelf = sys.modules[__name__]
includes = {}

class studyUser(DBM.user):
    def __init__(self, ID, CSTREAK=None, LSTREAK=None, DAYS=None):
        self.cstreak = CSTREAK
        self.lstreak = LSTREAK
        self.days = DAYS

        tempUser = DBM.tryGetOneUser(ID)
        if tempUser:
            super().__init__(tempUser.id, tempUser.name, tempUser.tz, tempUser.botrank, tempUser.bday, tempUser.country, tempUser.points)
        else:
            super().__init__(ID)

def getStudyUser(userid):
    DB = config.database

    thisUser = DBM.getUser(userid)

    if thisUser:
        if DBM.checkDB():
            conn = sqlite3.connect(DB)
            cursor = conn.cursor()
            cursor.execute(
                    "SELECT cstreak, lstreak, days "
                    "FROM studyusers "
                    "WHERE user = ?",
                    (userid,)
                    )
            result = cursor.fetchone()
            conn.close()

            if result:
                thisStudyUser = studyUser(thisUser.id)
                thisStudyUser.cstreak = result[0]
                thisStudyUser.lstreak = result[1]
                thisStudyUser.days = result[2]

                return thisStudyUser

            else:
                return None

    else:
        return None

def tryGetOneStudyUser(studyuserstring):
    thisStudyUser = None

    try:
        thisStudyUser = getStudyUser(int(studyuserstring))

    except ValueError:
        thisUser = DBM.tryGetOneUser(studyuserstring)

        if thisUser:
            thisStudyUser = getStudyUser(thisUser.id)

    return thisStudyUser

def addStudyUser(profile):
    DB = config.database

    if DBM.checkDB():
        conn = sqlite3.connect(DB)
        cursor = conn.cursor()
        cursor.execute(
                "INSERT INTO studyusers"
                "(user, cstreak, lstreak, days) "
                "VALUES (?, ?, ?, ?)",
                (profile.id, profile.cstreak, profile.lstreak, profile.days)
                )
        conn.commit()
        conn.close()

def removeStudyUser(profile):
    DB = config.database

    if DBM.checkDB():
        conn = sqlite3.connect(DB)
        conn.execute("PRAGMA foreign_keys = 1")
        cursor = conn.cursor()
        cursor.execute(
                "DELETE FROM studyusers "
                "WHERE user = ?",
                (profile.id,)
                )
        conn.commit()
        conn.close()

def updateStudyUser(profile):
    thisStudyUser = getStudyUser(profile.id)

    if thisStudyUser:
        if profile.cstreak:
            thisStudyUser.cstreak = profile.cstreak
        if profile.lstreak:
            thisStudyUser.lstreak = profile.lstreak
        if profile.days:
            thisStudyUser.days = profile.days

        DB = config.database

        if DBM.checkDB():
            conn = sqlite3.connect(DB)
            cursor = conn.cursor()
            cursor.execute(
                    "UPDATE studyusers SET "
                    "cstreak = ?, lstreak = ?, days = ? "
                    "WHERE user = ?",
                    (thisStudyUser.cstreak, thisStudyUser.lstreak, thisStudyUser.days, thisStudyUser.id)
                    )
            conn.commit()
            conn.close()

def searchStudyUserbyName(searchstring):
    search = DBM.searchUserbyName(searchstring)

    if search:
        foundStudyUsers = []

        for result in search:
            thisStudyUser = getStudyUser(result.id)

            if thisStudyUser:
                foundStudyUsers.append(thisStudyUser)

        if len(foundStudyUsers) > 0:
            return foundStudyUsers

        else:
            return None

    else:
        return None

def searchStudyUserbyServer(serverprofile):
    search = DBM.searchUserbyServer(serverprofile)

    if search:
        foundStudyUsers = []
        
        for result in search:
            thisStudyUser = getStudyUser(result.id)

            if thisStudyUser:
                foundStudyUsers.append(thisStudyUser)

        if len(foundStudyUsers) > 0:
            return foundStudyUsers

        else:
            return None

    else:
        return None
        
class studyLog:
    def __init__(self, ID=None, USER=None, DATE=None, NOTE=None):
        self.id = ID
        self.user = USER
        self.date = DATE
        self.note = NOTE

def getStudyLog(logid):
    DB = config.database

    if DBM.checkDB():
        conn = sqlite3.connect(DB)
        cursor = conn.cursor()
        cursor.execute(
                "SELECT user, date, note "
                "FROM studysessions "
                "WHERE id = ?",
                (logid,)
                )
        result = cursor.fetchone()
        conn.close()

        if result:
            thisStudyLog = studyLog(logid)
            thisStudyLog.user = result[0]
            thisStudyLog.date = result[1]
            thisStudyLog.note = result[2]

            return thisStudyLog

        else:
            return None

def addStudyLog(profile):
    DB = config.database

    if DBM.checkDB():
        conn = sqlite3.connect(DB)
        cursor = conn.cursor()
        cursor.execute(
                "INSERT INTO studysessions"
                "(user, date, note) "
                "VALUES (?, ?, ?)",
                (profile.user, profile.date, profile.note)
                )
        conn.commit()
        conn.close()

def removeStudyLog(profile):
    DB = config.database

    if DBM.checkDB():
        conn = sqlite3.connect(DB)
        conn.execute("PRAGMA foreign_keys = 1")
        cursor = conn.cursor()
        cursor.execute(
                "DELETE FROM studysessions "
                "WHERE id = ?",
                (profile.id,)
                )
        conn.commit()
        conn.close()

def updateStudyLog(profile):
    thisStudyLog = getStudyLog(profile.id)

    if thisStudyLog:
        if profile.user:
            thisStudyLog.user = profile.user
        if profile.date:
            thisStudyLog.date = profile.date
        if profile.note:
            thisStudyLog.note = profile.note

        DB = config.database

        if DBM.checkDB():
            conn = sqlite3.connect(DB)
            cursor = conn.cursor()
            cursor.execute(
                    "UPDATE studysessions SET "
                    "user = ?, date = ?, note = ? "
                    "WHERE id = ?",
                    (thisStudyLog.user, thisStudyLog.date, thisStudyLog.note, thisStudyLog.id)
                    )
            conn.commit()
            conn.close()

def searchStudyLogbyUser(profile):
    DB = config.database
    if DBM.checkDB():
        conn = sqlite3.connect(DB)
        cursor = conn.cursor()
        cursor.execute(
                "SELECT id "
                "FROM studysessions "
                "WHERE user = ?",
                (profile.id,)
                )
        search = cursor.fetchall()
        conn.close()

        if len(search) > 0:
            foundStudyLogs = []
            for result in search:
                thisStudyLog = getStudyLog(result[0])
                foundStudyLogs.append(thisStudyLog)

            return foundStudyLogs

        else:
            return None

def registerCommands():
    global studyC
    studyC = command('study', mSelf)
    studyC.description = 'Commands for tracking and monitoring study habits.'
    studyC.instruction = 'Specify a parameter.'
    global logC
    logC = command('log', studyC)
    logC.description = 'For managing tracked study sessions.'
    logC.instruction = 'Specify a parameter.'
    global markC 
    markC= command('mark', logC)
    markC.description = 'Marks a user as having studied for the current day.'
    markC.instruction = 'Provide a user followed (optionally) by a note.'
    markC.function = 'markF'
    global unmarkC
    unmarkC = command('unmark', logC)
    unmarkC.description = 'Unmarks a user\'s previously logged day of study.'
    unmarkC.instruction = 'Specify a user and (optionally) the date of study to be removed, in format DD-MM-YYYY. Removes from the current day by default.'
    unmarkC.function = 'unmarkF'
    global checkC
    checkC = command('check', logC)
    checkC.description = 'Checks for a user\'s logged study.'
    checkC.instruction = 'Specify a user and (optionally) the date of study, in format DD-MM-YYYY. Checks the current day by default.'
    checkC.function = 'checkF'
    imports.update({__name__ : includes})

def markF(inputData, content):
    userString = content[0]
    logNote = None

    if len(content) > 1:
        if content[1].startswith('"') and content[1].endswith('"'):
            logNote = content[1][1:-1]

    thisUser = DBM.tryGetOneUser(userString)

    if thisUser:
        logDate = thisUser.now().strftime("%d-%m-%Y")

        thisLog = studyLog()
        thisLog.user = thisUser.id
        thisLog.date = logDate
        thisLog.note = logNote

        addStudyLog(thisLog)

        config.outQ.put(f'Study logged for {thisUser.name} on {logDate}.')

    else:
        config.outQ.put('User not found.')
        
def unmarkF(inputData, content):
    userString = content[0]
    thisUser = DBM.tryGetOneUser(userString)

    if thisUser:
        search = searchStudyLogbyUser(thisUser)

        if search:
            if len(content) > 1:
                dateString = ' '.join(content[1:])

            else:
                dateString = thisUser.now().strftime("%d-%m-%Y")

            foundLog = None

            for result in search:
                if result.date == dateString:
                    foundLog = result

            if foundLog:
                removeStudyLog(foundLog)
                config.outQ.put(f'{thisUser.name} unmarked for {foundLog.date}.')

            else:
                config.outQ.put(f'{thisUser.name} did not study on {dateString}.')

        else:
            config.outQ.put('No logs found.')

    else:
        config.outQ.put('User not found.')

def checkF(inputData, content):
    userString = content[0]

    thisUser = DBM.tryGetOneUser(userString)

    if thisUser:
        search = searchStudyLogbyUser(thisUser)

        if search:
            if len(content) > 1:
                dateString = ' '.join(content[1:])

            else:
                dateString = thisUser.now().strftime("%d-%m-%Y")

            foundLog = None

            for result in search:
                if result.date == dateString:
                    foundLog = result

            if foundLog:
                if foundLog.note:
                    config.outQ.put(f'{thisUser.name} studied on {foundLog.date}.\n"{foundLog.note}"')
                else:
                    config.outQ.put(f'{thisUser.name} studied on {foundLog.date}.')

            else:
                config.outQ.put(f'{thisUser.name} did not study on {dateString}.')

        else:
            config.outQ.put('No logs found.')

    else:
        config.outQ.put('User not found.')

def dbinit(DB):
    config.debugQ.put('Configuring for study logging...')
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    cursor.execute(
            "CREATE TABLE studysessions("
            "id INTEGER PRIMARY KEY AUTOINCREMENT, user INTEGER, date TEXT, note TEXT, "
            "FOREIGN KEY(user) REFERENCES users(id) ON DELETE CASCADE ON UPDATE NO ACTION)"
            )
    cursor.execute(
            "CREATE TABLE studyusers("
            "user INTEGER PRIMARY KEY, cstreak INTEGER DEFAULT 0, lstreak INTEGER DEFAULT 0, days INTEGER DEFAULT 0, "
            "FOREIGN KEY(user) REFERENCES users(id) ON DELETE CASCADE ON UPDATE NO ACTION)"
            )
    conn.commit()
    conn.close()

if __name__ == "__main__":
    print('A collection of study tracking commands for a botParts bot. No main.')
else:
    registerCommands()
