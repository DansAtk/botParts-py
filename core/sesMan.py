import sys

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

def login():
    userText = input('User: ')

    setUser(userText)

    if currentUser:
        serverText = input('Server: ')

        setServer(serverText)

        if currentServer:
            setAlias()

            if currentAlias:
                print('\nLogged in as {} on server {}.\n'.format(currentUser.name, currentServer.name))

            else:
                print('\nError: User {} has no alias on server {}.\n'.format(currentUser.name, currentServer.name))

        else:
            print('\nError: Server not found!\n')

    else:
        print('\nError: User not found!\n')

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
    
def sessionLogoutF():
    global currentUser
    global currentServer
    global currentAlias

    currentUser = None
    currentServer = None
    currentAlias = None

    print('\nLogged out!\n\n\n')

def serverF():
    global currentServer

    if currentServer:
        print('Server {}:'.format(currentServer.id))
        print('Name: {}'.format(currentServer.name))
        print('Timezone: {}'.format(currentServer.tz))
        print('Trigger: {}'.format(currentServer.trigger))

def serverTriggerF(userinput):
    global currentServer
    setTrigger = False

    if len(userinput) == 1:
        if userinput[0].lower() == 'none':
            if currentServer.trigger:
                currentServer.trigger = None
                setTrigger = True
                print('Server trigger has been removed.')

            else:
                print('Server trigger is already set to \'None\'')

        else:
            if len(userinput[0]) < 3:
                if len(userinput[0]) > 0:
                    currentServer.trigger = userinput[0]
                    setTrigger = True
                    print('Server trigger has been set to {}'.format(userinput[0]))

                else:
                    print('Please specify at least one character for a trigger.')

            else:
                print('Try a shorter trigger.')
    else:
        print('Please limit the trigger to a single character or small group of characters with no whitespace.')

    if setTrigger:
        DBM.updateServer(currentServer)

if __name__ == "__main__":
    print('An offline, multiuser and (simulated) multiserver session manager. No main.')
else:
    registerCommands()
