import commandsmodule
import config

includes = {}

change = commandsmodule.command('change', __name__)

def init():
    includes.update({change.name : change})
    change.description = "Used to alter bot system variables. Usable by admins only."
    change.function = 'changeF'
    change.parameters.update({'trigger' : commandsmodule.command('trigger', __name__)})
    change.parameters['trigger'].description = "Set the command trigger to a different set of characters."
    change.parameters['trigger'].function = 'triggerF'
    config.imported.append('configmodule')

def changeF(message):
    print("Please specify a parameter. Available parameters: " + ', '.join(change.parameters) + ", help.")
    
def triggerF(message):
    if len(message) == 1:
        if len(message[0]) < 3:
            config.trigger = message[0]
        else:
            print("Try a shorter trigger.")
    else:
        print("Please limit the trigger to a single character or small group of characters.")

if __name__ == "__main__":
    print("No main.")
else:
    init()
