import sys
import config
from commandM import command

mSelf = sys.modules[__name__]
includes = {}
config.imports.append('sayM')

def init():
    sayC = command('say', mSelf)
    sayC.description = 'Repeats the input text.'
    sayC.function = 'sayF'

    quietlyC = command('quietly', sayC)
    quietlyC.description = 'Quietly says things in all lowercase.'
    quietlyC.function = 'quietlyF'
    loudlyC = command('loudly', sayC)
    loudlyC.description = 'Shouts things in all caps.'
    loudlyC.function = 'loudlyF'

def sayF(userinput):
    print(' '.join(userinput))

def quietlyF(userinput):
    print((' '.join(userinput)).lower())

def loudlyF(userinput):
    print((' '.join(userinput)).upper())

if __name__ == "__main__":
    print('A module for repeating the user\'s input message in various formats. No main.')
else:
    init()
