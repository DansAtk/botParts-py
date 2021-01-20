# A test bot module that repeats an input phrase in different ways.

import sys
import config
import commands

def init():
    say = commands.command('say', __name__)
    includes.update({say.name : say})
    say.description = "repeats the input text."
    say.function = 'say'

    say.parameters.update({'quietly' : commands.command('quietly', __name__)})
    say.parameters.update({'loudly' : commands.command('loudly', __name__)})

    say.parameters['quietly'].function = 'quietly'
    say.parameters['quietly'].description = "quietly says things"
    say.parameters['loudly'].function = 'loudly'
    say.parameters['loudly'].description = "shouts things in all caps"

def say(message):
    fullMessage = ' '.join(message)
    print(fullMessage)

def loudly(message):
    fullMessage = ' '.join(message)
    print(fullMessage.upper())

def quietly(message):
    fullMessage = ' '.join(message)
    print(fullMessage.lower())

if __name__ == "__main__":
    print("saymodule is in control.")
    init()
else:
    config.imported.append('saymodule')
    includes = {}
    init()
