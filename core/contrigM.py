import sys
import json

from core import config
from core.commandM import command

mSelf = sys.modules[__name__]
includes = {}
config.imports.append(__name__)

def registerCommands():
    global pushC
    pushC = command('push', mSelf)
    pushC.description = 'Pushes the current default settings to a file to make it persistent.'
    pushC.function = 'pushF'
    global pullC
    pullC = command('pull', mSelf)
    pullC.description = 'Pulls the persistent settings from a file.'
    pullC.function = 'pullF'
    global defaultC
    defaultC = command('default', mSelf)
    defaultC.description = 'Used to alter default settings.'
    defaultC.instruction = 'Specify a parameter. By itself displays the current settings.'
    defaultC.function = 'defaultF'
    global defaultTriggerC
    defaultTriggerC = command('trigger', defaultC)
    defaultTriggerC.description = 'Used to alter the default trigger.'
    defaultTriggerC.instruction = 'Specify a new trigger.'
    defaultTriggerC.function = 'defaultTriggerF'
    global shutdownC
    shutdownC = command('shutdown', mSelf)
    shutdownC.description = 'Closes the bot gracefully.'
    shutdownC.function = 'shutdownF'
    includes.update({'exit' : shutdownC})
    includes.update({'quit' : shutdownC})

def pushF():
    print('Pushing config to file...')
    try:
        with open(config.conFile, 'w') as conf:
            json.dump(config.settings, conf)
        print('Success!')
    except:
        print('Failure!')

def pullF():
    print('Pulling config from file...')
    try:
        with open(config.conFile, 'r') as conf:
            config.settings = json.load(conf)
        print('Success!')
    except FileNotFoundError:
        print('No config file found!')

def defaultTriggerF(userinput):
    if len(userinput) == 1:
        if userinput[0].lower() == 'none':
            try:
                del config.settings['trigger']
                print('Trigger has been removed.')

            except KeyError:
                print('Trigger is already set to \'None\'')

        else:
            if len(userinput[0]) < 3:
                if len(userinput[0]) > 0:
                    config.settings['trigger'] = userinput[0]
                    print('Trigger has been set to {}'.format(userinput[0]))

                else:
                    print('Please specify at least one character for a trigger.')

            else:
                print('Try a shorter trigger.')
    else:
        print('Please limit the trigger to a single character or small group of characters with no whitespace.')

def shutdownF():
    sys.exit()

def moduleCleanup():
    print('Beginning cleanup...')
    for module in config.imports:
        if hasattr(sys.modules[module], 'cleanup'):
            sys.modules[module].cleanup()
    print('Done!')

def cleanup():
    pushF()

if __name__ == "__main__":
    print('For controlling bot state and configuration, and handling graceful startup and shutdown. No main.')
else:
    registerCommands()
    pullF()
