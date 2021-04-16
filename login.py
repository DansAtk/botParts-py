import sys
import multiprocessing
import threading
import time

from core import config

config.inQ = multiprocessing.Queue()
config.outQ = multiprocessing.Queue()
config.debugQ = multiprocessing.Queue()
config.promptQ = multiprocessing.Queue()

from core import *
from ext import *

def inM():
    while config.running.is_set():
        input_text = input()

        if sesMan.currentAlias:
            thisMessage = commandM.fullMessageData(sesMan.currentUser, sesMan.currentServer, input_text)
            config.inQ.put(thisMessage)
        else:
            config.promptQ.put(input_text)

def outM():
    while config.running.is_set():
        if not config.outQ.empty():
            output_text = config.outQ.get()
            if output_text:
                print(f'\n{output_text}\n')

def debugM():
    while not shuttingdown:
        if not config.debugQ.empty():
            debug_text = config.debugQ.get()
            if debug_text:
                print(f'\n>>>>>>>>>>>>>>>>>>\n{debug_text}\n<<<<<<<<<<<<<<<<<<\n')


def terminal():
    try:  
        config.running = multiprocessing.Event() 
        config.running.set()
        config.login = multiprocessing.Event() 
        config.login.clear()
        inThread = threading.Thread(target=inM, daemon=True)
        inThread.start()
        outThread = threading.Thread(target=outM)
        outThread.start()
        debugThread = threading.Thread(target=debugM)
        debugThread.start()
        mailroom = multiprocessing.Process(target=commandM.manage_read_pool)
        mailroom.start()

        while config.running.is_set():
            if sesMan.currentAlias:
                if config.login.is_set():
                    time.sleep(0.5)
                else:
                    sesMan.clearAll()

            else:
                if config.login.is_set():
                    sesMan.login()

                else:
                    config.outQ.put('Welcome to testBot! Please choose login or exit.')

                    menuChoice = config.promptQ.get()

                    if menuChoice.lower() == 'login':
                        config.login.set()

                    elif menuChoice.lower() == 'exit':
                        contrigM.shutdownF()

                    else:
                        config.outQ.put('Unknown command!')

    except KeyboardInterrupt:
        if config.running.is_set():
            contrigM.moduleCleanup()

    finally:
        if config.running.is_set():
            contrigM.moduleCleanup()
        config.debugQ.put('Closing message queues...')
        config.inQ.close()
        config.inQ.join_thread()
        config.promptQ.close()
        config.promptQ.join_thread()
        outThread.join(timeout=1)
        config.outQ.close()
        config.outQ.join_thread()
        while not config.debugQ.empty():
            time.sleep(0.5)

        global shuttingdown
        shuttingdown = True
        debugThread.join(timeout=1)
        config.debugQ.close()
        config.debugQ.join_thread()

        mailroom.join(timeout=1)

        sys.exit()

if __name__ == "__main__":
    shuttingdown = False
    terminal()

else:
    print("Run this as main")
