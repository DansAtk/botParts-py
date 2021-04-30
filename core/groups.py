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
groupTypes = ['global', 'local']

class group:
    def __init__(self, ID=None, NAME=None, TYPE=None, PLACE=None):
        self.id = ID 
        self.name = NAME
        self.type = TYPE
        self.place = PLACE
        self.members = {'users' : [], 'groups' : []}

    def getMembers(self):
        if utils.checkDB():
            conn = sqlite3.connect(DB)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT memberuserid, membergroupid "
                "FROM memberships "
                "WHERE groupid = ?",
                (self.id,)
                )
            results = cursor.fetchall()
            conn.close()

            self.memberusers = []
            self.membergroups = []

            if len(results) > 0:
                for each in results:
                    if each[1] == None:
                        thisUser = users.getUser(each[0])
                        self.members['users'].append(thisUser)
                    else:
                        thisGroup = getGroup(each[1])
                        self.members['groups'].append(thisGroup)

            return self.members

    def addMember(self, memberid):
        if utils.checkDB():
            if users.getUser(memberid):
                conn = sqlite3.connect(DB)
                cursor = conn.cursor()
                cursor.execute(
                        "INSERT INTO memberships "
                        "(groupid, memberuserid) "
                        "VALUES (?, ?)",
                        (self.id, memberid)
                        )
                conn.commit()
                conn.close()
            elif getGroup(memberid):
                conn = sqlite3.connect(DB)
                cursor = conn.cursor()
                cursor.execute(
                        "INSERT INTO memberships "
                        "(groupid, membergroupid) "
                        "VALUES (?, ?)",
                        (self.id, memberid)
                        )
                conn.commit()
                conn.close()

    def removeMember(self, memberid):
        if utils.checkDB():
            conn = sqlite3.connect(DB)
            conn.execute("PRAGMA foreign_keys = 1")
            cursor = conn.cursor()
            cursor.execute(
                    "DELETE FROM memberships "
                    "WHERE groupid = ? AND (memberuserid = ? OR membergroupid = ?)",
                    (self.id, memberid, memberid)
                    )
            conn.commit()
            conn.close()
    
def getGroup(groupid):
    if utils.checkDB():
        conn = sqlite3.connect(DB)
        cursor = conn.cursor()
        cursor.execute(
                "SELECT id, name, type, placeid "
                "FROM groups "
                "WHERE id = ?",
                (groupid,)
                )
        result = cursor.fetchone()
        conn.close()

        if result:
            thisGroup = group(result[0])
            thisGroup.name = result[1]
            thisGroup.type = result[2]
            thisGroup.place = result[3]

            return thisGroup
            
        else:
            return None

def tryGetOneGroup(groupString):
    thisGroup = None

    try:
        thisGroup = getGroup(int(groupString))

    except ValueError:
        searchResults = searchGroupbyName(groupString)
        
        if searchResults:
            if len(searchResults) == 1:
                thisGroup = searchResults[0]
    
    return thisGroup

def addGroup(profile):
    if utils.checkDB():
        conn = sqlite3.connect(DB)
        cursor = conn.cursor()
        cursor.execute(
                "INSERT INTO groups"
                "(name, type, placeid) "
                "VALUES (?, ?, ?)",
                (profile.name, profile.type, profile.place)
                )
        conn.commit()
        conn.close()

def removeGroup(groupid):
    if utils.checkDB():
        conn = sqlite3.connect(DB)
        conn.execute("PRAGMA foreign_keys = 1")
        cursor = conn.cursor()
        cursor.execute(
                "DELETE FROM groups "
                "WHERE id = ?",
                (groupid,)
                )
        conn.commit()
        conn.close()

def updateGroup(profile):
    thisGroup = getGroup(profile.id)

    if thisGroup:
        if profile.name:
            thisGroup.name = profile.name
        if profile.type:
            thisGroup.type = profile.type
        if profile.place:
            thisGroup.place = profile.place
        
        if utils.checkDB():
            conn = sqlite3.connect(DB)
            cursor = conn.cursor()
            cursor.execute(
                    "UPDATE groups SET "
                    "name = ?, type = ?, placeid = ? "
                    "WHERE id = ?",
                    (thisGroup.name, thisGroup.type, thisGroup.place, profile.id)
                    )
            conn.commit()
            conn.close()

def searchGroupbyName(searchString):
    if utils.checkDB():
        conn = sqlite3.connect(DB)
        cursor = conn.cursor()
        cursor.execute(
                "SELECT id "
                "FROM groups "
                "WHERE name LIKE ?",
                ('%{}%'.format(searchString),)
                )
        search = cursor.fetchall()
        conn.close()

        if len(search) > 0:
            foundGroups = []
            for result in search:
                thisGroup = getGroup(result[0])
                foundGroups.append(thisGroup)

            return foundGroups

        else:
            return None

def searchGroupbyType(searchString):
    if utils.checkDB():
        conn = sqlite3.connect(DB)
        cursor = conn.cursor()
        cursor.execute(
                "SELECT id "
                "FROM groups "
                "WHERE type LIKE ?",
                ('%{}%'.format(searchString),)
                )
        search = cursor.fetchall()
        conn.close()

        if len(search) > 0:
            foundGroups = []
            for result in search:
                thisGroup = getGroup(result[0])
                foundGroups.append(thisGroup)

            return foundGroups

        else:
            return None

def searchGroupbyMember(memberid):
    if utils.checkDB():
        conn = sqlite3.connect(DB)
        cursor = conn.cursor()
        cursor.execute(
                "SELECT groupid "
                "FROM memberships "
                "WHERE (memberuserid = ? OR membergroupid = ?)",
                (memberid, memberid)
                )
        search = cursor.fetchall()
        conn.close()

        if len(search) > 0:
            foundGroups = []
            for result in search:
                thisGroup = getGroup(result[0])
                foundGroups.append(thisGroup)

            return foundGroups

        else:
            return None

def searchGroupbyPlace(placeid):
    if utils.checkDB():
        conn = sqlite3.connect(DB)
        cursor = conn.cursor()
        cursor.execute(
                "SELECT id "
                "FROM groups "
                "WHERE placeid = ?",
                (placeid,)
                )
        search = cursor.fetchall()
        conn.close()

        if len(search) > 0:
            foundGroups = []
            for result in search:
                thisGroup = getGroup(result[0])
                foundGroups.append(thisGroup)

            return foundGroups

        else:
            return None

def dbinit():
    try:
        conn = sqlite3.connect(DB)
        cursor = conn.cursor()
        config.debugQ.put('Configuring for groups...')
        cursor.execute(
                "CREATE TABLE groups("
                "id INTEGER PRIMARY KEY, name TEXT, type TEXT NOT NULL, placeid INTEGER, "
                "FOREIGN KEY(placeid) REFERENCES places(id) ON DELETE CASCADE ON UPDATE NO ACTION)"
                )
        conn.commit()
        config.debugQ.put('Success!')
        config.debugQ.put('Configuring for memberships...')
        cursor.execute(
                "CREATE TABLE memberships("
                "groupid INTEGER NOT NULL, memberuserid INTEGER, membergroupid INTEGER, "
                "UNIQUE(groupid, memberuserid, membergroupid), "
                "FOREIGN KEY(groupid) REFERENCES groups(id) ON DELETE CASCADE ON UPDATE NO ACTION, "
                "FOREIGN KEY(memberuserid) REFERENCES users(id) ON DELETE CASCADE ON UPDATE NO ACTION, "
                "FOREIGN KEY(membergroupid) REFERENCES groups(id) ON DELETE CASCADE ON UPDATE NO ACTION)"
                )
        conn.commit()
        conn.close()
        config.debugQ.put('Success!')

    except:
        config.debugQ.put('Unable to configure groups and/or memberships table!')

def registerCommands():
    global addGroupC
    addGroupC = command('group', utils.addC)
    addGroupC.description = 'Builds a group from parameters, then adds it to the database.'
    addGroupC.instruction = 'Specify group attributes using \'Attribute=Value\' with each separated by a space.'
    addGroupC.function = 'addGroupF'
    addGroupC.parent_module = mSelf
    global addGroupMemberC
    addGroupMemberC = command('member', addGroupC)
    addGroupMemberC.description = 'Adds a user (or group) as a member of a group.'
    addGroupMemberC.instruction = 'Specify a group followed by its new member.'
    addGroupMemberC.function = 'addGroupMemberF'
    global removeGroupC
    removeGroupC = command('group', utils.removeC)
    removeGroupC.description = 'Removes a group from the database.'
    removeGroupC.instruction = 'Specify a group.'
    removeGroupC.function = 'removeGroupF'
    removeGroupC.parent_module = mSelf
    global removeGroupMemberC
    removeGroupMemberC = command('member', removeGroupC)
    removeGroupMemberC.description = 'Removes a user\'s (or group\'s) membership from a group.'
    removeGroupMemberC.instruction = 'Specify a group followed by its member.'
    removeGroupMemberC.function = 'removeGroupMemberF'
    global editGroupC
    editGroupC = command('group', utils.editC)
    editGroupC.description = 'Updates an existing group with new attributes.'
    editGroupC.instruction = 'First specify a group. Then, specify new attributes using \'Attribute=Value\' with each separated by a space.'
    editGroupC.function = 'editGroupF'
    editGroupC.parent_module = mSelf
    global showGroupC
    showGroupC = command('group', utils.showC)
    showGroupC.description = 'Displays detailed information about a single group.'
    showGroupC.instruction = 'Specify a group.'
    showGroupC.function = 'showGroupF'
    showGroupC.parent_module = mSelf
    global listGroupC
    listGroupC = command('group', utils.listC)
    listGroupC.description = 'Lists all groups in the database.'
    listGroupC.function = 'listGroupF'
    listGroupC.parent_module = mSelf
    global listGroupMemberC
    listGroupMemberC = command('member', listGroupC)
    listGroupMemberC.description = 'Lists all members of a given group.'
    listGroupMemberC.function = 'listGroupMemberF'
    global findGroupC
    findGroupC = command('group', utils.findC)
    findGroupC.description = 'Searches for groups meeting the given criteria.'
    findGroupC.instruction = 'Specify a criteria.'
    findGroupC.parent_module = mSelf
    global findGroupNameC
    findGroupNameC = command('name', findGroupC)
    findGroupNameC.description = 'Searches for groups with names matching the given query.'
    findGroupNameC.instruction = 'Specify a name.'
    findGroupNameC.function = 'findGroupNameF'
    global findGroupTypeC
    findGroupTypeC = command('type', findGroupC)
    findGroupTypeC.description = 'Searches for groups with types matching the given query.'
    findGroupTypeC.instruction = 'Specify a type.'
    findGroupTypeC.function = 'findGroupTypeF'
    global findGroupPlaceC
    findGroupPlaceC = command('place', findGroupC)
    findGroupPlaceC.description = 'Searches for groups with places matching the given query.'
    findGroupPlaceC.instruction = 'Specify a place.'
    findGroupPlaceC.function = 'findGroupPlaceF'
    global findGroupMemberC
    findGroupMemberC = command('member', findGroupC)
    findGroupMemberC.description = 'Searches for groups of which the given user or group is a member.'
    findGroupMemberC.instruction = 'Specify a user or group.'
    findGroupMemberC.function = 'findGroupMemberF'

def addGroupF(inputData, content):
    groupDetails = content
    groupData = []

    for p in range(0, len(groupDetails)):
        if '=' in groupDetails[p]:
            groupData.append(groupDetails[p].split('='))

    groupDict = {}

    for q in groupData:
        groupDict.update({q[0] : q[1]})

    goodProfile = False
    
    newGroup = group()
   
    if 'name' in groupDict.keys():
        if groupDict['name'].startswith('"') and groupDict['name'].endswith('"'):
            newGroup.name = groupDict['name'][1:-1]
            goodProfile = True

    if 'type' in groupDict.keys():
        if groupDict['type'].startswith('"') and groupDict['type'].endswith('"'):
            if groupDict['type'][1:-1].lower() in groupTypes:
                newGroup.type = groupDict['type'][1:-1].lower()
                goodProfile = True

    if 'place' in groupDict.keys():
        if groupDict['place'].startswith('"') and groupDict['place'].endswith('"'):
            thisPlace = places.tryGetOnePlace(groupDict['place'][1:-1])
            if thisPlace:
                newGroup.place = thisPlace.id
                goodProfile = True

    if goodProfile:
        addGroup(newGroup)
        config.outQ.put(f'Added group {newGroup.name}.')

    else:
        config.outQ.put('Invalid attribute(s).')

def addGroupMemberF(inputData, content):
    groupString = content[0]
    memberString = content[1]

    thisGroup = tryGetOneGroup(groupString)
    thisMemberUser = users.tryGetOneUser(memberString)
    thisMemberGroup = tryGetOneGroup(memberString)

    if thisGroup and thisMemberUser:
        conn = sqlite3.connect(DB)
        cursor = conn.cursor()
        cursor.execute(
                "SELECT groupid, memberuserid "
                "FROM memberships "
                "WHERE groupid = ? AND memberuserid = ?",
                (thisGroup.id, thisMemberUser.id)
                )
        result = cursor.fetchone()
        conn.close()

        if result:
            config.outQ.put('User is already a member of the given group.')

        else:
            thisGroup.addMember(thisMemberUser.id)
            config.outQ.put('Membership added.')

    elif thisGroup and thisMemberGroup:
        conn = sqlite3.connect(DB)
        cursor = conn.cursor()
        cursor.execute(
                "SELECT groupid, membergroupid "
                "FROM memberships "
                "WHERE groupid = ? AND membergroupid = ?",
                (thisGroup.id, thisMemberGroup.id)
                )
        result = cursor.fetchone()
        conn.close()

        if result:
            config.outQ.put('Group is already a member of the given group.')

        else:
            thisGroup.addMember(thisMemberGroup.id)
            config.outQ.put('Membership added.')

    else:
        config.outQ.put('Group and/or member not found.')

def removeGroupF(inputData, content):
    thisThread = request_queue(inputData, filter_channel=True, filter_user=True)
    groupString = content[0]
    thisGroup = tryGetOneGroup(groupString)

    if thisGroup:
        config.outQ.put(f'{thisThread["tag"]}> Remove group {thisGroup.name}({thisGroup.id})? ({thisThread["tag"]}> y/N)')
        rawResponse = thisThread['queue'].get()
        response = rawResponse.content

        if response.lower() == 'y':
            removeGroup(thisGroup.id)
            config.outQ.put('Group removed.')

        else:
            config.outQ.put('Cancelled.')

    else:
        config.outQ.put('Group not found.')

def removeGroupMemberF(inputData, content):
    groupString = content[0]
    memberString = content[1]

    thisGroup = tryGetOneGroup(groupString)
    thisMemberUser = users.tryGetOneUser(memberString)
    thisMemberGroup = tryGetOneGroup(memberString)

    if thisGroup and thisMemberUser:
        conn = sqlite3.connect(DB)
        cursor = conn.cursor()
        cursor.execute(
                "SELECT groupid "
                "FROM memberships "
                "WHERE groupid = ? AND memberuserid = ?",
                (thisGroup.id, thisMemberUser.id)
                )
        result = cursor.fetchone()
        conn.close()

        if result:
            thisGroup.removeMember(thisMemberUser.id)
            config.outQ.put('Membership removed.')

        else:
            config.outQ.put('User is not a member of the given group.')

    elif thisGroup and thisMemberGroup:
        conn = sqlite3.connect(DB)
        cursor = conn.cursor()
        cursor.execute(
                "SELECT groupid "
                "FROM memberships "
                "WHERE groupid = ? AND membergroupid = ?",
                (thisGroup.id, thisMemberUser.id)
                )
        result = cursor.fetchone()
        conn.close()

        if result:
            thisGroup.removeMember(thisMemberGroup.id)
            config.outQ.put('Membership removed.')

        else:
            config.outQ.put('Group is not a member of the given group.')

    else:
        config.outQ.put('Group and/or member not found.')

def editGroupF(inputData, content):
    groupData = []
    groupString = content[0]
    groupDetails = content[1]

    thisGroup = tryGetOneGroup(groupString)

    if thisGroup:
        editGroup = group(thisGroup.id)

        for p in range(0, len(groupDetails)):
            if '=' in groupDetails[p]:
                groupData.append(groupDetails[p].split('='))

        groupDict = {}

        for q in groupData:
            groupDict.update({q[0] : q[1]})

        goodProfile = False
        
        if 'name' in groupDict.keys():
            if groupDict['name'].startswith('"') and groupDict['name'].endswith('"'):
                newGroup.name = groupDict['name'][1:-1]
                goodProfile = True

        if 'type' in groupDict.keys():
            if groupDict['type'].startswith('"') and groupDict['type'].endswith('"'):
                if groupDict['type'][1:-1].lower() in groupTypes:
                    newGroup.type = groupDict['type'][1:-1].lower()
                    goodProfile = True

        if 'place' in groupDict.keys():
            if groupDict['place'].startswith('"') and groupDict['place'].endswith('"'):
                thisPlace = places.tryGetOnePlace(groupDict['place'][1:-1])
                if thisPlace:
                    newGroup.place = thisPlace.id
                    goodProfile = True

        if goodProfile:
            updateGroup(editGroup)
            config.outQ.put(f'Updated group {thisGroup.name}({thisGroup.id}).')

        else:
            config.outQ.put('Invalid attribute(s).')

    else:
        config.outQ.put('Group not found.')

def showGroupF(inputData, content):
    groupString = ' '.join(content)
    thisGroup = tryGetOneGroup(groupString)

    if thisGroup:
        output_text = ''
        output_text += (f'Name = {thisGroup.name}\n')
        output_text += (f'ID = {thisGroup.id}\n')
        output_text += (f'Type = {thisGroup.type}\n')
        output_text += (f'Place = {thisGroup.place}\n')
        output_text += ('\n')

        members = thisGroup.getMembers()
        
        output_text += ('Member Users:\n')
        for i, each in enumerate(members['users']):
            if i:
                output_text += '\n'

            output_text += f'{each.name}({each.id})'

        output_text += ('\n\nMember Groups:\n')
        for i, each in enumerate(members['groups']):
            if i:
                output_text += '\n'

            output_text += f'{each.name}({each.id})'

        config.outQ.put(output_text)

    else:
        config.outQ.put('Group not found.')

def listGroupF(inputData):
    if utils.checkDB():
        conn = sqlite3.connect(DB)
        cursor = conn.cursor()
        cursor.execute(
                "SELECT id FROM groups"
                )
        results = cursor.fetchall()
        conn.close()

        output_text = 'All Groups:\n'

        for i, each in enumerate(results):
            if i:
                output_text += '\n'
        
            thisGroup = getGroup(each[0])
            output_text += f'{thisGroup.id} - {thisGroup.name} - {thisGroup.type} - {thisGroup.place}'

        config.outQ.put(output_text)

def listGroupMemberF(inputData, content):
    groupString = ' '.join(content)
    thisGroup = tryGetOneGroup(groupString)

    if thisGroup:
        members = thisGroup.getMembers()

        output_text = f'Members of {thisGroup.name}({thisGroup.id}):\n'
        
        output_text += ('Member Users:\n')
        for i, each in enumerate(members['users']):
            if i:
                output_text += '\n'

            output_text += f'{each.name}({each.id})'

        output_text += ('\n\nMember Groups:\n')
        for i, each in enumerate(members['groups']):
            if i:
                output_text += '\n'

            output_text += f'{each.name}({each.id})'

        config.outQ.put(output_text)

    else:
        config.outQ.put('Group not found.')

def findGroupNameF(inputData, content):
    groupString = ' '.join(content)
    results = searchGroupbyName(groupString)
    if results:
        output_text = ''
        if len(results) == 1:
            output_text += 'One group found:\n'

        else:
            output_text += f'{len(results)} groups found:\n'

        for i, each in enumerate(results):
            if i:
                output_text += '\n'
    
            output_text += f'{each.name}({each.id})'

        config.outQ.put(output_text)

    else:
        config.outQ.put('No groups found!')

def findGroupTypeF(inputData, content):
    typeString = ' '.join(content)
    results = searchGroupbyType(typeString)
    if results:
        output_text = ''
        if len(results) == 1:
            output_text += 'One group found:\n'

        else:
            output_text += f'{len(results)} groups found:\n'

        for i, each in enumerate(results):
            if i:
                output_text += '\n'
    
            output_text += f'{each.name}({each.id})'

        config.outQ.put(output_text)

    else:
        config.outQ.put('No groups found!')

def findGroupPlaceF(inputData, content):
    placeString = ' '.join(content)
    thisPlace = places.tryGetOnePlace(placeString)

    if thisPlace:
        results = searchGroupbyPlace(thisPlace.id)
        if results:
            output_text = ''
            if len(results) == 1:
                output_text += 'One group found:\n'

            else:
                output_text += f'{len(results)} groups found:\n'

            for i, each in enumerate(results):
                if i:
                    output_text += '\n'
        
                output_text += f'{each.name}({each.id})'

            config.outQ.put(output_text)

        else:
            config.outQ.put('No groups found!')

    else:
        config.outQ.put('Place not found!')

def findGroupMemberF(inputData, content):
    memberString = ' '.join(content)
    thisMemberUser = users.tryGetOneUser(memberString)
    thisMemberGroup = tryGetOneGroup(memberString)

    if thisMemberUser:
        results = searchGroupbyMember(thisMemberUser.id)
        if results:
            output_text = ''
            if len(results) == 1:
                output_text += 'One group found:\n'

            else:
                output_text += f'{len(results)} groups found:\n'

            for i, each in enumerate(results):
                if i:
                    output_text += '\n'
        
                output_text += f'{each.name}({each.id})'

            config.outQ.put(output_text)

        else:
            config.outQ.put('No groups found!')

    elif thisMemberGroup:
        results = searchGroupbyMember(thisMemberGroup.id)
        if results:
            output_text = ''
            if len(results) == 1:
                output_text += 'One group found:\n'

            else:
                output_text += f'{len(results)} groups found:\n'

            for i, each in enumerate(results):
                if i:
                    output_text += '\n'
        
                output_text += f'{each.name}({each.id})'

            config.outQ.put(output_text)

        else:
            config.outQ.put('No groups found!')

    else:
        config.outQ.put('Member not found!')

if __name__ == "__main__":
    print("No main.")
else:
    registerCommands()
