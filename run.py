import config
import configmodule
import commandsmodule
import saymodule
import studymodule
import controlmodule
import moduletemplate
import databasemodule
import usermgmtmodule

def main():
    try:
        while True:
            input_text = input()

            commandsmodule.read(input_text)
    finally:
        configmodule.cleanUp()

if __name__ == "__main__":
    main()

else:
    print("Run this as main")

