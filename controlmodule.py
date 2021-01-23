import sys

import config
import commandsmodule

includes = {}

exit = commandsmodule.command('exit', __name__)
quit = commandsmodule.command('quit', __name__)

def init():
    includes.update({exit.name : exit})
    exit.description = "Closes the bot gracefully."
    exit.function = 'exitF'
    includes.update({quit.name : quit})
    quit.description = "Closes the bot gracefully."
    quit.function = 'exitF'
    config.imports.append('controlmodule')

def exitF(message):
    sys.exit()

if __name__ == "__main__":
    print("No main.")
else:
    init()
