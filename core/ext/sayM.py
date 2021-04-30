import sys
import random

import config
from core.commands import command
from core import users
from core import places

mSelf = sys.modules[__name__]
includes = {}
config.register(mSelf)

def registerCommands():
    global sayC
    sayC = command('say', mSelf)
    sayC.description = 'Repeats the input text.'
    sayC.instruction = 'Specify a message surrounded by quotes (""). ' \
            'Add parameters to change how the message is presented. ' \
            'Enter a term without quotes to pull a related saved quote ' \
            'from the database.'
    sayC.function = 'sayF'
    global sayQuietlyC
    sayQuietlyC = command('quietly', sayC)
    sayQuietlyC.description = 'Quietly repeats a message in all lowercase.'
    sayQuietlyC.instruction = 'Specify a message surrounded by quotes (""). ' \
            'Enter a term without quotes to pull a related saved quote ' \
            'from the database.'
    sayQuietlyC.function = 'sayQuietlyF'
    global sayLoudlyC
    sayLoudlyC = command('loudly', sayC)
    sayLoudlyC.description = 'Shouts a message in all caps.'
    sayLoudlyC.instruction = 'Specify a message surrounded by quotes (""). ' \
            'Enter a term without quotes to pull a related saved quote ' \
            'from the database.'
    sayLoudlyC.function = 'sayLoudlyF'
    global sayRobotC
    sayRobotC = command('robot', sayC)
    sayRobotC.description = 'Translates a message to binary.'
    sayRobotC.instruction = 'Specify a message surrounded by quotes (""). ' \
            'Enter a term without quotes to pull a related saved quote ' \
            'from the database.'
    sayRobotC.function = 'sayRobotF'

def sayF(inputData, content):
    if content[0].startswith('"') and content[0].endswith('"'):
        config.outQ.put(f'{content[0][1:-1]}')
    else:
        config.outQ.put(f'{sayC.howto()}')

def sayQuietlyF(inputData, content):
    if content[0].startswith('"') and content[0].endswith('"'):
        config.outQ.put(f'{content[0][1:-1].lower()}')
    else:
        config.outQ.put(f'{sayQuietlyC.howto()}')

def sayLoudlyF(inputData, content):
    if content[0].startswith('"') and content[0].endswith('"'):
        config.outQ.put(f'{content[0][1:-1].upper()}')
    else:
        config.outQ.put(f'{sayLoudlyC.howto()}')

def sayRobotF(inputData, content):
    if content[0].startswith('"') and content[0].endswith('"'):
        inputText = ' '.join(content[0][1:-1])
        roboText = (''.join(format(ord(x), '08b') for x in inputText))
        config.outQ.put(f'{roboText}')

    else:
        config.outQ.put(f'{sayRobotC.howto()}')

if __name__ == "__main__":
    print('A module for repeating the user\'s input message in various formats. No main.')
else:
    registerCommands()
