import sys

import config
import commandsmodule

includes = {}

exit = commandsmodule.command('exit', __name__)

def init():
    includes.update({exit.name : exit})
    exit.description = "Closes the bot gracefully."
    exit.function = 'exitF'
    config.imported.append('controlmodule')

def exitF(message):
    sys.exit()

if __name__ == "__main__":
    print("No main.")
else:
    init()