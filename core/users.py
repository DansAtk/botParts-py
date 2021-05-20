import sys
import os
import pathlib
import shutil

import sqlite3
import pytz
from datetime import *

import config
from core import commands
from core import utils

mSelf = sys.modules[__name__]
includes = {}
config.register(mSelf)
DB = config.database

class user:
    def __init__(self, ID, NAME=None, TZ=None, BOTRANK=None, BDAY=None, COUNTRY=None, POINTS=None):
        self.id = ID 
        self.name = NAME
        self.tz = TZ
        self.botrank = BOTRANK
        self.bday = BDAY
        self.country = COUNTRY
        self.points = POINTS

    def now(self):
        if self.tz:
            return datetime.now(pytz.timezone(self.tz))
        
        else:
            return getTime()
            
def getUser(userid):
    if utils.checkDB():
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
    if utils.checkDB():
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

def removeUser(profile):
    if utils.checkDB():
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
        
        if utils.checkDB():
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

def searchUserbyName(searchstring):
    if utils.checkDB():
        conn = sqlite3.connect(DB)
        cursor = conn.cursor()

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
                thisUser = getUser(result[0])
                foundUsers.append(thisUser)

            return foundUsers

        else:
            return None

def searchUserbyCountry(searchstring):
    if utils.checkDB():
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
                thisUser = getUser(result[0])
                foundUsers.append(thisUser)

            return foundUsers

        else:
            return None

def searchUserbyTimezone(searchstring):
    if utils.checkDB():
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
                thisUser = getUser(result[0])
                foundUsers.append(thisUser)

            return foundUsers

        else:
            return None

def searchUserbyBirthday(searchstring):
    if utils.checkDB():
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
                thisUser = getUser(result[0])
                foundUsers.append(thisUser)

            return foundUsers

        else:
            return None

def dbinit():
    try:
        conn = sqlite3.connect(DB)
        cursor = conn.cursor()
        config.debugQ.put('Configuring for users...')
        cursor.execute(
                "CREATE TABLE users("
                "id INTEGER PRIMARY KEY, name TEXT, botrank INTEGER DEFAULT '0', country TEXT, "
                "tz TEXT DEFAULT 'US/Eastern', bday TEXT, points INTEGER DEFAULT '0')"
                )
        conn.commit()
        conn.close()
        config.debugQ.put('Success!')

    except:
        config.debugQ.put('Unable to configure users table!')

def registerCommands():
    global addUserC
    addUserC = commands.command('user', utils.addC)
    addUserC.description = 'Builds a user from parameters, then adds it to the database.'
    addUserC.instruction = 'Specify user attributes using \'Attribute=Value\' with each separated by a space. \'id\' is required.'
    addUserC.function = 'addUserF'
    addUserC.parent_module = mSelf
    global removeUserC
    removeUserC = commands.command('user', utils.removeC)
    removeUserC.description = 'Removes a user from the database.'
    removeUserC.instruction = 'Specify a user.'
    removeUserC.function = 'removeUserF'
    removeUserC.parent_module = mSelf
    global editUserC
    editUserC = commands.command('user', utils.editC)
    editUserC.description = 'Updates an existing user with new attributes.'
    editUserC.instruction = 'First specify a user. Then, specify new attributes using \'Attribute=Value\' with each separated by a space.'
    editUserC.function = 'editUserF'
    editUserC.parent_module = mSelf
    global showUserC
    showUserC = commands.command('user', utils.showC)
    showUserC.description = 'Displays detailed information about a single user.'
    showUserC.instruction = 'Specify a user.'
    showUserC.function = 'showUserF'
    showUserC.parent_module = mSelf
    global listUserC
    listUserC = commands.command('user', utils.listC)
    listUserC.description = 'Lists all users in the database.'
    listUserC.function = 'listUserF'
    listUserC.parent_module = mSelf
    global timeForC
    timeForC = commands.command('for', utils.timeC)
    timeForC.description = 'Displays the time in a specific user\'s timezone.'
    timeForC.instruction = 'Specify a user.'
    timeForC.function = 'timeForF'
    timeForC.parent_module = mSelf
    global findUserC
    findUserC = commands.command('user', utils.findC)
    findUserC.description = 'Searches for users meeting the given criteria.'
    findUserC.instruction = 'Specify a parameter.'
    findUserC.parent_module = mSelf
    global findUserNameC
    findUserNameC = commands.command('name', findUserC)
    findUserNameC.description = 'Searches for users with names and/or nicknames matching the given query.'
    findUserNameC.instruction = 'Specify a name or nickname.'
    findUserNameC.function = 'findUserNameF'
    global findUserCountryC
    findUserCountryC = commands.command('country', findUserC)
    findUserCountryC.description = 'Searches for users with countries matching the given query.'
    findUserCountryC.instruction = 'Specify a country.'
    findUserCountryC.function = 'findUserCountryF'
    global findUserTimezoneC
    findUserTimezoneC = commands.command('timezone', findUserC)
    findUserTimezoneC.description = 'Searches for users with timezones matching the given query.'
    findUserTimezoneC.instruction = 'Specify a timezone.'
    findUserTimezoneC.function = 'findUserTimezoneF'
    global findUserBirthdayC
    findUserBirthdayC = commands.command('birthday', findUserC)
    findUserBirthdayC.description = 'Searches for users with birthdays matching the given query.'
    findUserBirthdayC.instruction = 'Specify a birthday in format DD-MM.'
    findUserBirthdayC.function = 'findUserBirthdayF'

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
                    thisTZ = utils.tryGetOneTimezone(userDict['tz'][1:-1])
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

    if goodProfile:
        addUser(newUser)
        config.outQ.put(f'Added user {newUser.name}({newUser.id}).')

    else:
        config.outQ.put('Invalid attribute(s).')

def removeUserF(inputData, content):
    thisThread = commands.request_queue(inputData, filter_place=True, filter_user=True)
    thisQ = thisThread['queue']
    userString = ' '.join(content)
    thisUser = tryGetOneUser(userString)

    if thisUser:
        config.outQ.put(f'{thisThread["tag"]}> Remove user {thisUser.name}({thisUser.id})? ({thisThread["tag"]}>y/N)')
        rawResponse = thisQ.get()
        response = ' '.join(rawResponse.content)

        if response.lower() == 'y':
            removeUser(thisUser)
            config.outQ.put('User removed.')

        else:
            config.outQ.put('Cancelled.')

    else:
        config.outQ.put('User not found.')
        
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
                thisTZ = utils.tryGetOneTimezone(userDict['tz'][1:-1])
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
            config.outQ.put(f'Updated user {thisUser.name}({thisUser.id}).')

        else:
            config.outQ.put('Invalid attribute(s).')

    else:
        config.outQ.put('User not found.')

def showUserF(inputData, content):
    if len(content) > 1:
        userString = ' '.join(content)
    else:
        userString = content[0]
    thisUser = tryGetOneUser(userString)

    if thisUser:
        output_text = ''
        output_text += (f'Name = {thisUser.name}\n')
        output_text += (f'ID = {thisUser.id}\n')
        output_text += (f'Country = {thisUser.country}\n')
        output_text += (f'Timezone = {thisUser.tz}\n')
        output_text += (f'Birthday = {thisUser.bday}\n')
        output_text += (f'Bot Rank = {thisUser.botrank}\n')
        config.outQ.put(output_text)

    else:
        config.outQ.put('User not found.')

def listUserF(inputData):
    if utils.checkDB():
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
        
if __name__ == "__main__":
    print("No main.")
else:
    registerCommands()
