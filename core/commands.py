import sys
import inspect
import multiprocessing
from queue import Queue
import concurrent.futures
import copy

import config
from core.perms import getCombinedPerm

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
                            #THIS IS WHERE TO LOAD theseCommands WITH PERMISSIONS
                            theseCommands[collection][module].update({command : imports[collection][module][command]})

                results = findFilters(inMessage)

                if results:
                    for each in results:
                        if 'commands' in ongoing[each]:
                            for collection in theseCommands:
                                if ongoing[each]['module'] in theseCommands[collection]:
                                    theseCommands[collection][ongoing[each]['module']].update(ongoing[each]['commands'])

                        #THIS IS WHERE TO LOAD ONGOING COMMANDS WITH PERMISSIONS

                        if 'tag' in ongoing[each]:
                            if inMessage.content.startswith(f'{inMessage.place.trigger}{ongoing[each]["tag"]}>'):
                                inMessage.content = inMessage.content.split(f'{inMessage.place.trigger}{ongoing[each]["tag"]}>', 1)[1] 
                                ongoing[each]['queue'].put(inMessage)
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
    foundFilters = []

    for eachKey, eachValue in ongoing.items():
        if eachValue['filter'].compare(findMessage):
            foundFilters.append(eachKey)

    if len(foundFilters) > 0:
        return foundFilters
    
    else:
        return None

def request_queue(ref_message, filter_place=None, filter_user=None, filter_group=None):
    global ongoing
    newQ = Queue()
    thisFilter = messageFilter()

    if filter_place or filter_user or filter_group:
        if filter_place:
            thisFilter.place = filter_place
        if filter_user:
            thisFilter.user = filter_user
        if filter_group:
            thisFilter.group = filter_group

        ongoing.update({ref_message.id : {'filter' : thisFilter, 'queue' : newQ, 'tag' : ref_message.id}})

        return ongoing[ref_message.id]

    else:
        return None

def temp_commands(ref_message, moduleName, addition, filter_place=None, filter_user=None, filter_group=None):
    global ongoing
    thisFilter = messageFilter()

    if filter_place or filter_user or filter_group:
        if filter_place:
            thisFilter.place = filter_place
        if filter_user:
            thisFilter.user = filter_user
        if filter_group:
            thisFilter.group = filter_group

        ongoing.update({ref_message.id : {'filter' : thisFilter, 'module' : moduleName, 'commands' : addition}})

        return 0

    else:
        return 1

class command:
    def __init__(self, NAME, PARENT, STORAGE=None, DESCRIPTION=None, INSTRUCTION=None, FUNCTION=None, ENABLED=True):
        self.name = NAME
        self.full_name = NAME
        self.parent = PARENT
        self.description = DESCRIPTION
        self.instruction = INSTRUCTION
        self.function = FUNCTION
        self.enabled = ENABLED
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

        com = self
        while not inspect.ismodule(com.parent):
            self.full_name = f'{com.parent.name} {self.full_name}'
            com = com.parent

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
    def __init__(self, ID=None, USER=None, PLACE=None):
        self.id = ID
        self.user = USER
        self.place = PLACE

class fullMessageData(messageData):
    def __init__(self, ID=None, USER=None, PLACE=None, CONTENT=None):
        self.content = CONTENT
        super().__init__(ID, USER, PLACE)

class messageFilter:
    def __init__(self, USER=None, PLACE=None, GROUP=None):
        self.user = USER
        self.place = PLACE
        self.group = GROUP

    def compare(self, message):
        isMatch = True

        if self.user:
            if message.user.id != self.user.id:
                isMatch = False
        if self.place and isMatch:
            if not message.place.checkInheritance(self.place.id):
                isMatch = False
        if self.group and isMatch:
            if not self.group.checkUserMember(message.user.id):
                isMatch = False

        return isMatch

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

                            thisPerm = perms.getCombinedPerm(inputData, pack.full_name)
                            
                            if thisPerm:
                                if thisPerm.value == 1:
                                    config.outQ.put('You do not have permission to do that!')
                                else:
                                    pack.execute(inputData, content)
                            else:
                                pack.execute(inputData, content)

            if valid == False:
                config.debugQ.put('Invalid command!')

def verifyCommand(fullText):
    global imports
    commandText = fullText.split(' ')
    fullCommand = []

    for parameter in commandText:
        fullCommand.append(parameter)

    valid = False

    if fullText.lower() == 'commands':
        valid = True

    else:
        for collection in imports:
            for module in imports[collection]:
                i = 0
                pack = imports[collection][module]

                if (i < len(fullCommand)) and (fullCommand[i].lower() in pack):
                    pack = pack[fullCommand[i].lower()]
                    i += 1
                    while (i < len(fullCommand)) and (fullCommand[i].lower() in pack.includes):
                        pack = pack.includes[fullCommand[i].lower()]
                        i += 1
                    
                if i == (len(fullCommand) - 1):
                    valid = True
    
    return valid

if __name__ == "__main__":
    print("A framework for easily implementing and handling branching commands for a chat bot. No main.\n")
