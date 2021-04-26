import sys
import multiprocessing
import threading
import time

import config

config.inQ = multiprocessing.Queue()
config.outQ = multiprocessing.Queue()
config.debugQ = multiprocessing.Queue()

mSelf = sys.modules[__name__]
includes = {}
config.register(mSelf)

def inM():
    while config.running.is_set():
        input_text = input()
        config.outQ.put(input_text)

def outM():
    while config.running.is_set():
        if not config.outQ.empty():
            output_text = config.outQ.get()
            if output_text:
                print(f'\n{output_text}\n')

def debugM():
        if not config.debugQ.empty():
            debug_text = config.debugQ.get()
            if debug_text:
                print(f'\n>>>>>>>>>>>>>>>>>>\n{debug_text}\n<<<<<<<<<<<<<<<<<<\n')

def registerCommands():
    includes.update({'a command' : 'wow'})
    
def begin():
    try:  
        registerCommands()
        config.running = multiprocessing.Event() 
        config.running.set()
        config.signals.update({'login' : multiprocessing.Event()}) 
        config.signals['login'].clear()
        inThread = threading.Thread(target=inM, daemon=True)
        inThread.start()
        outThread = threading.Thread(target=outM)
        outThread.start()
        debugThread = threading.Thread(target=debugM)
        debugThread.start()

        while True:
            time.sleep(1)

    finally:
        config.debugQ.put('Closing message queues...')
        config.inQ.close()
        config.inQ.join_thread()
        outThread.join(timeout=1)
        config.outQ.close()
        config.outQ.join_thread()
        while not config.debugQ.empty():
            time.sleep(0.5)

        debugThread.join(timeout=1)
        config.debugQ.close()
        config.debugQ.join_thread()

        sys.exit()

if __name__ == "__main__":
    print('An offline, multiuser and (simulated) multiserver session managing interface. No main.')
