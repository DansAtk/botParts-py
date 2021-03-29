import os
import sqlite3
import config
import commandsmodule
import sys
import pathlib

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
    database.parameters.update({'get' : 
        commandsmodule.command('get', __name__)})
    database.parameters['get'].description = (
        "Checks the current active database.")
    database.parameters['get'].function = 'getDBF'
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
        thisDB = config.dataPath / (message + '.db')
    else:
        thisDB = getDB()
    
    try:
        doInit = False
        if thisDB.exists():
            response = input('Database \'{dbname}\' already exists. Re-initialize database? This will empty the database. <y/N> '.format(dbname=thisDB.stem))
            if response.lower() == 'y':
                doInit = True
            else:
                print('Canceled.')
        else:
            doInit = True

        if doInit:
            conn = sqlite3.connect(thisDB)
            cursor = conn.cursor()
            conn.commit()
            conn.close()
            for module in config.imports:
                if hasattr(sys.modules[module], 'dbinit'):
                    sys.modules[module].dbinit(thisDB)
            print('Database \'{dbname}\' initialized.'.format(dbname=thisDB.stem))

            currentDB = thisDB

    except:
        print("Error.")

def getDB():
    global currentDB
    DB = ""
    if currentDB:
        DB = currentDB
    else:
        DB = config.dataPath / 'defaultDB.db'

    return DB

def getDBF(message=''):
    DB = getDB()
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
    messageDB = config.dataPath / (message + '.db')
    if messageDB.exists():
        currentDB = messageDB
    else:
        response = input('Database \'{dbname}\' not found! Would you like to create it? <y/N>'.format(dbname=message))
        if response.lower() == 'y':
            initialize(message)
        else:
            print('Canceled.')

def deleteF(message=''):
    doDelete = False

    if len(message) > 0:
        thisDB = config.dataPath / (message + '.db')
        if thisDB.exists():
            doDelete = True
        else:
            print('Database \'{dbname}\' does not exist!'.format(dbname=message))

    else:
       thisDB = getDB() 
       doDelete = True

    if doDelete:
       response = input('Are you sure you want to delete database \'{dbname}\'? <y/N> '.format(dbname=thisDB.stem))
       
       if response.lower() == 'y':
           os.remove(thisDB)
           print('Database deleted.')
       else:
           print('Cancelled.')

if __name__ == "__main__":
    print("No main.")
else:
    init()
