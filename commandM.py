# Classes and functions for organizing and utilizing commands and subcommands in a botParts bot.

# botParts requires sys, commandM and config to be imported by all modules.
import sys
import inspect
import config

# These lines are also required by all botParts modules for the module to register itself with the bot and set up its own dictionary of commands. Defining mSelf as the current module makes it easier to define top-level module commands.

mSelf = sys.modules[__name__]
includes = {}
config.imports.append('commandM')

# The command class. Can be used to define top level commands and sub-commands/arguments/parameters. Every command must be given at least a name and a parent. All subcommand trees must lead back to a top level command that has the module itself as a parent.
class command:
    def __init__(self, NAME, PARENT, DESCRIPTION='', FUNCTION='', ENABLED=True, PERM=0):
        self.name = NAME
        self.parent = PARENT
        self.description = DESCRIPTION
        self.function = FUNCTION
        self.enabled = ENABLED
        self.perm = PERM
        self.includes = {}

        if inspect.ismodule(self.parent):
            self.parent_module = self.parent
        else:
            mod = self
            while not inspect.ismodule(mod):
                mod = mod.parent
            self.parent_module = mod

        self.parent.includes.update({self.name : self})

    def help(self):
        helptext = self.description + " Available parameters: "

        for parameter in self.includes.values():
            helptext += parameter.name + ", "

        helptext += "help."
        return helptext

    def paramError(self, userinput):
        errorText = 'Unknown argument(s) \'{text}\'. Available arguments: {arguments}.'.format(text=userinput, arguments=((', '.join(self.includes)) + (', ' * (len(self.includes) > 0)) + 'help'))
        return errorText

    def execute(self, *args):
        try:
            if args:
                getattr(self.parent_module, self.function)(args)
            else:
                getattr(self.parent_module, self.function)()

        except TypeError:
            if args:
                print(self.paramError(' '.join(args)))
            else:
                print('The associated function requires arguments.')
        
        except AttributeError:
            print('No associated function found.')

        except :
            print(sys.exc_info()[0])

# Utility function for reading incoming text and parsing it for both a valid trigger and valid commands across all imported botParts modules. If a valid command is found, its associated function is executed and passed the remainder of the input text as arguments.
def read(userinput):
    if userinput.startswith(config.settings['trigger']):
        message = userinput[1:].split(' ')
        valid = False

        for module in config.imports:
            pack = sys.modules[module]

            i = 0
            while (i < len(message)) and (message[i] in pack.includes.keys()):
                pack = pack.includes[message[i]]
                i += 1

            if i > 0:
                valid = True

                if ' '.join(message[i:]) == 'help':
                    print(pack.help())
                else:
                    pack.execute(*message[i:])

        if valid == False:
            print('Invalid command!')

# Use init() to declare and set up commands, and register them with the module's dictionary so they can be found by the bot. Command objects can be denoted with a C at the end as a naming convention.
def init():
    commandsC = command('commands', mSelf)
    commandsC.description = 'Lists all currently supported commands, across all active modules using the botParts commands module.'
    commandsC.function = 'commandsF'

# Functions associated with commands declared in init() can be defined here. These functions can be denoted with an F at the end as a naming convention.
def commandsF():
    currentCommands = 'Currently available commands: '
    for i, module in enumerate(config.imports):
        for command in sys.modules[module].includes:
            if i:
                currentCommands += ', '
            
            currentCommands += command

    print(currentCommands)

# botParts modules are generally designed to be imported by the botParts core modules and not used as mains themselves. If the module is used as main, print an overview of the module's use and then exit. If it is imported, go ahead with registering the module with the bot.
if __name__ == "__main__":
    print("A framework for easily implementing and handling branching commands for a chat bot. No main.")
else:
    init()
