import multiprocessing
import threading
import time

from core import *
from ext import *

def inM():
    while True:
        input_text = input()
        thisMessage = commandM.fullMessageData(sesMan.currentUser, sesMan.currentServer, input_text)
        config.inQ.put(thisMessage)

def outM():
    while True:
        if not config.outQ.empty():
            output_text = config.outQ.get()
            if output_text:
                print(f'\n{output_text}\n')

def debugM():
    while True:
        if not config.debugQ.empty():
            debug_text = config.debugQ.get()
            print(f'\n>>>>>>>>>>>>>>>>>>\n{debug_text}\n<<<<<<<<<<<<<<<<<<\n')

def terminal():
    try:
        mProcesses = []
        inThread = threading.Thread(target=inM, daemon=True)
        outThread = threading.Thread(target=outM, daemon=True)
        debugThread = threading.Thread(target=debugM, daemon=True)
        debugThread.start()
        mailroom = multiprocessing.Process(target=commandM.readM)

        ready = False

        while True:

            if sesMan.currentAlias:
                if not ready:
                    inThread.start()
                    outThread.start()
                    mailroom.start()
                    ready = True

            else:
                if ready:
                    inThread.join()
                    outThread.join()
                    debugThread.join()
                    ready = False

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
        inThread.join()
        outThread.join()
        debugThread.join()
        mailroom.join()
        contrigM.moduleCleanup()
        config.inQ.close()
        config.inQ.join_thread()
        config.outQ.close()
        config.outQ.join_thread()
        config.debugQ.close()
        config.debugQ.join_thread()

if __name__ == "__main__":
    terminal()

else:
    print("Run this as main")
