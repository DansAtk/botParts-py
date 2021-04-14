import pathlib
import multiprocessing

#class interface:
    #def __init__(self, IN=None, OUT=None, DEBUG=None):
        #self.inQ = IN
        #self.outQ = OUT
        #self.debugQ = DEBUG

inQ = None
outQ = None
debugQ = None
#mainInterface = (inQ, outQ, debugQ)

settings = {'dbversion' : '0.3'}

# Tracking imported botParts modules.
imports = []

# Paths
backupPath = pathlib.Path.cwd() / 'backup'
dataPath = pathlib.Path.cwd() / 'data'
conFile = pathlib.Path.cwd() / 'core' / 'conf.json'
database = dataPath / 'unified.db'

if __name__ == "__main__":
    print("No main.")
