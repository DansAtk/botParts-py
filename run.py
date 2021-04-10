from core import *
from ext import *

#import usermgmtmodule

def main():
    try:
        while True:
            input_text = input()

            commandM.read(input_text)
    finally:
        contrigM.moduleCleanup()

if __name__ == "__main__":
    main()

else:
    print("Run this as main")
