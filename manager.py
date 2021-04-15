import multiprocessing
import threading

from core import *
from ext import *

def inM():
    while config.running.is_set():
        input_text = input()
        thisMessage = commandM.fullMessageData(sesMan.currentUser, sesMan.currentServer, input_text)
        config.inQ.put(thisMessage)

def outM():
    while config.running.is_set():
        if not config.outQ.empty():
            output_text = config.outQ.get()
            if output_text:
                print(f'\n{output_text}\n')

def debugM():
    while config.running.is_set():
        if not config.debugQ.empty():
            debug_text = config.debugQ.get()
            if debug_text:
                print(f'\n>>>>>>>>>>>>>>>>>>\n{debug_text}\n<<<<<<<<<<<<<<<<<<\n')

def terminal():
    try:
        mProcesses = []
        config.running = multiprocessing.Event() 
        config.running.set()
        inThread = threading.Thread(target=inM, daemon=True)
        outThread = threading.Thread(target=outM)
        debugThread = threading.Thread(target=debugM)
        mailroom = multiprocessing.Process(target=commandM.readM)
        debugThread.start()

        loggedin = False

        while config.running.is_set():
            if sesMan.currentAlias:
                if not loggedin:
                    inThread.start()
                    outThread.start()
                    mailroom.start()
                    loggedin = True

            else:
                if loggedin:
                    inThread.join()
                    outThread.join()
                    debugThread.join()
                    loggedin = False

                print('Welcome to testBot! Please choose login or exit.')

                menuChoice = input()

                if menuChoice.lower() == 'login':
                    print()

                    sesMan.login()

                elif menuChoice.lower() == 'exit':
                    print()
                    contrigM.shutdownF()

                else:
                    print('\nUnknown command!\n')


    finally:
        if config.running.is_set():
            contrigM.moduleCleanup()
        mailroom.join()
        outThread.join()
        debugThread.join()

if __name__ == "__main__":
    terminal()

else:
    print("Run this as main")
