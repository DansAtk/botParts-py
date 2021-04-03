import sys
import os
import pathlib
import shutil

import sqlite3
from datetime import *

from core import config
from core.commandM import command

mSelf = sys.modules[__name__]
includes = {}
config.imports.append(__name__)

currentDB = ''

def init():
    global databaseC
    databaseC = command('database', mSelf)
    databaseC.description = 'Commands for managing databases in the bot\'s data folder.'
    databaseC.function = 'databaseF'
    global setupC
    setupC = command('setup', databaseC)
    setupC.description = 'Initializes a new database. If the database already exists, it can be reinitialized.'
    setupC.function = 'initialize'
    global setC
    setC = command('set', databaseC)
    setC.description = 'Sets the current active database.'
    setC.function = 'setF'
    global checkC
    checkC = command('check', databaseC)
    checkC.description = 'Checks the current active database.'
    checkC.function = 'checkF'
    global listC
    listC = command('list', databaseC)
    listC.description = 'Lists all databases in the bot\'s data folder.'
    listC.function = 'listF'
    global deleteC
    deleteC = command('delete', databaseC)
    deleteC.description = 'Deletes a database. By default, deletes the currently active database if one is not specified.'
    deleteC.function = 'deleteF'
    global backupC
    backupC = command('backup', databaseC)
    backupC.description = 'Creates a backup of the selected database, or all databases.'
    backupC.function = 'backupF'

def databaseF():
    print(databaseC.help() + '\n')
    listF()
    print()
    checkF()

def initialize(userinput=''):
    global currentDB

    if not config.dataPath.exists():
        pathlib.path.mkdir(config.dataPath)

    if len(userinput) > 0:
        thisDB = config.dataPath / (' '.join(userinput) + '.db')
    else:
        thisDB = checkDB()

    try:
        doInit = False
        if thisDB.exists():
            response = input('Database \'{dbname}\' already exists. Re-initialize database? This will empty the database. <y/N> '.format(dbname=thisDB.stem))
            if response.lower() == 'y':
                doInit = True
            else:
                print('Canceled.')
        else:
            if thisDB.stem.lower() == 'all':
                print('\'All\' is a reserved word and cannot be used as a database name.')
            else:
                doInit = True
        
        if doInit:
            conn = sqlite3.connect(thisDB)
            cursor = conn.cursor()
            cursor.execute("CREATE TABLE info(id INTEGER PRIMARY KEY AUTOINCREMENT, key TEXT, value TEXT)")
            cursor.execute("INSERT INTO info(key, value) VALUES (?, ?)", ('dbversion', config.dbversion))
            cursor.execute("INSERT INTO info(key, value) VALUES (?, ?)", ('trigger', '!'))
            cursor.execute("INSERT INTO info(key, value) VALUES (?, ?)", ('cheer', '\U0001F44D'))
            cursor.execute("INSERT INTO info(key, value) VALUES (?, ?)", ('serverid', ''))
            cursor.execute("INSERT INTO info(key, value) VALUES (?, ?)", ('servername', ''))
            conn.commit()
            conn.close()

            for module in config.imports:
                if hasattr(sys.modules[module], 'dbinit'):
                    sys.modules[module].dbinit(thisDB)

            print('Database \'{dbname}\' initialized.'.format(dbname=thisDB.stem))

            currentDB = thisDB

    except:
        #print(sys.exc_info()[0])
        print('Error.')

def getF(DBname):
    result = ''
    DB = config.dataPath / (DBname + '.db')

    if DB.exists():
        result = DB
    else:
        result = 0

    return result

def checkDB():
    global currentDB
    DB = ''

    if currentDB:
        print('nope')
        DB = currentDB
    else:
        DB = config.dataPath / 'defaultDB.db'

    return DB

def checkF():
    DB = checkDB()

    print('Current active database is: {dbname}'.format(dbname=DB.stem))

def listDB():
    DBlist = [f for f in config.dataPath.glob('*.db')]

    return DBlist

def listF():
    DBlist = listDB()

    print('All databases:')
    for DB in DBlist:
        print(DB.stem)

def setF(userinput):
    global currentDB
    thisDB = config.dataPath / (' '.join(userinput) + '.db')

    if thisDB.exists():
        currentDB = thisDB
    else:
        response = input('Database \'{dbname}\' not found! Would you like to create it? <y/N> '.format(dbname=' '.join(userinput)))

        if response.lower() == 'y':
            initialize(userinput)
        else:
            print('Canceled.')

def deleteF(userinput=''):
    doDelete = False

    if len(userinput) > 0:
        thisDB = config.dataPath / (' '.join(userinput) + '.db')

        if thisDB.exists():
            doDelete = True
        else:
            print('Database \'{dbname}\' does not exist!'.format(dbname=' '.join(userinput)))

    else:
        thisDB = checkDB()
        doDelete = True

    if doDelete:
        response = input('Are you sure you want to delete database \'{dbname}\'? <y/N> '.format(dbname=thisDB.stem))

        if response.lower() == 'y':
            thisDB.unlink()
            print('Database deleted.')

        else:
            print('Cancelled.')

def backup(DB):
    timestamp = (datetime.now()).strftime("%Y%m%d%H%M%S%f")
    
    if not config.backupPath.exists():
        pathlib.path.mkdir(config.backupPath)

    backupFile = config.backupPath / ('{dbname}_backup_{code}.db'.format(dbname=DB.stem, code=timestamp))
    
    shutil.copy2(DB, backupFile)

    return backupFile

def backupF(userinput=''):
    if len(userinput) > 0:
        if ' '.join(userinput).lower() == 'all':
            counter = 0
            for DB in listDB():
                backup(DB)
                counter += 1

            print('{dbcount} databases found and backed up.'.format(dbcount=counter))

        else:
            thisDB = config.dataPath / (' '.join(userinput) + '.db')
            
            if thisDB.exists():
                oFile = backup(thisDB)
                print('Database \'{dbname}\' backed up to \'{backupname}\'.'.format(dbname=thisDB.stem, backupname=oFile.name))

            else:
                print('Database \'{dbname}\' not found!'.format(dbname=thisDB.stem))

    else:
        thisDB = checkDB()

        if thisDB.exists():
            oFile = backup(thisDB)
            print('Database \'{dbname}\' backed up to \'{backupname}\'.'.fomat(dbname=thisDB.stem, backupname=oFile.name))

        else:
            print('No database is currently active or selected.')

def cleanup():
    backupF(['all'])

if __name__ == "__main__":
    print("No main.")
else:
    init()
