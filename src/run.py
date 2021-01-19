import sys

import config
import commands
import botmodule
import messparse

def main():
    while True:
        input_text = input()

        messparse.read(input_text)


if __name__ == "__main__":
    main()

else:
    print("Run this as main")

