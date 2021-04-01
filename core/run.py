import config
import configM
import commandM
import controlM
import sayM
#import tester
#import studymodule
#import moduletemplate
#import databasemodule
#import usermgmtmodule

def main():
    try:
        while True:
            input_text = input()

            commandM.read(input_text)
    finally:
        controlM.moduleCleanup()

if __name__ == "__main__":
    main()

else:
    print("Run this as main")
