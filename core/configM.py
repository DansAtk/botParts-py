import json

from commandM import command
import sys
import config

mSelf = sys.modules[__name__]
includes = {}
config.imports.append('configM')

def init():
    pushC = command('push', mSelf)
    pullC = command('pull', mSelf)
    changeC = command('change', mSelf)

    pushC.description = 'Pushes the current config to a file to make it persistent.'
    pullC.description = 'Pulls the persistent config from a file.'
    changeC.description = 'Used to alter config variables.'
    pushC.function = 'pushF'
    pullC.function = 'pullF'
    changeC.function = 'changeF'

    pullF()

def pushF():
    print('Pushing config to file...')
    try:
        with open('./conf.json', 'w') as conf:
            json.dump(config.settings, conf)
        print('Success!')
    except:
        print('Failure!')

def pullF():
    print('Pulling config from file...')
    try:
        with open('./conf.json', 'r') as conf:
            config.settings = json.load(conf)
        print('Success!')
    except FileNotFoundError:
        print('No config file found!')

def changeF(userinput):
    print(changeC.paramError(userinput))

def triggerF(userinput):
    if len(message) == 1:
        if len(message[0]) < 3:
            config.settings['trigger'] = message[0]
        else:
            print('Try a shorter trigger.')
    else:
        print('Please limit the trigger to a single character or small group of characters with no whitespace.')

def cleanup():
    pushF()

if __name__ == "__main__":
    print("Bot configuration management utilities. No main.")
else:
    init()
