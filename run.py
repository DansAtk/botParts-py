import importlib
import config
from core import *
from core.ext import *
thisMod = importlib.import_module(f'interface.{config.interface}')
thisModExt = importlib.import_module(f'interface.{config.interface}.ext')

def start():
    thisMod.login.start()

if __name__ == "__main__":
    start()
else:
    print('Run as main.')
