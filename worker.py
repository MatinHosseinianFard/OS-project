import hashlib
import json
from socket import *
from time import sleep
import os

class style():
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    UNDERLINE = '\033[4m'
    RESET = '\033[0m'

def md5_worker(id, l):
    IP = "127.0.0.1"
    PORT = 9090
    ADDR = (IP, PORT)
    SIZE = 1024
    FORMAT = 'utf-8'
    
    s = socket(AF_INET, SOCK_STREAM)
    s.connect(ADDR)
    s.send("worker".encode(FORMAT))
    while True:
        # sleep(1)
        # l.acquire()
        # print("worker ", id, "got the lock")
        files_name = s.recv(SIZE).decode(FORMAT)
        # print("I am worker", id, "for converting : ", files_name)
        # l.release()
        # print("worker ", id, "release the lock", files_name)
        # files_name = files_name.split(" ")
        # os.listdir(basepath)
        # if files_name[0] != '':
        message = f"I am worker {id} for converting : {files_name}\n"
        for file_name in files_name.split(" "):
            if os.path.isfile(f"./TransactionFiles/{file_name}"):
                not_md5_file = open(f"./TransactionFiles/{file_name}")
                not_md5_content = str(json.load(not_md5_file)).encode()
                not_md5_content = hashlib.md5(not_md5_content).hexdigest()
                not_md5_file.close()

                md5_file = open(f"./TransactionFiles/md5/{file_name}.md5", "w")
                md5_file.write(not_md5_content)
                md5_file.close()
                message += style.GREEN + f"converting {file_name} was successful\n" + style.RESET
            else:
                message += style.RED + f"{file_name} Does not exist!\n" + style.RESET
        s.send(message.encode(FORMAT))
        # file_name = queue.get(block=True)
        # not_md5_file = open(f"TransactionFiles/{file_name}")
        # not_md5_content = str(json.load(not_md5_file)).encode()
        # not_md5_content = hashlib.md5(not_md5_content).hexdigest()
        # not_md5_file.close()

        # md5_file = open(f"TransactionFiles/{file_name}.md5", "w")
        # md5_file.write(not_md5_content)
        # md5_file.close()
        # print("I am worker", id, file_name)