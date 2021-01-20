# parses the incoming message

import config
import sys

def read(text):

    if text.startswith(config.trigger):
        message = text[1:].split(" ")
        valid = 0
        for module in config.imported:
            if message[0] in sys.modules[module].includes.keys():
                valid = 1
                i = 1 
                pack = sys.modules[module].includes[message[0]]
                for word in message[i:]:
                    if word in pack.parameters.keys():
                        pack = pack.parameters[word]
                        i += 1
                if ' '.join(message[i:]) == "help":
                    print(pack.help())
                else:
                    pack.execute(message[i:])

        if valid == 0:
            print("Invalid command!")

if __name__ == "__main__":
    print("Don't use this as a main!")
