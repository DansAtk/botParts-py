import sys

import config
import commandsmodule

includes = {}

exit = commandsmodule.command('exit', __name__)

def init():
    includes.update({exit.name : exit})
    exit.description = "Closes the bot gracefully."
    exit.function = 'exitF'
    includes.update({'quit' : exit})
    config.imports.append('controlmodule')

def exitF(message):
    for module in config.imports:
        if hasattr(sys.modules[module], 'cleanup'):
            sys.modules[module].cleanup()
    sys.exit()

if __name__ == "__main__":
    print("No main.")
else:
    init()
