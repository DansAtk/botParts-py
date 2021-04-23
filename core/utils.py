import sys
import os
import pathlib
import shutil
import multiprocessing
import time
import json

import sqlite3
import pytz
import calendar
from datetime import *

import config
from core.commandM import command, request_queue

mSelf = sys.modules[__name__]
includes = {}
config.register(mSelf)
DB = config.database
imports = config.imports

def getTime(refTZ=None):
    if refTZ:
        return datetime.now(pytz.timezone(refTZ))
    else:
        return datetime.now(pytz.timezone('US/Eastern'))

def getTimezone(tzName):
    return tryGetOneTimezone(tzName)

def tryGetOneTimezone(timezonestring):
    thisTimezone = None

    searchResults = searchTimezonebyName(timezonestring)

    if searchResults:
        if len(searchResults) == 1:
            thisTimezone = searchResults[0]

    return thisTimezone

def searchTimezonebyName(userinput):
    foundTZ = []
    
    for timezone in pytz.all_timezones:
        if userinput.lower() in timezone.lower():
            foundTZ.append(timezone)

    if len(foundTZ) > 0:
        return foundTZ
    
    else:
        return None

def checkDB():
    if DB.exists():
        return True

    else:
        config.debugQ.put('Database not found.')
        return False

def backupDB():
    if checkDB():
        timestamp = (datetime.now()).strftime("%Y%m%d%H%M%S%f")
    
        if not config.backupPath.exists():
            config.backupPath.mkdir()

        backupFile = config.backupPath / ('{dbname}_backup_{code}.db'.format(dbname=config.database.stem, code=timestamp))
    
        shutil.copy2(config.database, backupFile)

        return backupFile

def cleanup():
    if checkDB():
        oFile = backupDB()
        config.debugQ.put(f'Database backed up to \'{oFile.name}\'.')

def registerCommands():
    global databaseC
    databaseC = command('database', mSelf)
    databaseC.description = 'Commands for managing the bot\'s database.'
    databaseC.instruction = 'Specify a parameter. Alone, displays information about the database\'s current state.'
    databaseC.function = 'databaseF'
    global databaseSetupC
    databaseSetupC = command('setup', databaseC)
    databaseSetupC.description = 'Initializes the database. If the database already exists, it can be reinitialized.'
    databaseSetupC.function = 'databaseSetupF'
    global databaseDeleteC
    databaseDeleteC = command('delete', databaseC)
    databaseDeleteC.description = 'Deletes the database.' 
    databaseDeleteC.function = 'databaseDeleteF'
    global databaseBackupC
    databaseBackupC = command('backup', databaseC)
    databaseBackupC.description = 'Creates a backup of the database.'
    databaseBackupC.function = 'databaseBackupF'
    global addC
    addC = command('add', mSelf)
    addC.description = 'Used to create new objects in the database.'
    addC.instruction = 'Specify a parameter.'
    global removeC
    removeC = command('remove', mSelf)
    removeC.description = 'Used to remove existing objects from the database.'
    removeC.instruction = 'Specify a parameter.'
    global editC
    editC = command('edit', mSelf)
    editC.description = 'Updates existing objects with new attributes.'
    editC.instruction = 'Specify a parameter.'
    global showC
    showC = command('show', mSelf)
    showC.description = 'Displays detailed information about database objects.'
    showC.instruction = 'Specify a parameter.'
    global listC
    listC = command('list', mSelf)
    listC.description = 'Lists all objects of the given type currently in the database.'
    listC.instruction = 'Specify a parameter.'
    global listTimezoneC
    listTimezoneC = command('timezone', listC)
    listTimezoneC.description = 'Lists all available timezones.'
    listTimezoneC.function = 'listTimezoneF'
    global timeC
    timeC = command('time', mSelf)
    timeC.description = 'Displays the current time.'
    timeC.function = 'timeF'
    global timeZonesC
    timeZonesC = command('zones', timeC)
    timeZonesC.description = 'Lists all available timezones.'
    timeZonesC.function = 'listTimezoneF'
    global findC
    findC = command('find', mSelf)
    findC.description = 'Searches for objects meeting the given criteria.'
    findC.instruction = 'Specify a parameter.'
    global findTimezoneC
    findTimezoneC = command('timezone', findC)
    findTimezoneC.description = 'Searches for timezones with names matching the given query.'
    findTimezoneC.instruction = 'Specify the name of a timezone.'
    findTimezoneC.function = 'findTimezoneF'
    global botC
    botC = command('bot', mSelf)
    botC.description = 'Bot controls and monitoring. Usable by bot owner only.'
    botC.function = 'botF'
    global botConfigC
    botConfigC = command('config', botC)
    botConfigC.description = 'Used to manage the bot\'s default configuration.'
    botConfigC.instruction = 'Specify a parameter. By itself displays the current config.'
    botConfigC.function = 'botConfigF'
    global botConfigPushC
    botConfigPushC = command('push', botConfigC)
    botConfigPushC.description = 'Pushes the current default config to a file.'
    botConfigPushC.function = 'botConfigPushF'
    global botConfigPullC
    botConfigPullC = command('pull', botConfigC)
    botConfigPullC.description = 'Imports default config from a file.'
    botConfigPullC.function = 'botConfigPullF'
    global botConfigTriggerC
    botConfigTriggerC = command('trigger', botConfigC)
    botConfigTriggerC.description = 'Used to alter the default trigger.'
    botConfigTriggerC.instruction = 'Specify a new trigger.'
    botConfigTriggerC.function = 'botConfigTriggerF'
    global botShutdownC
    botShutdownC = command('shutdown', botC)
    botShutdownC.description = 'Closes the bot gracefully.'
    botShutdownC.function = 'botShutdownF'
    includes.update({'exit' : botShutdownC})
    includes.update({'quit' : botShutdownC})

def databaseF(inputData):
    config.outQ.put(databaseC.help())

def databaseSetupF(inputData):
    if not config.dataPath.exists():
        config.dataPath.mkdir()

    try:
        doInit = False
        if DB.exists():
            thisThread = request_queue(inputData, filter_channel=True, filter_user=True)
            thisQ = thisThread['queue']
            config.outQ.put(f'{thisThread["tag"]}> Database already exists. Re-initialize? This will empty the database. ({thisThread["tag"]}> y/N)')
            rawResponse = thisQ.get()
            response = ' '.join(rawResponse.content)
            if response.lower() == 'y':
                DB.unlink()
                doInit = True
            else:
                config.outQ.put('Canceled.')
        else:
            doInit = True
        
        if doInit:
            conn = sqlite3.connect(DB)
            cursor = conn.cursor()
            config.debugQ.put('Configuring info table...')
            cursor.execute(
                    "CREATE TABLE info("
                    "id INTEGER PRIMARY KEY AUTOINCREMENT, key TEXT, value TEXT)"
                    )
            cursor.execute("INSERT INTO info(key, value) VALUES (?, ?)",
                    ('dbversion', config.settings['dbversion']))
            conn.commit()
            conn.close()

            for collection in imports:
                for module in imports[collection]:
                    if hasattr(sys.modules[module], 'dbinit'):
                        sys.modules[module].dbinit(DB)

            config.debugQ.put('Database initialized.')
    
    except:
        config.debugQ.put('An error occurred.')

def databaseDeleteF(inputData):
    thisThread = request_queue(inputData, filter_channel=True, filter_user=True)
    thisQ = thisThread['queue']
    config.outQ.put(f'{thisThread["tag"]}> Are you sure you want to delete the current database? ({thisThread["tag"]}> y/N)')
    rawResponse = thisQ.get()
    response = ' '.join(rawResponse.content)

    if response.lower() == 'y':
        config.database.unlink()
        config.outQ.put('Database deleted.')

    else:
        config.outQ.put('Cancelled.')

def databaseBackupF(inputData):
    if checkDB():
        oFile = backupDB()
        config.debugQ.put(f'Database backed up to \'{oFile.name}\'.')

def listTimezoneF(inputData):
    output_text = ''

    for i, each in enumerate(pytz.all_timezones):
        if i:
            output_text += '\n'

        output_text += each

    config.outQ.put(output_text)

def timeF(inputData):
    config.outQ.put(f'The current time is {getTime()}.')

def findTimezoneF(inputData, content):
    timezoneString = ' '.join(content)
    results = searchTimezonebyName(timezoneString)
    
    if results:
        output_text = ''
        if len(results) == 1:
            output_text += 'One timezone found:\n'

        else:
            output_text += f'{len(results)} timezones found:\n'

        for i, each in enumerate(results):
            if i:
                output_text += '\n'
    
            output_text += each

        config.outQ.put(output_text)

    else:
        config.outQ.put('No timezones found!')

def botConfigPushF(inputData=None):
    config.debugQ.put('Pushing config to file...')
    try:
        with open(config.conFile, 'w') as conf:
            json.dump(config.settings, conf)
        config.debugQ.put('Success!')

    except IOError:
        config.debugQ.put('File or location doesn\'t exist!')
        
    except:
        config.debugQ.put('Failure!')

def botConfigPullF(inputData=None):
    config.debugQ.put('Pulling config from file...')
    try:
        with open(config.conFile, 'r') as conf:
            config.settings = json.load(conf)
        config.debugQ.put('Success!')
    except FileNotFoundError:
        config.debugQ.put('No config file found!')

def botConfigTriggerF(inputData, content):
    triggerText = content[0]

    if len(triggerText) == 1:
        if triggerText.lower() == 'none':
            try:
                del config.settings['trigger']
                config.outQ.put('Trigger has been removed.')

            except KeyError:
                config.outQ.put('Trigger is already set to \'None\'.')

        else:
            if len(triggerText) < 3:
                if len(triggerText) > 0:
                    config.settings['trigger'] = triggerText
                    config.outQ.put(f'Trigger has been set to {triggerText}')

                else:
                    config.outQ.put('Please specify at least one character for a trigger.')

            else:
                config.outQ.put('Try a shorter trigger.')
    else:
        config.outQ.put('Please limit the trigger to a single character or small group of characters with no whitespace.')

def botShutdownF(inputData=None):
    moduleCleanup()

def moduleCleanup():
    config.debugQ.put('Cleaning up modules...')

    for collection in imports:
        print(collection)
        for module in imports[collection]:
            print(module)
            if hasattr(sys.modules[module], 'cleanup'):
                print(f'{module} has it!')
                thisfunc = getattr(sys.modules[module], 'cleanup')
                sys.modules[module].cleanup()

    config.running.clear()

def cleanup():
    botConfigPushF()

if __name__ == "__main__":
    print("No main.")
else:
    registerCommands()
    botConfigPullF()
