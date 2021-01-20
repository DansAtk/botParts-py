# A test bot module that repeats an input phrase in different ways.

import sys
import config
import commandsmodule

say = commandsmodule.command('say', __name__)

def init():
    includes.update({say.name : say})
    say.description = "Repeats the input text."
    say.function = 'sayF'

    say.parameters.update({'quietly' : commandsmodule.command('quietly', __name__)})
    say.parameters.update({'loudly' : commandsmodule.command('loudly', __name__)})

    say.parameters['quietly'].function = 'quietlyF'
    say.parameters['quietly'].description = "Quietly says things."
    say.parameters['loudly'].function = 'loudlyF'
    say.parameters['loudly'].description = "Shouts things in all caps."

def sayF(message):
    fullMessage = ' '.join(message)
    print(fullMessage)

def loudlyF(message):
    fullMessage = ' '.join(message)
    print(fullMessage.upper())

def quietlyF(message):
    fullMessage = ' '.join(message)
    print(fullMessage.lower())

if __name__ == "__main__":
    print("saymodule is in control.")
    init()
else:
    config.imported.append('saymodule')
    includes = {}
    init()
