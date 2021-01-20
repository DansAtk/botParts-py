import sys
import json

import commandsmodule
import config

includes = {}

change = commandsmodule.command('change', __name__)
push = commandsmodule.command('push', __name__)
pull = commandsmodule.command('pull', __name__)

def init():
    print("Startup config.\n")
    pullF()
    includes.update({push.name : push, pull.name : pull, change.name : change})
    push.description = "Pushes the current config to a file to make it persistent."
    push.function = 'pushF'
    pull.description = "Pulls the saved config from file."
    pull.function = 'pullF'
    change.description = "Used to alter bot system variables. Usable by admins only."
    change.function = 'changeF'
    change.parameters.update({'trigger' : commandsmodule.command('trigger', __name__)})
    change.parameters['trigger'].description = "Set the command trigger to a different set of characters."
    change.parameters['trigger'].function = 'triggerF'
    config.imports.append('configmodule')

def cleanUp():
    print("Saving config...")
    pushF()
    print("done!")

def pushF(message = ""):
    print("Pushing config to file.")
    try:
        with open("./conf.json", 'w') as conf:
            json.dump(config.settings, conf)
        print("Success!")
    except:
        print("Failure!")

def pullF(message = ""):
    print("Pulling config from file...")
    try:
        with open("./conf.json", 'r') as conf:
            config.settings = json.load(conf)
        print("Success!")
    except FileNotFoundError:
        print("No config file found!")

def changeF(message):
    print("Please specify a parameter. Available parameters: " + ', '.join(change.parameters) + ", help.")
    
def triggerF(message):
    if len(message) == 1:
        if len(message[0]) < 3:
            config.settings['trigger'] = message[0]
        else:
            print("Try a shorter trigger.")
    else:
        print("Please limit the trigger to a single character or small group of characters.")

if __name__ == "__main__":
    print("No main.")
else:
    init()
