import sys
import inspect
import multiprocessing
from queue import Queue
import concurrent.futures
import copy

import config

if not config.inQ:
    config.inQ = Queue()

if not config.outQ:
    config.outQ = Queue()

if not config.debugQ:
    config.debugQ = Queue()

imports = config.imports
ongoing = {}

def manage_read_pool():
    global ongoing
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        messageReaders = {}

        while config.running.is_set():
            done, not_done = concurrent.futures.wait(messageReaders, timeout=0.1, return_when=concurrent.futures.FIRST_COMPLETED)

            while not config.inQ.empty():
                inMessage = config.inQ.get()

                theseCommands = {}
                for collection in imports:
                    theseCommands.update({collection : {}})

                    for module in imports[collection]:
                        theseCommands[collection].update({module : {}})

                        for command in imports[collection][module]:
                            theseCommands[collection][module].update({command : imports[collection][module][command]})

                testFilter = messageData()
                testFilter.place = inMessage.place
                testFilter.channel = inMessage.channel
                testFilter.user = inMessage.user

                result = findFilters(testFilter)

                if result:
                    if 'commands' in ongoing[result]:
                        for collection in theseCommands:
                            if ongoing[result]['module'] in theseCommands[collection]:
                                theseCommands[collection][ongoing[result]['module']].update(ongoing[result]['commands'])

                    if 'tag' in ongoing[result]:
                        if inMessage.content.startswith(f'{inMessage.place.trigger}{ongoing[result]["tag"]}>'):
                            inMessage.content = inMessage.content.split(f'{inMessage.place.trigger}{ongoing[result]["tag"]}>', 1)[1] 
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
                    del ongoing[inMessage.id]
                del messageReaders[future]

def findFilters(findMessage):
    global ongoing
    foundServerFilters = []
    foundChannelFilters = []
    foundUserFilters = []

    for eachKey, eachValue in ongoing.items():
        if findMessage.place.id == eachValue['filter'].place.id:
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
    newQ = Queue()
    thisFilter = messageData()

    thisFilter.place = ref_message.place
    if filter_channel == True:
        thisFilter.channel = ref_message.channel
    if filter_user == True:
        thisFilter.user = ref_message.user

    ongoing.update({ref_message.id : {'filter' : thisFilter, 'queue' : newQ, 'tag' : ref_message.id}})

    return ongoing[ref_message.id]

def temp_commands(ref_message, moduleName, addition, filter_user=False, filter_channel=False):
    global ongoing
    thisFilter = messageData()

    thisFilter.place = ref_message.place
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

        self.parent_module = None

        if inspect.ismodule(self.parent):
            self.parent_module = self.parent
        else:
            mod = self
            while not mod.parent_module:
                mod = mod.parent
            self.parent_module = mod.parent_module

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
    def __init__(self, ID=None, USER=None, PLACE=None, CHANNEL=None):
        self.id = ID
        self.user = USER
        self.place = PLACE
        self.channel = CHANNEL

    def fits(other):
        likeness = 0

        if other.place == None or self.place == None:
            likeness += 1
        else:
            if self.place.id == other.place.id:
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
    def __init__(self, ID=None, USER=None, PLACE=None, CONTENT=None, CHANNEL=None):
        self.content = CONTENT
        super().__init__(ID, USER, PLACE, CHANNEL)

# Utility function for reading incoming text and parsing it for both a valid trigger and valid commands across all imported botParts modules. If a valid command is found, its associated function is executed and passed the remainder of the input text as arguments.
def readM(thisMessage, theseCommands):
    global imports
    doRead = False
    if thisMessage.place.trigger and len(thisMessage.place.trigger) > 0:
        if thisMessage.content.startswith(thisMessage.place.trigger):
            fullText = thisMessage.content.split(thisMessage.place.trigger, 1)[1] 

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

        if ' '.join(fullCommand).lower() == 'commands':
            currentCommands = 'Currently available commands: '

            for i, collection in enumerate(theseCommands):
                if i and not currentCommands.endswith(', '):
                    currentCommands += ', '

                for i, module in enumerate(theseCommands[collection]):
                    if i and not currentCommands.endswith(', '):
                        currentCommands += ', '

                    for i, each in enumerate(theseCommands[collection][module]):
                        if i and not currentCommands.endswith(', '):
                            currentCommands += ', '

                        currentCommands += each

            config.outQ.put(currentCommands)

        else:
            valid = False

            for collection in theseCommands:
                for module in theseCommands[collection]:
                    i = 0
                    pack = theseCommands[collection][module]

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
                            if thisMessage.place:
                                inputData.place = thisMessage.place
                            if len(fullCommand[i:]) > 0:
                                content = fullCommand[i:]

                            pack.execute(inputData, content)

            if valid == False:
                config.debugQ.put('Invalid command!')

if __name__ == "__main__":
    print("A framework for easily implementing and handling branching commands for a chat bot. No main.\n")
