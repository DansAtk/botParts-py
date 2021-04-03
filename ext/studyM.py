import sys
import sqlite3
import datetime

from core import config
from core.commandM import command

mSelf = sys.modules[__name__]
includes = {}
config.imports.append(__name__)

def init():
    global studyC
    studyC = command('study', mSelf)
    studyC.description = 'Commands for tracking and monitoring study habits.'
    studyC.function = 'studyF'
    
    global logC
    logC = command('log', studyC)
    logC.description = 'For managing tracked study sessions.'
    logC.function = 'logF'
    
    global markC 
    markC= command('mark', logC)
    markC.description = 'Marks you as having studied for the day.'
    markC.function = 'markF'

    global unmarkC
    unmarkC = command('unmark', logC)
    unmarkC.description = 'Unmarks you as having studied for the day.'
    unmarkC.function = 'unmarkF'

    global checkC
    checkC = command('check', logC)
    checkC.description = 'Returns whether study has been logged for the current day.'
    checkC.function = 'checkF'

def logF():
    print(logC.help())

def studyF():
    print(studyC.help())

def markF():
    print(markC.help())

def unmarkF():
    print(unmarkC.help())

def logPull(DB):
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    conn.commit()
    conn.close()
    return
    
def logPush(DB):
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    conn.commit()
    conn.close()
    return

def dbinit(DB):
    print('Configuring for study logging...')
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE studysessions(id INTEGER PRIMARY KEY AUTOINCREMENT, userid INTEGER, datestudied TEXT, streak INTEGER)")
    print('\'studysessions\' table created.')
    conn.commit()
    conn.close()

def cleanup():
    print('study cleanup...')

if __name__ == "__main__":
    print('A collection of study tracking commands for a botParts bot. No main.')
else:
    init()
