import hashlib
import json
from socket import *
from time import sleep
import os
import random
import time
class style():
    RED = '\033[31m'
    GREEN = '\033[32m'
    RESET = '\033[0m'

def md5_worker(id):
    IP = "127.0.0.1"
    PORT = 9090
    ADDR = (IP, PORT)
    SIZE = 1024
    FORMAT = 'utf-8'
    
    s = socket(AF_INET, SOCK_STREAM)
    s.connect(ADDR)
    s.send(f"worker{id}".encode(FORMAT))
    # sleep(0.1)
    while True:

        files_name = s.recv(SIZE).decode(FORMAT)
        message = f"I am worker {id} for converting : {files_name}\n"
        print(message)
        for file_name in files_name.split(" "):
            if os.path.isfile(f"./TransactionFiles/{file_name}"):
                not_md5_file = open(f"./TransactionFiles/{file_name}")
                not_md5_content = str(json.load(not_md5_file)).encode()
                not_md5_content = hashlib.md5(not_md5_content).hexdigest()
                not_md5_file.close()

                md5_file = open(f"./TransactionFiles/{file_name}.md5", "w")
                if random.random() < 0.5:
                    md5_file.write(not_md5_content + " BUG")
                    print(style.RED + f"Mistake in {file_name}" + style.RESET )
                else:
                    md5_file.write(not_md5_content)
                md5_file.close()
                log_file_update = open("./log.txt", "a")
                text = f"{file_name} {id}\n"
                log_file_update.write(text)
                log_file_update.close()
                message += style.GREEN + f"converting {file_name} was successful by worker {id}\n" + style.RESET
            else:
                message += style.RED + f"{file_name} Does not exist!\n" + style.RESET
        print(message)
        # s.send(message.encode(FORMAT))
