import sys
import random

from core import config
from core.commandM import command, imports
from core import DBM

mSelf = sys.modules[__name__]
includes = {}

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
    imports.update({__name__ : includes})

def sayF(inputData, content):
    if content[0].startswith('"') and content[0].endswith('"'):
        #print(f'{content[0][1:-1]}\n')
        config.outQ.put(f'{content[0][1:-1]}')
    else:
        #print(f'{sayC.howto()}\n')
        config.outQ.put(f'{sayC.howto()}')

def sayQuietlyF(inputData, content):
    if content[0].startswith('"') and content[0].endswith('"'):
        config.outQ.put(f'{content[0][1:-1].lower()}')
        #print(f'{content[0][1:-1].lower()}\n')
    else:
        #print(f'{sayQuietlyC.howto()}\n')
        config.outQ.put(f'{sayQuietlyC.howto()}')

def sayLoudlyF(inputData, content):
    if content[0].startswith('"') and content[0].endswith('"'):
        #print(f'{content[0][1:-1].upper()}\n')
        config.outQ.put(f'{content[0][1:-1].upper()}')
    else:
        #print(f'{sayLoudlyC.howto()}\n')
        config.outQ.put(f'{sayLoudlyC.howto()}')

def sayRobotF(inputData, content):
    if content[0].startswith('"') and content[0].endswith('"'):
        inputText = ' '.join(content[0][1:-1])
        roboText = (''.join(format(ord(x), '08b') for x in inputText))
        #print(f'{roboText}\n')
        config.outQ.put(f'{roboText}')

    else:
        #print(f'{sayRobotC.howto()}\n')
        config.outQ.put(f'{sayRobotC.howto()}')

if __name__ == "__main__":
    print('A module for repeating the user\'s input message in various formats. No main.')
else:
    registerCommands()
