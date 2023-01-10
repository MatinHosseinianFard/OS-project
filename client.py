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
        job_queue.put(file_name)
    # while True:
    #     files_name = get_files_name("./TransactionFiles").split()
    #     for file_name in files_name:
    #         if file_name not in first_files_name:
    #             job_queue.put(file_name)


def checker(id):
    while True:
        # sleep(3)
        
        file_name = job_queue.get(block=True)
        
        globalLock.acquire()
        files_name = list(job_queue.queue)
        globalLock.release()
        # print(file_name)
        if file_name[-3:] != "md5":
            # print(f"I am ckecker {id} and check {file_name}")

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
                    globalLock2.acquire()
                    s.send(f"{file_name} 0".encode(FORMAT))
                    s.recv(SIZE).decode()
                    globalLock2.release()
                else:
                    print("True")
                not_md5_file.close()
                # else:
                #     job_queue.put(file_name)
                #     job_queue.put(f"{file_name}.md5")
            else:
                print(f"I am ckecker {id} for check {file_name}.md5 existent", os.path.isfile(f"./TransactionFiles/{file_name}.md5"))
                # while os.path.isfile(f"./TransactionFiles/{file_name}.md5"):
                #     while f"{file_name}.md5" not in list(job_queue.queue):
                #         pass
                # print("HI")
                if not os.path.isfile(f"./TransactionFiles/{file_name}.md5"):
                    globalLock2.acquire()
                    s.send(f"{file_name} 1".encode(FORMAT))
                    # print()
                    s.recv(SIZE).decode()
                    globalLock2.release()
                
                job_queue.put(f"{file_name}.md5")
                job_queue.put(file_name)
                
               


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

    # job_queue = Queue()
    # job_queue_2 = Queue()
    job_queue = LifoQueue()
    # print(files_name)
    # send_request()
    t1 = threading.Thread(target=send_request)
    t1.start()
    sleep(0.1)

    t2 = threading.Thread(target=fileGetter)
    t2.start()
    checkers = [threading.Thread(
        target=checker, args=(i,)).start() for i in range(1, 6)]
    # for i in checkers:
    #     i.start()

    # s.close()
