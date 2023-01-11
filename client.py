from socket import *
import threading
from queue import Queue, LifoQueue
from collections import deque
from time import sleep
import os
import json
import hashlib
import time
from worker import style

IP = "127.0.0.1"
PORT = 9090
ADDR = (IP, PORT)
SIZE = 1024
FORMAT = 'utf-8'


s = socket(AF_INET, SOCK_STREAM)
s.connect(ADDR)
globalLock = threading.Lock()
globalLock2 = threading.Lock()

files_name = []


def fileGetter():
    first_files_name = get_files_name("./TransactionFiles").split()
    for file_name in first_files_name:
        n_md5.put(file_name)
        
def sender():
    while True:
        
        while not mistake_send.empty():
            print("mistake_send")
            must_send = mistake_send.get()
            file_name = must_send.split(" ")[0]
            s.send(must_send.encode(FORMAT))
            bad_worker, warning = s.recv(SIZE).decode().split(" ")
            mistake = ""
            if warning == "1":
                mistake = "first mistake"
            elif warning == "2":
                mistake = "second mistake, so its killed"
            f = open("./client_log.txt", "a")
            log = f"Worker {bad_worker} made a mistake in creating the content of {file_name}.md5 and it is its {mistake}\n"
            f.write(log)
            f.close()
        
        # while not true_send.empty():
        #     must_send = true_send.get()
        #     s.send(must_send.encode(FORMAT))
        #     print(s.recv(SIZE).decode())
        
        if not create_send.empty():
            print("create_send")
            must_send = create_send.get(block=False)
            # sleep(1)
            s.send(must_send)
            s.recv(SIZE)


def checker(id):
    while True:
        file_name = n_md5.get(block=True)

        # globalLock.acquire()
        files_name = list(n_md5.queue)
        # globalLock.release()    
        if file_name[-3:] != "md5":

            not_md5_file = open(f"./TransactionFiles/{file_name}")
            if f"{file_name}.md5" in files_name:
                print(f"I am ckecker {id} for check {file_name}.md5 content")
                while not os.path.isfile(f"./TransactionFiles/{file_name}.md5"):
                    pass
                md5_file = open(f"./TransactionFiles/{file_name}.md5")

                md5_file_content = md5_file.read()
                md5_file.close()

                check_md5_file_content = str(
                    json.load(not_md5_file)).encode()
                check_md5_file_content = hashlib.md5(
                    check_md5_file_content).hexdigest()

                if not str(check_md5_file_content) == md5_file_content:
                    print(
                        style.RED + f"The md5 content {file_name} is wrong" + style.RESET)
                    # globalLock2.acquire()
                    # s.send(f"{file_name} 0".encode(FORMAT))
                    mistake_send.put(f"{file_name} 0")
                    
                    # globalLock2.release()
                else:
                    print("True")
                    # true_send.put(f"{file_name} 3")
                not_md5_file.close()

            else:
                print(f"I am ckecker {id} for check {file_name}.md5 existent", os.path.isfile(
                    f"./TransactionFiles/{file_name}.md5"))

                if not os.path.isfile(f"./TransactionFiles/{file_name}.md5"):
                    # globalLock2.acquire()
                    # s.send(f"{file_name} 1".encode(FORMAT))
                    # print()
                    create_send.put(f"{file_name} 1".encode(FORMAT))
                    # s.recv(SIZE).decode()
                    # globalLock2.release()

                n_md5.put(f"{file_name}.md5")
                n_md5.put(file_name)


def send_request():
    s.send("client".encode(FORMAT))


def get_files_name(basepath):
    files_name = ""
    # List all files in a directory using os.listdir
    for entry in os.listdir(basepath):
        if os.path.isfile(os.path.join(basepath, entry)):
            files_name += f"\n{entry}"

    return files_name


if __name__ == "__main__":

    n_md5 = LifoQueue()
    md5 = LifoQueue()

    mistake_send = LifoQueue()
    create_send = LifoQueue()
    true_send = LifoQueue()
    
    t1 = threading.Thread(target=send_request)
    t1.start()
    sleep(0.1)

    t2 = threading.Thread(target=fileGetter)
    t2.start()
    checkers = [threading.Thread(
        target=checker, args=(i,)).start() for i in range(1, 6)]
    
    t3 = threading.Thread(target=sender)
    t3.start()
    
