# Classes and functions for organizing and utilizing commands and subcommands in a botParts bot.

# botParts requires sys, commandM and config to be imported by all modules.
import sys
import inspect
import multiprocessing
import queue
import concurrent.futures
import copy

from core import config

if not config.inQ:
    config.inQ = Queue()

if not config.outQ:
    config.outQ = Queue()

if not config.debugQ:
    config.debugQ = Queue()

# These lines are also required by all botParts modules for the module to register itself with the bot and set up its own dictionary of commands. Defining mSelf as the current module makes it easier to define top-level module commands.

imports = {}
ongoing = {}

mSelf = sys.modules[__name__]
includes = {}

# The command class. Can be used to define top level commands and sub-commands/arguments/parameters. Every command must be given at least a name and a parent. All subcommand trees must lead back to a top level command that has the module itself as a parent.

def manage_read_pool():
    global ongoing
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        messageReaders = {}

        while config.running.is_set():
            done, not_done = concurrent.futures.wait(messageReaders, timeout=0.1, return_when=concurrent.futures.FIRST_COMPLETED)

            while not config.inQ.empty():
                inMessage = config.inQ.get()

                theseCommands = {}
                for module in imports:
                    theseCommands.update({module : {}})

                    for name, command in imports[module].items():
                        theseCommands[module].update({name : command})

                testFilter = messageData()
                testFilter.server = inMessage.server
                testFilter.channel = inMessage.channel
                testFilter.user = inMessage.user

                result = findFilters(testFilter)

                if result:
                    if 'commands' in ongoing[result]:
                        theseCommands[ongoing[result]['module']].update(ongoing[result]['commands'])

                    if 'tag' in ongoing[result]:
                        if inMessage.content.startswith(f'{inMessage.server.trigger}{ongoing[result]["tag"]}>'):
                            inMessage.content = inMessage.content.split(f'{inMessage.server.trigger}{ongoing[result]["tag"]}>', 1)[1] 
                            ongoing[result]['queue'].put(inMessage)
                        else:
                            messageReaders[executor.submit(readM, inMessage, theseCommands)] = inMessage
                    else:
                        messageReaders[executor.submit(readM, inMessage, theseCommands)] = inMessage
                else:
                    messageReaders[executor.submit(readM, inMessage, theseCommands)] = inMessage

            for future in done:
                inMessage = messageReaders[future]

                try:
                    response = future.result()
                except Exception as E:
                    print(E)
                else:
                    pass

                if inMessage.id in ongoing:
                    print(f'removing ongoing game {inMessage.id}')
                    del ongoing[inMessage.id]
                    print(f'removed.')
                del messageReaders[future]

def findFilters(findMessage):
    global ongoing
    foundServerFilters = []
    foundChannelFilters = []
    foundUserFilters = []

    for eachKey, eachValue in ongoing.items():
        if findMessage.server.id == eachValue['filter'].server.id:
            foundServerFilters.append(eachKey)

    if len(foundServerFilters) == 1:
        return foundServerFilters[0]

    elif len(foundServerFilters) > 1:
        for each in foundServerFilters:
            thisFilter = ongoing[each]['filter']
            if thisFilter.channel == None or findMessage.channel == None:
                foundChannelFilters.append(each)
            else:
                if findMessage.channel.id == thisFilter.channel.id:
                    foundChannelFilters.append(each)
        
        if len(foundChannelFilters) == 1:
            return foundChannelFilters[0]

        elif len(foundChannelFilters) > 1:
            for each in foundChannelFilters:
                thisFilter = ongoing[each]['filter']
                if thisFilter.user == None or findMessage.user == None:
                    foundUserFilters.append(each)
                else:
                    if findMessage.user.id == thisFilter.user.id:
                        foundUserFilters.append(each)

            if len(foundUserFilters) == 1:
                return foundUserFilters[0]
            
            else:
                return None
        else:
            return None
    else:
        return None

def request_queue(ref_message, filter_user=False, filter_channel=False):
    global ongoing
    newQ = queue.Queue()
    thisFilter = messageData()

    thisFilter.server = ref_message.server
    if filter_channel == True:
        thisFilter.channel = ref_message.channel
    if filter_user == True:
        thisFilter.user = ref_message.user

    ongoing.update({ref_message.id : {'filter' : thisFilter, 'queue' : newQ, 'tag' : ref_message.id}})

    return ongoing[ref_message.id]

def temp_commands(ref_message, moduleName, addition, filter_user=False, filter_channel=False):
    global ongoing
    thisFilter = messageData()

    thisFilter.server = ref_message.server
    if filter_channel == True:
        thisFilter.channel = ref_message.channel
    if filter_user == True:
        thisFilter.user = ref_message.user

    ongoing.update({ref_message.id : {'filter' : thisFilter, 'module' : moduleName, 'commands' : addition}})

    return 0

class command:
    def __init__(self, NAME, PARENT, STORAGE=None, DESCRIPTION=None, INSTRUCTION=None, FUNCTION=None, ENABLED=True, PERM=0):
        self.name = NAME
        self.parent = PARENT
        self.description = DESCRIPTION
        self.instruction = INSTRUCTION
        self.function = FUNCTION
        self.enabled = ENABLED
        self.perm = PERM
        self.includes = {}
        self.storage = STORAGE

        if inspect.ismodule(self.parent):
            self.parent_module = self.parent
        else:
            mod = self
            while not inspect.ismodule(mod):
                mod = mod.parent
            self.parent_module = mod

        if self.storage != None:
            self.storage.update({self.name : self})
        else:
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
def readM(thisMessage, theseCommands):
    global imports
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

        for module in theseCommands:
            pack = theseCommands[module]

            i = 0
            if (i < len(fullCommand)) and (fullCommand[i].lower() in pack):
                pack = pack[fullCommand[i].lower()]
                i += 1
                while (i < len(fullCommand)) and (fullCommand[i].lower() in pack.includes):
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

        #valid = False
#
        #for module in imports.keys():
            #pack = sys.modules[module]
#
            #i = 0
            #while (i < len(fullCommand)) and (fullCommand[i].lower() in pack.includes.keys()):
                #pack = pack.includes[fullCommand[i].lower()]
                #i += 1
#
            #if i > 0:
                #valid = True
#
                #if ' '.join(fullCommand[i:]).lower() == 'help':
                    #config.debugQ.put(f'{pack.help()}')
                #else:
                    #inputData = messageData()
                    #content = None
#
                    #if thisMessage.id:
                        #inputData.id = thisMessage.id
                    #if thisMessage.user:
                        #inputData.user = thisMessage.user
                    #if thisMessage.server:
                        #inputData.server = thisMessage.server
                    #if len(fullCommand[i:]) > 0:
                        #content = fullCommand[i:]
#
                    #pack.execute(inputData, content)
#
        #if valid == False:
            #config.debugQ.put('Invalid command!')


# Use registerCommands() to declare and set up commands, and register them with the module's dictionary so they can be found by the bot. Command objects can be denoted with a C at the end as a naming convention.
def registerCommands():
    commandsC = command('commands', mSelf)
    commandsC.description = 'Lists all currently supported commands, across all active modules.'
    commandsC.instruction = 'Use the command by itself.'
    commandsC.function = 'commandsF'
    imports.update({__name__ : includes})

# Functions associated with commands declared in registerCommands() can be defined here. These functions can be denoted with an F at the end as a naming convention.
def commandsF(inputData):
    global imports
    currentCommands = 'Currently available commands: '
    for i, module in enumerate(imports):
        if i:
            currentCommands += ', '

        for i, each in enumerate(imports[module]):
            if i:
                currentCommands += ', '
        
            currentCommands += each


    config.outQ.put(currentCommands)

# botParts modules are generally designed to be imported by the botParts core modules and not used as mains themselves. If the module is used as main, print an overview of the module's use and then exit. If it is imported, go ahead with registering the module with the bot.
if __name__ == "__main__":
    print("A framework for easily implementing and handling branching commands for a chat bot. No main.\n")
else:
    registerCommands()
