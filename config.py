import sys
import pathlib

inQ = None
outQ = None
debugQ = None
promptQ = None

interface = 'basic'
running = None

settings = {'dbversion' : '0.5'}
imports = {'core' : {}, 'core-ext' : {}, 'interface' : {}, 'interface-ext' : {}}
signals = {}

# Paths
backupPath = pathlib.Path.cwd() / 'backup'
dataPath = pathlib.Path.cwd() / 'data'
conFile = pathlib.Path.cwd() / 'conf.json'
database = dataPath / 'unified.db'

def register(thisModule):
    modulePath = thisModule.__name__.split('.')
    if len(modulePath) > 1:
        if modulePath[0] == 'core':
            if len(modulePath) > 2:
                if modulePath[1] == 'ext':
                    imports['core-ext'].update({thisModule.__name__ : thisModule.includes})
            else:
                imports['core'].update({thisModule.__name__ : thisModule.includes})

        elif modulePath[0] == 'interface':
            if len(modulePath) > 3:
                if modulePath[2] == 'ext':
                    imports['interface-ext'].update({thisModule.__name__ : thisModule.includes})
            elif len(modulePath) > 2:
                imports['interface'].update({thisModule.__name__ : thisModule.includes})

if __name__ == "__main__":
    print("No main.")
