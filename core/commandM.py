# Classes and functions for organizing and utilizing commands and subcommands in a botParts bot.

# botParts requires sys, commandM and config to be imported by all modules.
import sys
import inspect
import multiprocessing
import queue
import concurrent.futures

from core import config

if not config.inQ:
    config.inQ = Queue()

if not config.outQ:
    config.outQ = Queue()

if not config.debugQ:
    config.debugQ = Queue()

# These lines are also required by all botParts modules for the module to register itself with the bot and set up its own dictionary of commands. Defining mSelf as the current module makes it easier to define top-level module commands.

mSelf = sys.modules[__name__]
includes = {}
config.imports.append(__name__)

ongoing = {}

# The command class. Can be used to define top level commands and sub-commands/arguments/parameters. Every command must be given at least a name and a parent. All subcommand trees must lead back to a top level command that has the module itself as a parent.

def manage_read_pool():
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        messageReaders = {}

        while config.running.is_set():
            done, not_done = concurrent.futures.wait(messageReaders, timeout=0.1, return_when=concurrent.futures.FIRST_COMPLETED)

            while not config.inQ.empty():
                inMessage = config.inQ.get()

                testFilter = messageData()
                testFilter.server = inMessage.server
                testFilter.channel = inMessage.channel
                testFilter.user = inMessage.user

                #results = findFilters(testFilter)

                #if results:
                    #ongoing[results].put(inMessage)
                #else:
                messageReaders[executor.submit(readM, inMessage)] = inMessage

            for future in done:
                inMessage = messageReaders[future]

                try:
                    response = future.result()
                except:
                    print('F exception')
                else:
                    pass

                #if ongoing[inMessage]:
                    #del ongoing[inMessage.id]
                del messageReaders[future]

def findFilters(findMessage):
    foundServerFilters = []
    foundChannelFilters = []
    foundUserFilters = []

    for each in ongoing.keys():
        if findMessage.server.id == each.server.id:
            foundServerFilters.append(each)

    if len(foundServerFilters) == 1:
        return foundServerFilters[0]

    elif len(foundServerFilters) > 1:
        for each in ongoing.keys():
            if each.channel == None or findMessage.channel == None:
                foundChannelFilters.append(each)
            else:
                if findMessage.channel.id == each.channel.id:
                    foundChannelFilters.append(each)
        
        if len(foundChannelFilters) == 1:
            return foundChannelFilters[0]

        elif len(foundChannelFilters) > 1:
            for each in ongoing.keys():
                if each.user == None or findMessage.user == None:
                    foundUserFilters.append(each)
                else:
                    if findMessage.user.id == each.user.id:
                        foundUserFilters.append(each)

            if len(foundUserFilters) == 1:
                return foundUserFilters[0]
            
            else:
                return None
        else:
            return None
    else:
        return None

def request_queue(filter_message, filter_user=False, filter_channel=False):
    print('entered request')
    newQ = Queue.Queue()
    thisFilter = filter_message

    thisFilter.id = None
    if filter_user == False:
        thisFilter.user = None
    if filter_channel == False:
        thisFilter.channel = None

    ongoing.update({filter_message : newQ})

    print('got queue')

    return ongoing[filter_message]

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
    def __init__(self, ID=None, USER=None, SERVER=None, CHANNEL=None):
        self.id = ID
        self.user = USER
        self.server = SERVER
        self.channel = CHANNEL

    def fits(other):
        likeness = 0

        if other.server == None or self.server == None:
            likeness += 1
        else:
            if self.server.id == other.server.id:
                likeness += 1
            else:
                return 0

        if other.channel == None or self.channel == None:
            likeness += 1
        else:
            if self.channel.id == other.channel.id:
                likeness += 1
            else:
                return 0

        if other.user == None or self.user == None:
            likeness += 1
        else:
            if self.user.id == other.user.id:
                likeness += 1
            else:
                return 0

        return likeness

class fullMessageData(messageData):
    def __init__(self, ID=None, USER=None, SERVER=None, CONTENT=None, CHANNEL=None):
        self.content = CONTENT
        super().__init__(ID, USER, SERVER, CHANNEL)


# Utility function for reading incoming text and parsing it for both a valid trigger and valid commands across all imported botParts modules. If a valid command is found, its associated function is executed and passed the remainder of the input text as arguments.
def readM(thisMessage):
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

                    if thisMessage.id:
                        inputData.id = thisMessage.id
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

# botParts modules are generally designed to be imported by the botParts core modules and not used as mains themselves. If the module is used as main, print an overview of the module's use and then exit. If it is imported, go ahead with registering the module with the bot.
if __name__ == "__main__":
    print("A framework for easily implementing and handling branching commands for a chat bot. No main.\n")
else:
    registerCommands()
