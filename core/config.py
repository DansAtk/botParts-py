import pathlib
import multiprocessing

inQ = None
outQ = None
debugQ = None
promptQ = None

running = None
login = None

settings = {'dbversion' : '0.3'}

# Paths
backupPath = pathlib.Path.cwd() / 'backup'
dataPath = pathlib.Path.cwd() / 'data'
conFile = pathlib.Path.cwd() / 'core' / 'conf.json'
database = dataPath / 'unified.db'

if __name__ == "__main__":
    print("No main.")
