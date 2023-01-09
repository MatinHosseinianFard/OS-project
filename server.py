from socket import *
import os
import threading
from threading import Lock

import multiprocessing
from worker import md5_worker

IP = "127.0.0.1"
PORT = 9090
ADDR = (IP, PORT)
SIZE = 1024
FORMAT = 'utf-8'


def worker(i):

    globals()["worker%s" % i] = multiprocessing.Process(target=md5_worker, args=(i))
    globals()["worker%s" % i].start()
    while True:
        if not globals()["worker%s" % i].is_alive():
            globals()["worker%s" % i].kill()
            globals()["worker%s" % i] = multiprocessing.Process(
                target=md5_worker, args=(1))
            globals()["worker%s" % i].start()


def client_handling(conn, addr):
    print(addr, " is connected to the server")
    connected = True

    while connected:
        menu = "\n1. Show files on the server\n" + \
            "2. Give me the address of the files you want to convert to md5\n" + \
            "3. Disconnect\n" + "\nChoose : "

        conn.send(menu.encode(FORMAT))

        request = int(conn.recv(SIZE).decode(FORMAT))
        if request == 1:
            files_name = get_files_name("./TransactionFiles")
            conn.send(files_name.encode(FORMAT))

        elif request == 2:
            files_name = conn.recv(SIZE).decode(FORMAT)
            for file_name in files_name.split(" "):
                files_address.append(file_name)
            # for i, file_name in enumerate(files_name.split(" ")):
            #     globals()["job_queue_%s" % ((i % 2)+1)].put(file_name)
            # conn.send(files_name.encode(FORMAT))

        elif request == 3:
            connected = False
            
    conn.close()
        

def worker_handling(conn, addr):
    # print(addr, " is connected to the server")
    connected = True
    while connected:
            files_name = ""
            files_address_lock.acquire()
            while True:
                if len(files_address) != 0:
                    split = 2 if len(files_address) >= 2 else len(files_address)
                    for _ in range(split):
                        files_name += files_address.pop() + " "
                    files_name = files_name.strip()
                    files_address_lock.release()
                    # sleep(1)
                    conn.send(files_name.encode(FORMAT))
                    try:
                        message = conn.recv(SIZE).decode(FORMAT)
                    except:
                        pass
                    print(message)
                    break            
            
def get_files_name(basepath):
    files_name = ""
    # List all files in a directory using os.listdir
    for entry in os.listdir(basepath):
        if os.path.isfile(os.path.join(basepath, entry)):
            files_name += f"\n{entry}"
    
    return files_name


def start():
    # Serevr Socket INITIATE
    s = socket(AF_INET, SOCK_STREAM)
    s.bind(ADDR)
    print("[STARTING] server is listening ....")
    s.listen()
    while True:
        conn, addr = s.accept()
        name = conn.recv(SIZE).decode(FORMAT)
        if name == "worker":
            thread = threading.Thread(target=worker_handling, args=(conn, addr))
        if name == "client":
            thread = threading.Thread(target=client_handling, args=(conn, addr))
        thread.start()
        print("[ACTIVE CONNECTIONS]", threading.activeCount() - 1)


if __name__ == "__main__":
    # files_address = [f'{i}.json' for i in range(1, 10)]
    files_address = []
    files_address_lock = Lock()
    workers = [threading.Thread(target=worker, args=(i, )).start() for i in range(1, 6)]
    start()
