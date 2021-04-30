import sys
import os
import pathlib
import shutil

import sqlite3

import config
from core.commands import command
from core import utils
from core import users
from core import places

mSelf = sys.modules[__name__]
includes = {}
config.register(mSelf)
DB = config.database

class perm:
    def __init__(self, COMMAND, TYPE, VALUE, TARGET=None):
        self.command = COMMAND
        self.type = TYPE
        self.value = VALUE
        self.target = TARGET

def getCommandPerm(profile):
    if utils.checkDB():
        conn = sqlite3.connect(DB)
        cursor = conn.cursor()
        cursor.execute(
                "SELECT value "
                "FROM perms "
                "WHERE command = ? AND userid IS NULL AND placeid IS NULL AND groupid IS NULL",
                (profile.command,)
                )
        result = cursor.fetchone()
        conn.close()

        if result:
            return result

        else:
            return None

def getUserPerm(profile):
    if utils.checkDB():
        conn = sqlite3.connect(DB)
        cursor = conn.cursor()
        cursor.execute(
                "SELECT value "
                "FROM perms "
                "WHERE command = ? AND userid = ? AND placeid IS NULL AND groupid IS NULL",
                (profile.command, profile.target)
                )
        result = cursor.fetchone()
        conn.close()

        if result:
            return result

        else:
            return None

def getCommandPerm(profile):
    if utils.checkDB():
        conn = sqlite3.connect(DB)
        cursor = conn.cursor()
        cursor.execute(
                "SELECT value "
                "FROM perms "
                "WHERE command = ? AND userid IS NULL AND placeid IS NULL AND groupid IS NULL"
                )
        result = cursor.fetchone()
        conn.close()

        if result:
            return result

        else:
            return None

def getCommandPerm(profile):
    if utils.checkDB():
        conn = sqlite3.connect(DB)
        cursor = conn.cursor()
        cursor.execute(
                "SELECT value "
                "FROM perms "
                "WHERE command = ? AND userid IS NULL AND placeid IS NULL AND groupid IS NULL"
                )
        result = cursor.fetchone()
        conn.close()

        if result:
            return result

        else:
            return None

def getUserPerm(profile):
    pass

def getPlacePerm(profile):
    pass

def getAliasPerm(profile):
    pass

def getGroupPerm(profile):
    pass

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
    thisAlias = aliases.getAlias(profile.target)

    if thisAlias:
        if utils.checkDB():
            conn = sqlite3.connect(DB)
            cursor = conn.cursor()
            cursor.execute(
                    "INSERT INTO perms"
                    "(command, userid, placeid, value) "
                    "VALUES (?, ?, ?, ?)",
                    (profile.command, thisAlias.user, thisAlias.place, profile.value)
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

def removeCommandPerm(profile):

