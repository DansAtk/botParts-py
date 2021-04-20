import sys
import random
import time
import threading

from core import config
from core.commandM import command, imports, temp_commands
from core import DBM

mSelf = sys.modules[__name__]
includes = {}
gamerun = False

def run_game(inputData):
    global gamerun
    gamerun = True
    gameCommands = {}
    global biteC
    biteC = command('bite', mSelf, gameCommands)
    biteC.description = 'Bites.'
    biteC.function = 'biteF'
    global stopC
    stopC = command('stop', mSelf, gameCommands)
    stopC.description = 'Bites.'
    stopC.function = 'stopF'

    dropster = threading.Thread(target=dropper, daemon=True)
    dropster.start()

    temp_commands(inputData, __name__, gameCommands, filter_user=True, filter_channel=True)

    while gamerun == True:
        time.sleep(1)

    dropster.join(timeout=5)

def stopF(inputData):
    global gamerun
    gamerun = False

def biteF(inputData):
    config.outQ.put('YOu are biting!')

def dropper():
    global gamerun
    while gamerun:
        time.sleep(5)
        config.outQ.put('Dropped something.')

def registerCommands():
    global startC
    startC = command('start', mSelf)
    startC.description = 'Starts the game.'
    startC.function = 'run_game'
    imports.update({__name__ : includes})

if __name__ == "__main__":
    print('A zombie game. No main.')
else:
    registerCommands()
