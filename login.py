import sys
import multiprocessing
import threading
import time

from core import config

config.inQ = multiprocessing.Queue()
config.outQ = multiprocessing.Queue()
config.debugQ = multiprocessing.Queue()
config.promptQ = multiprocessing.Queue()

from core import *
from ext import *

mSelf = sys.modules[__name__]
includes = {}
config.imports.append(__name__)

currentUser = None
currentServer = None
currentAlias = None

def inM():
    while config.running.is_set():
        input_text = input()

        if currentAlias:
            thisMessage = commandM.fullMessageData(currentUser, currentServer, input_text)
            config.inQ.put(thisMessage)
        else:
            config.promptQ.put(input_text)

def outM():
    while config.running.is_set():
        if not config.outQ.empty():
            output_text = config.outQ.get()
            if output_text:
                print(f'\n{output_text}\n')

def debugM():
    while not shuttingdown:
        if not config.debugQ.empty():
            debug_text = config.debugQ.get()
            if debug_text:
                print(f'\n>>>>>>>>>>>>>>>>>>\n{debug_text}\n<<<<<<<<<<<<<<<<<<\n')

def getTrigger():
    global currentServer

    if currentServer:
        trigger = currentServer.trigger

    else:
        trigger = None

    return trigger

def setUser(userinput):
    global currentUser

    thisUser = DBM.tryGetOneUser(userinput)

    if thisUser:
        currentUser = thisUser
        return currentUser

    else:
        return None

def setServer(userinput):
    global currentServer

    thisServer = DBM.tryGetOneServer(userinput)

    if thisServer:
        currentServer = thisServer
        return currentServer

    else:
        return None

def setAlias():
    global currentAlias

    thisAlias = DBM.getUserAlias(currentUser, currentServer)

    if thisAlias:
        currentAlias = thisAlias
        return currentAlias

    else:
        return None

def clearAll():
    global currentUser
    global currentServer
    global currentAlias

    currentUser = None
    currentServer = None
    currentAlias = None

def login():
    config.outQ.put('User: ')
    userText = config.promptQ.get()

    setUser(userText)

    if currentUser:
        config.outQ.put('Server: ')
        serverText = config.promptQ.get()

        setServer(serverText)

        if currentServer:
            setAlias()

            if currentAlias:
                config.outQ.put(f'Logged in as {currentUser.name} on server {currentServer.name}.')

            else:
                config.outQ.put(f'Error: User {currentUser.name} has no alias on server {currentServer.name}.')
                config.login.clear()

        else:
            config.outQ.put('Error: Server not found!')
            config.login.clear()

    else:
        config.outQ.put('Error: User not found!')
        config.login.clear()

def registerCommands():
    global sessionC
    sessionC = commandM.command('session', mSelf)
    sessionC.description = 'Commands for managing the current login session.'
    sessionC.instruction = 'Specify a parameter.'
    global sessionLogoutC
    sessionLogoutC = commandM.command('logout', sessionC)
    sessionLogoutC.description = 'Logs you out of the current session.'
    sessionLogoutC.function = 'sessionLogoutF'
    global sessionUserC
    sessionUserC = commandM.command('user', sessionC)
    sessionUserC.description = 'Used to alter user settings.'
    sessionUserC.instruction = 'Specify a parameter. By itself displays the current settings.'
    sessionUserC.function = 'sessionUserF'
    global sessionUserNameC
    sessionUserNameC = commandM.command('name', sessionUserC)
    sessionUserNameC.description = 'Used to change the current user\'s name.'
    sessionUserNameC.instruction = 'Specify a new name.'
    sessionUserNameC.function = 'sessionUserNameF'
    global sessionServerC
    sessionServerC = commandM.command('server', sessionC)
    sessionServerC.description = 'Used to alter server settings.'
    sessionServerC.instruction = 'Specify a parameter. By itself displays the current settings.'
    sessionServerC.function = 'sessionServerF'
    global sessionServerTriggerC
    sessionServerTriggerC = commandM.command('trigger', sessionServerC)
    sessionServerTriggerC.description = 'Used to alter the current server\'s trigger.'
    sessionServerTriggerC.instruction = 'Specify a new trigger.'
    sessionServerTriggerC.function = 'sessionServerTriggerF'
    
def sessionLogoutF(inputData):
    config.login.clear()

    config.outQ.put('Logged out!')

def sessionUserF(inputData):
    if inputData.user:
        out_text = ''

        out_text += (f'User {inputData.user.id}:\n')
        out_text += (f'Name: {inputData.user.name}\n')
        out_text += (f'Timezone: {inputData.user.tz}\n')
        out_text += (f'Country: {inputData.user.country}\n')
        out_text += (f'Birthday: {inputData.user.bday}\n')
        out_text += (f'Bot Rank: {inputData.user.botrank}')

        config.outQ.put(out_text)
    else:
        config.outQ.put('No current user!')

def sessionServerF(inputData):
    if inputData.server:
        out_text = ''

        out_text += (f'Server {inputData.server.id}:\n')
        out_text += (f'Name: {inputData.server.name}\n')
        out_text += (f'Timezone: {inputData.server.tz}\n')
        out_text += (f'Trigger: {inputData.server.trigger}')

        config.outQ.put(out_text)
    else:
        config.outQ.put('No current server!')

def sessionServerTriggerF(inputData, content):
    global currentServer
    setTrigger = False

    if len(content) == 1:
        if content[0].lower() == 'none':
            if currentServer.trigger:
                currentServer.trigger = None
                setTrigger = True
                config.outQ.put('Server trigger has been removed.')

            else:
                config.outQ.put('Server trigger is already set to \'None\'')

        else:
            if len(content[0]) < 3:
                if len(content[0]) > 0:
                    currentServer.trigger = content[0]
                    setTrigger = True
                    config.outQ.put(f'Server trigger has been set to {content[0]}')

                else:
                    config.outQ.put('Please specify at least one character for a trigger.')

            else:
                config.outQ.put('Try a shorter trigger.')
    else:
        config.outQ.put('Please limit the trigger to a single character or small group of characters with no whitespace.')

    if setTrigger:
        DBM.updateServer(currentServer)

def terminal():
    try:  
        config.running = multiprocessing.Event() 
        config.running.set()
        config.login = multiprocessing.Event() 
        config.login.clear()
        inThread = threading.Thread(target=inM, daemon=True)
        inThread.start()
        outThread = threading.Thread(target=outM)
        outThread.start()
        debugThread = threading.Thread(target=debugM)
        debugThread.start()
        mailroom = multiprocessing.Process(target=commandM.manage_read_pool)
        mailroom.start()

        while config.running.is_set():
            if currentAlias:
                if config.login.is_set():
                    time.sleep(0.5)
                else:
                    clearAll()

            else:
                if config.login.is_set():
                    login()

                else:
                    config.outQ.put('Welcome to testBot! Please choose login or exit.')

                    menuChoice = config.promptQ.get()

                    if menuChoice.lower() == 'login':
                        config.login.set()

                    elif menuChoice.lower() == 'exit':
                        contrigM.shutdownF()

                    else:
                        config.outQ.put('Unknown command!')

    except KeyboardInterrupt:
        if config.running.is_set():
            contrigM.moduleCleanup()

    finally:
        if config.running.is_set():
            contrigM.moduleCleanup()

        config.debugQ.put('Closing message queues...')
        config.inQ.close()
        config.inQ.join_thread()
        config.promptQ.close()
        config.promptQ.join_thread()
        outThread.join(timeout=1)
        config.outQ.close()
        config.outQ.join_thread()
        while not config.debugQ.empty():
            time.sleep(0.5)

        global shuttingdown
        shuttingdown = True
        debugThread.join(timeout=1)
        config.debugQ.close()
        config.debugQ.join_thread()

        mailroom.join(timeout=1)

        sys.exit()

if __name__ == "__main__":
    registerCommands()
    shuttingdown = False
    terminal()

else:
    print('An offline, multiuser and (simulated) multiserver session manager. Run as main.')
