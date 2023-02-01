from socket import *
import threading
from queue import LifoQueue
import logging
import os
import json
import hashlib
import re


class style():
    RED = '\033[31m'
    RESET = '\033[0m'


IP = "127.0.0.1"
PORT = 9090
ADDR = (IP, PORT)
SIZE = 1024
FORMAT = 'utf-8'

CKECKER_NUMBER = 5

# connect to the server that is running on this IP and port
s = socket(AF_INET, SOCK_STREAM)
s.connect(ADDR)


def file_address_extractor(basepath):
    """
    A function to extract the addresses of the files located in basepath path
    """
    # os.listdir(basepath) get a list of all files and directories
    # that are in basepath
    for entry in os.listdir(basepath):

        # If entry is file
        if os.path.isfile(os.path.join(basepath, entry)):
            # If the file type is md5 skip it
            # else put the file address in the commander's check queue
            if re.match(r'[0-9]*.json.md5', entry):
                continue
            else:
                ckeck_queue.put(os.path.join(basepath, entry))

        # Else if entry is folder(directory)
        # then call the function one more time with this path
        elif os.path.isdir(os.path.join(basepath, entry)):
            file_address_extractor(os.path.join(basepath, entry))


def message_sender():
    """
    A function to send messages.

    The priority is to send error report messages,
    and until the queue is empty,
    it will not start sending md file creation messages. This cycle repeats
    """
    while True:

        while not mistake_report_queue.empty():

            # A message is sent to the server along with the address
            # of the file whose md5 content is wrong
            message = mistake_report_queue.get()
            s.send(message.encode(FORMAT))

            # It waits for a response from the server,
            # which includes the ID and number of errors of the worker
            # who made the mistake
            bad_worker, warning = s.recv(SIZE).decode().split(" ")

            # logging the mistake information
            file_address = message.split(" ")[0]
            if warning == "1":
                mistake = "first mistake"
            elif warning == "2":
                mistake = "second mistake, so its killed"
            logger.info(
                f"Worker {bad_worker} made a mistake in creating the content of {file_address}.md5 and it is its {mistake}")

        if not must_create_queue.empty():
            # Sending the message of creating md5 file to the server
            # and receiving its response
            message = must_create_queue.get()
            s.send(message.encode(FORMAT))
            s.recv(SIZE)


def md5_content_checker(id):

    while True:
        # Getting the address of a file from the check queue
        file_address = ckeck_queue.get()

        # Getting the addresses of all files from the check queue
        file_addresses = list(ckeck_queue.queue)

        # If the file was not md5
        if file_address[-4:] != ".md5":

            # If the md5 file of this file is in the ckeck_queue
            if f"{file_address}.md5" in file_addresses:
                print(
                    f"I am ckecker {id} for check {file_address}.md5 content and existent is True")

                # Wait until it has been created by the worker
                # (or already exists among the server files)
                while not os.path.isfile(f"{file_address}.md5"):
                    pass

                # Open the md5 file and read its contents
                md5_file = open(f"{file_address}.md5")
                md5_file_content = md5_file.read()
                md5_file.close()

                # Open the original file and calculate its md5 content
                not_md5_file = open(f"{file_address}")
                correct_md5_content = str(
                    json.load(not_md5_file)).encode()
                correct_md5_content = hashlib.md5(
                    correct_md5_content).hexdigest()
                not_md5_file.close()

                # If the md5 content calculated by the commander is not equal
                # to the content of the md5 file,
                # add the file address to the check queuet
                if not str(correct_md5_content) == md5_file_content:
                    print(
                        style.RED + f"The md5 content {file_address} is wrong" + style.RESET)

                    mistake_report_queue.put(f"{file_address} 0")

            # If the md5 file of this file is not in the ckeck_queue
            else:
                print(f"I am ckecker {id} for check {file_address}.md5 and existent is", os.path.isfile(
                    f"{file_address}.md5"))

                # If its md5 file does not exist
                # then add it to must_create_queue
                if not os.path.isfile(f"{file_address}.md5"):
                    must_create_queue.put(f"{file_address} 1")

                # Add the file address and its md5 file address to the ckeck_queue
                ckeck_queue.put(f"{file_address}.md5")
                ckeck_queue.put(file_address)


def say_i_am_commander():
    s.send("commander".encode(FORMAT))


if __name__ == "__main__":

    # Logging configuration
    logging.basicConfig(filename="./commander_log.log", format='%(asctime)s.%(msecs)03d - %(message)s',
                        datefmt='%H:%M:%S', filemode='w', encoding='utf-8')

    # Create a logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # Commander check queue
    ckeck_queue = LifoQueue()

    # Queue to send mistake reports
    mistake_report_queue = LifoQueue()

    # Queue to send create request
    must_create_queue = LifoQueue()

    # Create thread to introduce the commander to the server and start it
    t1 = threading.Thread(target=say_i_am_commander)
    t1.start()

    # Wait until the thread is finished
    t1.join()

    # Make a thread to extract the addresses of the files
    threading.Thread(target=file_address_extractor,
                     args=(".\TransactionFiles", )).start()

    # Make threads to check md5 content and start them
    [threading.Thread(target=md5_content_checker, args=(i,)).start()
     for i in range(1, CKECKER_NUMBER+1)]

    # Create a thread to send messages and start it
    threading.Thread(target=message_sender).start()
