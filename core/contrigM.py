import sys
import multiprocessing
import time
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

def pushF(inputData=None):
    config.debugQ.put('Pushing config to file...')
    try:
        with open(config.conFile, 'w') as conf:
            json.dump(config.settings, conf)
        config.debugQ.put('Success!')
    except:
        config.debugQ.put('Failure!')

def pullF(inputData=None):
    config.debugQ.put('Pulling config from file...')
    try:
        with open(config.conFile, 'r') as conf:
            config.settings = json.load(conf)
        config.debugQ.put('Success!')
    except FileNotFoundError:
        config.debugQ.put('No config file found!')

def defaultTriggerF(inputData, content):
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

def shutdownF(inputData=None):
    moduleCleanup()

def moduleCleanup():
    config.debugQ.put('Cleaning up modules...')

    for module in config.imports:
        if hasattr(sys.modules[module], 'cleanup'):
            sys.modules[module].cleanup()

    config.running.clear()

def cleanup():
    pushF()

if __name__ == "__main__":
    print('For controlling bot state and configuration, and handling graceful startup and shutdown. No main.')
else:
    registerCommands()
    pullF()
