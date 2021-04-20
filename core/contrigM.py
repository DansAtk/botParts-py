import sys
import multiprocessing
import time
import json

from core import config
from core.commandM import command, imports

mSelf = sys.modules[__name__]
includes = {}

def registerCommands():
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
    imports.update({__name__ : includes})

def botConfigPushF(inputData=None):
    config.debugQ.put('Pushing config to file...')
    try:
        with open(config.conFile, 'w') as conf:
            json.dump(config.settings, conf)
        config.debugQ.put('Success!')
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

    for module in imports:
        if hasattr(sys.modules[module], 'cleanup'):
            sys.modules[module].cleanup()

    config.running.clear()

def cleanup():
    botConfigPushF()

if __name__ == "__main__":
    print('For controlling bot state and configuration, and handling graceful startup and shutdown. No main.')
else:
    registerCommands()
    botConfigPullF()
