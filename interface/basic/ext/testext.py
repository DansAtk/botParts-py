import sys
import config

mSelf = sys.modules[__name__]
includes = {}
config.register(mSelf)

def registerCommands():
    includes.update({'this' : 'should be in interface-ext'})

if __name__ == '__main__':
    print('test no main')
else:
    registerCommands()
