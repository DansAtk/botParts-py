import config
import commands
import messparse
import saymodule
import studymodule

def main():
    while True:
        input_text = input()

        messparse.read(input_text)


if __name__ == "__main__":
    main()

else:
    print("Run this as main")

