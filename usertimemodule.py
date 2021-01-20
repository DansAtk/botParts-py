import pytz
import datetime
import sqlite3
import calendar

import commandsmodule
import config

includes = {}

time = commandsmodule.command('time', __name__)

def init():
    includes.update({time.name : time})
    time.description = "Time management."
    time.function = 'timeF'
    time.parameters.update({'set' : commandsmodule.command('set', __name__)})
    time.parameters['set'].description = "Sets the time."
    time.parameters['set'].function = 'setF'
    config.imports.append('usertimemodule')

def timeF(message):
    if len(message) > 0:
        print(time.paramError(message))
    else:
        today = datetime.datetime.now()
        print(today)

def setF(message):
    if len(message) > 0:
        print(time.parameters['set'].paramError(message))
    else:
        print("The time has been set.")

if __name__ == "__main__":
    print("No main.")
else:
    init()
