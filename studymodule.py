# A test bot module to utilize the commands module.

import config
import commandsmodule

includes = {}

study = commandsmodule.command('study', __name__)

def init():
    includes.update({study.name : study})
    study.description = "A command for tracking and monitoring study habits."
    study.function = 'studyF'

    study.parameters.update({'log' : commandsmodule.command('log', __name__)})
    study.parameters['log'].parameters.update({'mark' : commandsmodule.command('mark', __name__)})
    study.parameters['log'].parameters.update({'unmark' : commandsmodule.command('unmark', __name__)})
    study.parameters['log'].parameters.update({'check' : commandsmodule.command('check', __name__)})

    study.parameters['log'].function = 'logF'
    study.parameters['log'].description = "Allows manipulation of tracked study sessions."
    study.parameters['log'].parameters['mark'].function = 'markF'
    study.parameters['log'].parameters['mark'].description = "Marks you as having studied for the day."
    study.parameters['log'].parameters['unmark'].function = 'unmarkF'
    study.parameters['log'].parameters['unmark'].description = "Unmarks you as having studied for the day."
    study.parameters['log'].parameters['check'].function = 'checkF'
    study.parameters['log'].parameters['check'].description = "Returns whether there is a study log for the current day."

def studyF(message):
    print("Please specify a parameter. Available parameters: " + ', '.join(study.parameters) + ", help.")

def markF(message):
    print(study.parameters['log'].parameters['mark'].description)

def unmarkF(message):
    print(study.parameters['log'].parameters['unmark'].description)

def checkF(message):
    print(study.parameters['log'].parameters['check'].description)

def logF(message):
    print("Please specify a parameter. Available parameters: " + ', '.join(study.parameters['log'].parameters) + ", help.")

if __name__ == "__main__":
    print("This is the study module.")
    init()
else:
    config.imported.append('studymodule')
    init()
