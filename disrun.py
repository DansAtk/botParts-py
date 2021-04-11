from core import *
from ext import *

def main():
    try:
        while True:
            if sesMan.currentAlias:
                input_text = input()
                trigger = None

                try:
                    trigger = config.settings['trigger']

                except KeyError:
                    pass

                commandM.read(input_text, trigger)

            else:
                print('Welcome to testBot! Please sign in.')

                userText = input('User: ')

                sesMan.setUser(userText)

                if sesMan.currentUser:
                    serverText = input('Server: ')

                    sesMan.setServer(serverText)

                    if sesMan.currentServer:
                        sesMan.setAlias()

                        if sesMan.currentAlias:
                            print('\nLogged in as {} on server {}.\n'.format(sesMan.currentUser.name, sesMan.currentServer.name))

                        else:
                            print('\nError: User {} has no alias on server {}.\n'.format(sesMan.currentUser.name, sesMan.currentServer.name))

                    else:
                        print('\nError: Server not found!\n')

                else:
                    print('\nError: User not found!\n')

    finally:
        contrigM.moduleCleanup()

if __name__ == "__main__":
    main()

else:
    print("Run this as main")
