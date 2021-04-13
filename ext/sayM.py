import sys
import random

from core import config
from core.commandM import command
from core import DBM

mSelf = sys.modules[__name__]
includes = {}
config.imports.append(__name__)

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
        print(f'{content[0][1:-1]}\n')
    else:
        print(f'{sayC.howto()}\n')

def sayQuietlyF(inputData, content):
    if content[0].startswith('"') and content[0].endswith('"'):
        print(f'{content[0][1:-1].lower()}\n')
    else:
        print(f'{sayQuietlyC.howto()}\n')

def sayLoudlyF(inputData, content):
    if content[0].startswith('"') and content[0].endswith('"'):
        print(f'{content[0][1:-1].upper()}\n')
    else:
        print(f'{sayLoudlyC.howto()}\n')

def sayRobotF(inputData, content):
    if content[0].startswith('"') and content[0].endswith('"'):
        inputText = ' '.join(content[0][1:-1])
        roboText = (''.join(format(ord(x), '08b') for x in inputText))
        print(f'{roboText}\n')
    else:
        print(f'{sayRobotC.howto()}\n')

if __name__ == "__main__":
    print('A module for repeating the user\'s input message in various formats. No main.')
else:
    registerCommands()
