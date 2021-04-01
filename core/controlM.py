import sys
import config
from commandM import command

mSelf = sys.modules[__name__]
includes = {}
config.imports.append('controlM')

def init():
    shutdownC = command('shutdown', mSelf)
    shutdownC.description = 'Closes the bot gracefully.'
    shutdownC.function = 'shutdownF'
    includes.update({'exit' : shutdownC})
    includes.update({'quit' : shutdownC})

def shutdownF():
    sys.exit()

def moduleCleanup():
    print('Beginning cleanup...')
    for module in config.imports:
        if hasattr(sys.modules[module], 'cleanup'):
            sys.modules[module].cleanup()
    print('Done!')

if __name__ == "__main__":
    print('For controlling bot state, handling graceful startup and shutdown. No main.')
else:
    init()
