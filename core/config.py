import pathlib

settings = {'trigger' : '!', 'dbversion' : '0.3'}

# Tracking imported botParts modules.
imports = []

# Paths
backupPath = pathlib.Path.cwd() / 'backup'
dataPath = pathlib.Path.cwd() / 'data'
conFile = pathlib.Path.cwd() / 'core' / 'conf.json'
database = dataPath / 'unified.db'

if __name__ == "__main__":
    print("No main.")
