import sys
import multiprocessing
import threading
import time

import config
from core import users
from core import places
from core.commands import command, fullMessageData, manage_read_pool
from core import utils

config.inQ = multiprocessing.Queue()
config.outQ = multiprocessing.Queue()
config.debugQ = multiprocessing.Queue()
config.promptQ = multiprocessing.Queue()

mSelf = sys.modules[__name__]
includes = {}
config.register(mSelf)
        

currentUser = None
currentPlace = None

def inM():
    message_id = 0
    while config.running.is_set():
        input_text = input()

        message_id += 1

        if currentUser and currentPlace:
            thisMessage = fullMessageData(message_id, currentUser, currentPlace, input_text)
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
    while not config.signals['shuttingdown'].is_set():
        if not config.debugQ.empty():
            debug_text = config.debugQ.get()
            if debug_text:
                print(f'\n>>>>>>>>>>>>>>>>>>\n{debug_text}\n<<<<<<<<<<<<<<<<<<\n')

def getTrigger():
    global currentPlace

    if currentPlace:
        trigger = currentPlace.trigger

    else:
        trigger = None

    return trigger

def setUser(userinput):
    global currentUser

    thisUser = users.tryGetOneUser(userinput)

    if thisUser:
        currentUser = thisUser
        return currentUser

    else:
        return None

def setPlace(userinput):
    global currentPlace

    thisPlace = places.tryGetOnePlace(userinput)

    if thisPlace:
        currentPlace = thisPlace
        return currentPlace

    else:
        return None

def clearAll():
    global currentUser
    global currentPlace

    currentUser = None
    currentPlace = None

def login():
    config.outQ.put('User: ')
    userText = config.promptQ.get()

    setUser(userText)

    if currentUser:
        config.outQ.put('Place: ')
        placeText = config.promptQ.get()

        setPlace(placeText)

        if currentPlace:
            config.outQ.put(f'Logged in as {currentUser.name} on place {currentPlace.name}.')

        else:
            config.outQ.put('Error: Place not found!')
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
    global sessionUserC
    sessionUserC = command('user', sessionC)
    sessionUserC.description = 'Used to alter user settings.'
    sessionUserC.instruction = 'Specify a parameter. By itself displays the current settings.'
    sessionUserC.function = 'sessionUserF'
    global sessionUserNameC
    sessionUserNameC = command('name', sessionUserC)
    sessionUserNameC.description = 'Used to change the current user\'s name.'
    sessionUserNameC.instruction = 'Specify a new name.'
    sessionUserNameC.function = 'sessionUserNameF'
    global sessionPlaceC
    sessionPlaceC = command('place', sessionC)
    sessionPlaceC.description = 'Used to alter place settings.'
    sessionPlaceC.instruction = 'Specify a parameter. By itself displays the current settings.'
    sessionPlaceC.function = 'sessionPlaceF'
    global sessionPlaceTriggerC
    sessionPlaceTriggerC = command('trigger', sessionPlaceC)
    sessionPlaceTriggerC.description = 'Used to alter the current place\'s trigger.'
    sessionPlaceTriggerC.instruction = 'Specify a new trigger.'
    sessionPlaceTriggerC.function = 'sessionPlaceTriggerF'
    
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

def sessionPlaceF(inputData):
    if inputData.place:
        out_text = ''

        out_text += (f'Place {inputData.place.id}:\n')
        out_text += (f'Name: {inputData.place.name}\n')
        out_text += (f'Timezone: {inputData.place.tz}\n')
        out_text += (f'Trigger: {inputData.place.trigger}')

        config.outQ.put(out_text)
    else:
        config.outQ.put('No current place!')

def sessionPlaceTriggerF(inputData, content):
    global currentPlace
    setTrigger = False

    if len(content) == 1:
        if content[0].lower() == 'none':
            if currentPlace.trigger:
                currentPlace.trigger = None
                setTrigger = True
                config.outQ.put('Place trigger has been removed.')

            else:
                config.outQ.put('Place trigger is already set to \'None\'')

        else:
            if len(content[0]) < 3:
                if len(content[0]) > 0:
                    currentPlace.trigger = content[0]
                    setTrigger = True
                    config.outQ.put(f'Place trigger has been set to {content[0]}')

                else:
                    config.outQ.put('Please specify at least one character for a trigger.')

            else:
                config.outQ.put('Try a shorter trigger.')
    else:
        config.outQ.put('Please limit the trigger to a single character or small group of characters with no whitespace.')

    if setTrigger:
        places.updatePlace(currentPlace)

def start():
    try:  
        registerCommands()
        config.running = multiprocessing.Event() 
        config.running.set()
        config.signals.update({'login' : multiprocessing.Event()})
        config.signals['login'].clear()
        config.signals.update({'shuttingdown' : multiprocessing.Event()})
        config.signals['shuttingdown'].clear()
        inThread = threading.Thread(target=inM, daemon=True)
        inThread.start()
        outThread = threading.Thread(target=outM)
        outThread.start()
        debugThread = threading.Thread(target=debugM)
        debugThread.start()
        mailroom = multiprocessing.Process(target=manage_read_pool)
        mailroom.start()

        while config.running.is_set():
            if currentUser and currentPlace:
                if config.signals['login'].is_set():
                    time.sleep(0.5)
                else:
                    clearAll()

            else:
                if config.signals['login'].is_set():
                    login()

                else:
                    config.outQ.put('Welcome to testBot! Please choose login or exit.')

                    menuChoice = config.promptQ.get()

                    if menuChoice.lower() == 'login':
                        config.signals['login'].set()

                    elif menuChoice.lower() == 'exit':
                        util.shutdownF()

                    else:
                        config.outQ.put('Unknown command!')

    except KeyboardInterrupt:
        if config.running.is_set():
            utils.moduleCleanup()

    finally:
        if config.running:
            if config.running.is_set():
                utils.moduleCleanup()

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

        config.signals['shuttingdown'].set()
        debugThread.join(timeout=1)
        config.debugQ.close()
        config.debugQ.join_thread()

        mailroom.join(timeout=1)

        sys.exit()

if __name__ == "__main__":
    print('An offline, multiuser and (simulated) multiserver session managing interface. No main.')
