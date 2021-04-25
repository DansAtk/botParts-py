import commandM
import sys
import config

includes = {}
config2.imports.append('tester')
self = sys.modules[__name__]

testNew = commandM.command('testNew', self)

New = commandM.command('New', self)
test = commandM.command('test', self)
test.description = 'This is description test.'

one = commandM.command('one', test, FUNCTION='oneF')
two = commandM.command('two', test)
three = commandM.command('three', test)
four = commandM.command('four', New)
four.function = 'fourF'
five = commandM.command('five', New)
five.description = 'This is description 5.'
six = commandM.command('six', testNew)

def oneF():
    print('function one')

def fourF(intext):
    print('function {}'.format(' '.join(intext)))
