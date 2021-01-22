import config
import configmodule
import commandsmodule
import messparse
import saymodule
import studymodule
import controlmodule
import usertimemodule
#import drawmodule

def main():
    try:
        while True:
            input_text = input()

            messparse.read(input_text)
    finally:
        configmodule.cleanUp()

if __name__ == "__main__":
    main()

else:
    print("Run this as main")

