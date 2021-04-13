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

def sayF(userinput):
    if userinput[0].startswith('"') and userinput[0].endswith('"'):
        print(userinput[0][1:-1])
    else:
        print(sayC.howto())

def sayQuietlyF(userinput):
    if userinput[0].startswith('"') and userinput[0].endswith('"'):
        print(userinput[0][1:-1].lower())
    else:
        print(sayQuietlyC.howto())

def sayLoudlyF(userinput):
    if userinput[0].startswith('"') and userinput[0].endswith('"'):
        print(userinput[0][1:-1].upper())
    else:
        print(sayLoudlyC.howto())

def sayRobotF(userinput):
    if userinput[0].startswith('"') and userinput[0].endswith('"'):
        inputText = ' '.join(userinput[0][1:-1])
        roboText = (''.join(format(ord(x), '08b') for x in inputText))
        print(f'\n{roboText}\n')
    else:
        print(sayRobotC.howto())

if __name__ == "__main__":
    print('A module for repeating the user\'s input message in various formats. No main.')
else:
    registerCommands()
