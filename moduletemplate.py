import config
import commandsmodule

includes = {}

commandtemplate = commandsmodule.command('commandtemplate', __name__)

def init():
    config.imports.append('ref.moduletemplate')
    includes.update({commandtemplate.name : commandtemplate})
    commandtemplate.description = "A template for a new command."
    commandtemplate.function = 'commandtemplateF'
    commandtemplate.parameters.update({'parametertemplate' : 
        commandsmodule.command('parametertemplate', __name__)})
    commandtemplate.parameters['parametertemplate'].description = (
        "A template for a new command.")
    commandtemplate.parameters['parametertemplate'].function = (
        'parametertemplateF')
    print("Imported moduletemplate.")

def commandtemplateF(message):
    if len(message) > 0:
        print(commandtemplate.paramError(message))
    else:
        print("A template for a new command's function. Should expect the " +
        "remainder of the typed command as an argument.")

def parametertemplateF(message):
    if len(message) > 0:
        print(commandtemplate.parameters['parametertemplate'].paramError(message))
    else:
        print("A template for a new parameter's function. Should expect the " +
        "remainder of the typed command as an argument.")

if __name__ == "__main__":
    print("No main.")
else:
    init()
