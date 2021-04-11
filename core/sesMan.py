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
        trigger = currentserver.trigger

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

def registerCommands():
    global sessionC
    sessionC = command('session', mSelf)
    sessionC.description = 'Commands for managing the current simulated login session.'
    sessionC.instruction = 'Specify a parameter.'
    global sessionLogoutC
    sessionLogoutC = command('logout', sessionC)
    sessionLogoutC.description = 'Logs you out of the current session.'
    sessionLogoutC.function = 'sessionLogoutF'
    
def sessionLogoutF():
    global currentUser
    global currentServer
    global currentAlias

    currentUser = None
    currentServer = None
    currentAlias = None

if __name__ == "__main__":
    print('An offline, multiuser and (simulated) multiserver session manager. No main.')
else:
    registerCommands()
