import sys

import config
import commands

includes = {}

def init():
    exit = commands.command('exit', __name__)
    includes.update({exit.name : exit})
    exit.description = "Closes the bot gracefully."
    exit.function = 'exitF'
    config.imported.append('controlmodule')

def exitF(message):
    sys.exit()

if __name__ == "__main__":
    main()
else:
    init()
