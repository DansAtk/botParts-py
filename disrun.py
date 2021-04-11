from core import *
from ext import *

def main():
    try:
        while True:
            if sesMan.currentAlias:
                input_text = input()
                trigger = sesMan.getTrigger()

                commandM.read(input_text, trigger)

            else:
                print('Welcome to testBot! Please choose login or exit.')

                menuChoice = input()

                if menuChoice.lower() == 'login':
                    print()
                    sesMan.login()

                elif menuChoice.lower() == 'exit':
                    print()
                    contrigM.shutdownF()

                else:
                    print('\nUnknown command!\n')

    finally:
        contrigM.moduleCleanup()

if __name__ == "__main__":
    main()

else:
    print("Run this as main")
