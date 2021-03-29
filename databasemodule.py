import os
import sqlite3
import config
import commandsmodule

includes = {}

data = commandsmodule.command('data', __name__)

def init():
    config.imports.append('databasemodule')
    includes.update({data.name : data})
    data.description = "A template for a new command."
    data.function = 'dataF'
    data.parameters.update({'parametertemplate' : 
        commandsmodule.command('parametertemplate', __name__)})
    data.parameters['parametertemplate'].description = (
        "A template for a new command.")
    data.parameters['parametertemplate'].function = (
        'parametertemplateF')

def initialize():
    if not os.path.isdir(config.dataPath):
        os.mkdir(config.dataPath)
    
    try:
        conn = sqlite3.connect(config.database)
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE users(id INTEGER PRIMARY KEY, username TEXT, " 
        + "password TEXT, rank INTEGER)")
        print("Users table initialized.")
        conn.commit()
        conn.close()
    except:
        print("Error.")

def getUser():
    print("Hello")

def dataF(message):
    if len(message) > 0:
        print(data.paramError(message))
    else:
        initialize()

def parametertemplateF(message):
    if len(message) > 0:
        print(data.parameters['parametertemplate'].paramError(message))
    else:
        print("A template for a new parameter's function. Should expect the " +
        "remainder of the typed command as an argument.")

if __name__ == "__main__":
    print("No main.")
else:
    init()
