import sys
import time
from core import config
from core.commandM import command
from core import DBM

mSelf = sys.modules[__name__]
includes = {}
config.imports.append(__name__)

currentUser = None
currentServer = None
currentAlias = None

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
    time.sleep(0.5)
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
    sessionC = command('session', mSelf)
    sessionC.description = 'Commands for managing the current login session.'
    sessionC.instruction = 'Specify a parameter.'
    global sessionLogoutC
    sessionLogoutC = command('logout', sessionC)
    sessionLogoutC.description = 'Logs you out of the current session.'
    sessionLogoutC.function = 'sessionLogoutF'
    global userC
    userC = command('user', mSelf)
    userC.description = 'Used to alter user settings.'
    userC.instruction = 'Specify a parameter. By itself displays the current settings.'
    userC.function = 'userF'
    global userNameC
    userNameC = command('name', userC)
    userNameC.description = 'Used to change the current user\'s name.'
    userNameC.instruction = 'Specify a new name.'
    userNameC.function = 'userNameF'
    global serverC
    serverC = command('server', mSelf)
    serverC.description = 'Used to alter server settings.'
    serverC.instruction = 'Specify a parameter. By itself displays the current settings.'
    serverC.function = 'serverF'
    global serverTriggerC
    serverTriggerC = command('trigger', serverC)
    serverTriggerC.description = 'Used to alter the current server\'s trigger.'
    serverTriggerC.instruction = 'Specify a new trigger.'
    serverTriggerC.function = 'serverTriggerF'
    
def sessionLogoutF(inputData):
    config.login.clear()

    config.outQ.put('Logged out!')

def serverF(inputData):
    global currentServer

    if currentServer:
        out_text = ''

        out_text += (f'Server {currentServer.id}:\n')
        out_text += (f'Name: {currentServer.name}\n')
        out_text += (f'Timezone: {currentServer.tz}\n')
        out_text += (f'Trigger: {currentServer.trigger}')

        config.outQ.put(out_text)

def serverTriggerF(inputData, content):
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

if __name__ == "__main__":
    print('An offline, multiuser and (simulated) multiserver session manager. No main.')
else:
    registerCommands()
