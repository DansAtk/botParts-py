import pathlib

settings = {'trigger' : '!'}

imports = []

if __name__ == "__main__":
    print("No main.")

backupPath = pathlib.Path.cwd() / 'backup'
dataPath = pathlib.Path.cwd() / 'data'
conFile = pathlib.Path.cwd() / 'core' / 'conf.json'
dbversion = '0.2'
