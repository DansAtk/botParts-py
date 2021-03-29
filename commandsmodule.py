# Classes and functions for organising available commands in each module.

import sys

import config

includes = {}

class command:
    def __init__(self, callname, module):
        self.name = callname
        self.parent_module = module
        self.description = ""
        self.parameters = {}
        self.function = ""
        self.enabled = True
        self.permlevel = 0

    def help(self):
        helptext = self.description + " Available parameters: "
        for param in self.parameters.values():
            helptext += param.name + ", "

        helptext += "help."
        return helptext

    def paramError(self, additional):
        errorText = "Unknown parameter(s) \'" + ' '.join(additional) + "\'. Available parameters: " + ', '.join(self.parameters) + (', ' * (len(self.parameters) > 0)) + "help."
        return errorText

    def execute(self, additional=""):
        getattr(sys.modules[self.parent_module], self.function)(additional)

# Parses incoming messages and finds/selects the desired command, if exists.
def read(text):
    if text.startswith(config.settings['trigger']):
        message = text[1:].split(" ")
        valid = 0
        for module in config.imports:
            if message[0] in sys.modules[module].includes.keys():
                valid = 1
                i = 1
                pack = sys.modules[module].includes[message[0]]
                for word in message[1:]:
                    if word in pack.parameters.keys():
                        pack = pack.parameters[word]
                        i += 1
                if ' '.join(message[i:]) == "help":
                    print(pack.help())
                else:
                    try:
                        pack.execute(message[i:])
                    except AttributeError:
                        print("This parameter does not have an associated function.")

        if valid == 0:
            print("Invalid command!")

# Prints all currently imported and supported bot commands.
commands = command('commands', __name__)

def init():
    includes.update({commands.name : commands})
    commands.description = "Lists all currently supported commands, across all active modules using the botParts commands module."
    commands.function = 'commandsF'

def commandsF(message):
    currentCommands = "Currently available commands: "
    for i, module in enumerate(config.imports):
        for command in sys.modules[module].includes:
            if i:
                currentCommands += ", "

            currentCommands += command

    print(currentCommands)

if __name__ == "__main__":
    print("A framework for easily implementing a branching command UI for a chat bot. No main.")
else:
    config.imports.append('commandsmodule')
    init()
