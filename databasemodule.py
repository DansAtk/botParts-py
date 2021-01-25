import sqlite3
import config
import commandsmodule

includes = {}

commandtemplate = commandsmodule.command('commandtemplate', __name__)

def init():
    config.imports.append('databasemodule')
    includes.update({commandtemplate.name : commandtemplate})
    commandtemplate.description = "A template for a new command."
    commandtemplate.function = 'commandtemplateF'
    commandtemplate.parameters.update({'parametertemplate' : 
        commandsmodule.command('parametertemplate', __name__)})
    commandtemplate.parameters['parametertemplate'].description = (
        "A template for a new command.")
    commandtemplate.parameters['parametertemplate'].function = (
        'parametertemplateF')

def initialize():
    try:
        conn = sqlite3.connect(config.database)
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE users(id INTEGER PRIMARY KEY, username TEXT, " 
        + "password TEXT, rank INTEGER)")
        print("Users table initialized.")
    except:
        print("Error.")
    finally:
        conn.commit()
        conn.close()

def getUser():
    print("Hello")

def commandtemplateF(message):
    if len(message) > 0:
        print(commandtemplate.paramError(message))
    else:
        print("A template for a new command's function. Should expect the " +
        "remainder of the typed command as an argument.")

def parametertemplateF(message):
    if len(message) > 0:
        print(commandtemplate.parameters['parametertemplate'].paramError(message))
    else:
        print("A template for a new parameter's function. Should expect the " +
        "remainder of the typed command as an argument.")

if __name__ == "__main__":
    print("No main.")
else:
    init()
