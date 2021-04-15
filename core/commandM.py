# Classes and functions for organizing and utilizing commands and subcommands in a botParts bot.

# botParts requires sys, commandM and config to be imported by all modules.
import sys
import inspect
from core import config

# These lines are also required by all botParts modules for the module to register itself with the bot and set up its own dictionary of commands. Defining mSelf as the current module makes it easier to define top-level module commands.

mSelf = sys.modules[__name__]
includes = {}
config.imports.append(__name__)

# The command class. Can be used to define top level commands and sub-commands/arguments/parameters. Every command must be given at least a name and a parent. All subcommand trees must lead back to a top level command that has the module itself as a parent.
class command:
    def __init__(self, NAME, PARENT, DESCRIPTION=None, INSTRUCTION=None, FUNCTION=None, ENABLED=True, PERM=0):
        self.name = NAME
        self.parent = PARENT
        self.description = DESCRIPTION
        self.instruction = INSTRUCTION
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

    def paramText(self):
        paramList = ''
        for parameter in self.includes.values():
            paramList += parameter.name + ', '

        paramList += 'help.'

        return paramList

    def howTo(self):
        if self.instruction:
            howText = f'{self.instruction} Available parameters: {self.paramText()}'

        else:
            howText = f'Available parameters: {self.paramText()}'

        return howText

    def help(self):
        helpText = f'{self.description} {self.howTo()}'

        return helpText

    def paramError(self, userinput):
        errorText = f'Unknown argument(s) \'{userinput}\'. {self.howTo()}'
        return errorText

    def execute(self, inputData=None, content=None):
        try:
            if inputData:
                if inputData and content:
                    getattr(self.parent_module, self.function)(inputData, content)
                else:
                    getattr(self.parent_module, self.function)(inputData)
            else:
                if content:
                    getattr(self.parent_module, self.function)(content)
                else:
                    getattr(self.parent_module, self.function)()

        except TypeError:
            # Often raised when a command is given too many or too few arguments.
            if content:
                config.debugQ.put(f'{self.paramError(" ".join(content))}')
            else:
                config.debugQ.put(f'{self.howTo()}')
        
        except AttributeError:
            # Often raised when a command does not have an associated function.
            config.debugQ.put(f'{self.howTo()}')

class messageData:
    def __init__(self, USER=None, SERVER=None):
        self.user = USER
        self.server = SERVER

class fullMessageData(messageData):
    def __init__(self, USER=None, SERVER=None, CONTENT=None):
        self.content = CONTENT
        super().__init__(USER, SERVER)


# Utility function for reading incoming text and parsing it for both a valid trigger and valid commands across all imported botParts modules. If a valid command is found, its associated function is executed and passed the remainder of the input text as arguments.
def readM():
    while config.running:
        if config.inQ:
            if not config.inQ.empty():
                thisMessage = config.inQ.get(block=True, timeout=0.01)

                doRead = False
                if thisMessage.server.trigger and len(thisMessage.server.trigger) > 0:
                    if thisMessage.content.startswith(thisMessage.server.trigger):
                        fullText = thisMessage.content.split(thisMessage.server.trigger, 1)[1] 

                        doRead = True

                else:
                    fullText = thisMessage.content
                    
                    doRead = True

                if doRead:
                    commandText = fullText.split(' ')
                    fullCommand = []
                    quoteText = None
                    for parameter in commandText:
                        if '"' in parameter and not quoteText:
                            if parameter.endswith('"'):
                                fullCommand.append(parameter)
                            else:
                                quoteText = parameter

                        elif parameter.endswith('"') and quoteText:
                            quoteText = f'{quoteText} {parameter}'
                            fullCommand.append(quoteText)
                            quoteText = None

                        else:
                            if quoteText:
                                quoteText = f'{quoteText} {parameter}'

                            else:
                                fullCommand.append(parameter)

                    if quoteText:
                        fullCommand.append(quoteText)

                    valid = False

                    for module in config.imports:
                        pack = sys.modules[module]

                        i = 0
                        while (i < len(fullCommand)) and (fullCommand[i].lower() in pack.includes.keys()):
                            pack = pack.includes[fullCommand[i].lower()]
                            i += 1

                        if i > 0:
                            valid = True

                            if ' '.join(fullCommand[i:]).lower() == 'help':
                                config.debugQ.put(f'{pack.help()}')
                            else:
                                inputData = messageData()
                                content = None

                                if thisMessage.user:
                                    inputData.user = thisMessage.user
                                if thisMessage.server:
                                    inputData.server = thisMessage.server
                                if len(fullCommand[i:]) > 0:
                                    content = fullCommand[i:]

                                pack.execute(inputData, content)

                    if valid == False:
                        config.debugQ.put('Invalid command!')

# Use registerCommands() to declare and set up commands, and register them with the module's dictionary so they can be found by the bot. Command objects can be denoted with a C at the end as a naming convention.
def registerCommands():
    commandsC = command('commands', mSelf)
    commandsC.description = 'Lists all currently supported commands, across all active modules.'
    commandsC.instruction = 'Use the command by itself.'
    commandsC.function = 'commandsF'

# Functions associated with commands declared in registerCommands() can be defined here. These functions can be denoted with an F at the end as a naming convention.
def commandsF(inputData):
    currentCommands = 'Currently available commands: '
    for i, module in enumerate(config.imports):
        for command in sys.modules[module].includes:
            if i:
                currentCommands += ', '
            
            currentCommands += command


    config.outQ.put(currentCommands)
    #print(currentCommands)

# botParts modules are generally designed to be imported by the botParts core modules and not used as mains themselves. If the module is used as main, print an overview of the module's use and then exit. If it is imported, go ahead with registering the module with the bot.
if __name__ == "__main__":
    print("A framework for easily implementing and handling branching commands for a chat bot. No main.\n")
else:
    registerCommands()
