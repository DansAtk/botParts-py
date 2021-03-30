import os
import sqlite3
import config
import commandsmodule
import sys
import pathlib
import shutil
from datetime import *

includes = {}

currentDB = ""

database = commandsmodule.command('database', __name__)

def init():
    config.imports.append('databasemodule')
    includes.update({database.name : database})
    database.description = "Commands for managing databases in the bot's data folder."
    database.function = 'databaseF'
    database.parameters.update({'setup' : 
        commandsmodule.command('setup', __name__)})
    database.parameters['setup'].description = (
        "Initializes a new database. If the database already exists, it can be reinitialized.")
    database.parameters['setup'].function = 'initialize'
    database.parameters.update({'set' : 
        commandsmodule.command('set', __name__)})
    database.parameters['set'].description = (
        "Sets the current active database.")
    database.parameters['set'].function = 'setDBF'
    database.parameters.update({'check' : 
        commandsmodule.command('check', __name__)})
    database.parameters['check'].description = (
        "Checks the current active database.")
    database.parameters['check'].function = 'checkDBF'
    database.parameters.update({'list' : 
        commandsmodule.command('list', __name__)})
    database.parameters['list'].description = (
        "Lists all databases in the bot's data folder.")
    database.parameters['list'].function = 'listDBF'
    database.parameters.update({'delete' : 
        commandsmodule.command('delete', __name__)})
    database.parameters['delete'].description = (
        "Deletes a database. By default, deletes the currently active database if one is not specified.")
    database.parameters['delete'].function = 'deleteF'
    database.parameters.update({'backup' : 
        commandsmodule.command('backup', __name__)})
    database.parameters['backup'].description = (
        "Creates a backup of the selected database, or all databases.")
    database.parameters['backup'].function = 'backupF'

def databaseF(message):
    if len(message) > 0:
        print(database.paramError(message))
    else:
        initialize()
        
def initialize(message=''):
    global currentDB

    if not os.path.isdir(config.dataPath):
        os.mkdir(config.dataPath)
    
    if len(message) > 0:
        thisDB = config.dataPath / (' '.join(message) + '.db')
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
            cursor.execute("INSERT INTO info(key, value) VALUES (?, ?)", ('trigger', '.'))
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
        print("Error.")

def getDB(DBname=''):
    result = ''
    if len(DBname) > 0:
        DB = config.dataPath / (DBname + '.db')
        if DB.exists():
            result = DB
        else:
            result = 0
    else:
        result = 0

    return result


def checkDB():
    global currentDB
    DB = ""
    if currentDB:
        DB = currentDB
    else:
        DB = config.dataPath / 'defaultDB.db'

    return DB

def checkDBF(message=''):
    DB = checkDB()
    print('Current active database is: {dbname}'.format(dbname=DB.stem))

def listDB():
    DBlist = [f for f in config.dataPath.glob('*.db')]

    return DBlist

def listDBF(message=''):
    DBlist = listDB()
    for DB in DBlist:
        print(DB.stem)

def setDBF(message):
    global currentDB
    messageDB = config.dataPath / (' '.join(message) + '.db')
    if messageDB.exists():
        currentDB = messageDB
    else:
        response = input('Database \'{dbname}\' not found! Would you like to create it? <y/N>'.format(dbname=' '.join(message)))
        if response.lower() == 'y':
            initialize(message)
        else:
            print('Canceled.')

def deleteF(message=''):
    doDelete = False

    if len(message) > 0:
        thisDB = config.dataPath / (' '.join(message) + '.db')
        if thisDB.exists():
            doDelete = True
        else:
            print('Database \'{dbname}\' does not exist!'.format(dbname=' '.join(message)))

    else:
       thisDB = checkDB() 
       doDelete = True

    if doDelete:
       response = input('Are you sure you want to delete database \'{dbname}\'? <y/N> '.format(dbname=thisDB.stem))
       
       if response.lower() == 'y':
           os.remove(thisDB)
           print('Database deleted.')
       else:
           print('Cancelled.')

def backup(DB):
    timestamp = (datetime.now()).strftime("%Y%m%d%H%M%S%f")
    if not os.path.isdir(config.backupPath):
        os.mkdir(config.backupPath)
    backupFile = config.backupPath / ('{dbname}_backup_{code}.db'.format(dbname=DB.stem, code=timestamp))
    shutil.copy2(DB, backupFile)
    return backupFile

def backupF(message=''):
    if len(message) > 0:
        if ' '.join(message).lower() == 'all':
            counter = 0
            for DB in listDB():
                backup(DB)
                counter += 1

            print('{dbcount} databases found and backed up.'.format(dbcount=counter))

        else:
            thisDB = config.dataPath / (' '.join(message) + '.db')
            if thisDB.exists():
                oFile = backup(thisDB)
                print('Database \'{dbname}\' backed up to \'{backupname}\'.'.format(dbname=thisDB.stem, backupname=oFile.name))
            else:
                print('Database \'{dbname}\' not found!'.format(dbname=thisDB.stem))
    else:
        thisDB = checkDB()
        if thisDB.exists():
            oFile = backup(thisDB)
            print('Database \'{dbname}\' backed up to \'{backupname}\'.'.format(dbname=thisDB.stem, backupname=oFile.name))
        else:
            print('No database is currently active or selected.')

def cleanup():
    backupF(['all'])

if __name__ == "__main__":
    print("No main.")
else:
    init()
