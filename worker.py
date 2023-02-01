import hashlib
import json
from socket import *
import os
import random
import re
import logging


class style():
    RED = '\033[31m'
    GREEN = '\033[32m'
    RESET = '\033[0m'
    YELLOW = '\033[33m'


def md5_worker(id):
    # Logging configuration
    logging.basicConfig(filename="./worker_log_%s.log" % id, format='%(asctime)s.%(msecs)03d - %(message)s',
                        datefmt='%H:%M:%S', filemode='a', encoding='utf-8')

    # Create a logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    IP = "127.0.0.1"
    PORT = 9090
    ADDR = (IP, PORT)
    SIZE = 1024
    FORMAT = 'utf-8'

    MISTAKE_RATE = random.random()

    # Connect to the server
    s = socket(AF_INET, SOCK_STREAM)
    s.connect(ADDR)

    # The worker introduces tiself to the server
    s.send(f"worker {id}".encode(FORMAT))
    while True:

        # The worker waits to receive the address of the files from the server
        # to create the md5 file of them
        files_name = s.recv(SIZE).decode(FORMAT)
        files_name.strip()

        for file_name in files_name.split(" "):

            # If there is a file with this address, calculate its md5 content
            if os.path.isfile(f"{file_name}"):
                not_md5_file = open(f"{file_name}")
                not_md5_content = str(json.load(not_md5_file)).encode()
                md5_content = hashlib.md5(not_md5_content).hexdigest()
                not_md5_file.close()

                # Get pure file name for logging
                pure_file_name = re.findall(r'[0-9]*.json', file_name).pop()
                logger.info(
                    f"{pure_file_name} was converted to {pure_file_name}.md5")

                # Creating its md5 file
                md5_file = open(f"{file_name}.md5", "w")

                # If random.random() < MISTAKE_RATE
                # then Write the incorrect md5 content calculated in it
                if random.random() < MISTAKE_RATE:
                    md5_file.write(md5_content + " BUG")
                    print(style.RED +
                          f"Deliberate mistake in {file_name}" + style.RESET)

                # Else Write the correct md5 content calculated in it
                else:
                    md5_file.write(md5_content)
                md5_file.close()

                message = style.GREEN + \
                    f"converting {file_name} by worker {id}\n" + style.RESET
                print(message)

            # If file Does not exist
            else:
                message = style.RED + \
                    f"{file_name} Does not exist!\n" + style.RESET
                print(message)

        # Send response to server
        s.send(message.encode(FORMAT))
