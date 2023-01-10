from socket import *
import os
import threading
from threading import Lock
from queue import Queue
from time import sleep
import multiprocessing
from worker import md5_worker

IP = "127.0.0.1"
PORT = 9090
ADDR = (IP, PORT)
SIZE = 1024
FORMAT = 'utf-8'

def worker(i):

    globals()["worker%s" % i] = multiprocessing.Process(
        target=md5_worker, args=(i, ))
    globals()["worker%s" % i].start()
    while True:
        if not globals()["worker%s" % i].is_alive():
            print("!!!!!!!")
            
            globals()["worker%s" % i].kill()
            globals()["worker%s" % i] = multiprocessing.Process(
                target=md5_worker, args=(i, ))
            globals()["worker%s" % i].start()
            break

def workerBlock(job_queue):
    warnings = [0 for i in range(5)]
    while True:
        mistake_file = job_queue.get(block=True)
        f = open("./log.txt", "r")
        text = str(f.read()).strip().split()
        warnings[int(text[text.index(mistake_file) + 1])-1] += 1
        print(warnings)
        if warnings[int(text[text.index(mistake_file) + 1])-1] == 2:
            globals()["worker%s" % int(text[text.index(mistake_file) + 1])].kill()
            warnings[int(text[text.index(mistake_file) + 1])-1] = 0
        
    
def client_handling(conn, addr):
    print(addr, " is connected to the server")
    connected = True

    while connected:
        # recieve_address_lock.acquire()
        file_name = conn.recv(SIZE).decode(FORMAT).split(" ")
        conn.send("Recieved".encode(FORMAT))
        print(file_name)
        if file_name[1] == "1":
        # print(file_name)
            files_address.put(file_name[0])
        # recieve_address_lock.release()
        else:
            job_queue.put(file_name[0])
    conn.close()


def worker_handling(conn, addr, id):
    # print(addr, " is connected to the server")
    connected = True
    while connected:
        files_name = ""
        files_address_lock.acquire()
        while True:
            if not files_address.empty():
                split = 2 if files_address.qsize() >= 2 else files_address.qsize()
                for _ in range(split):
                    files_name += files_address.get() + " "
                files_name = files_name.strip()
                files_address_lock.release()
                # sleep(1)
                try:
                    send_address_lock.acquire()
                    conn.send(files_name.encode(FORMAT))
                    send_address_lock.release()
                except:
                    send_address_lock.release()
                    print(f"NOT SUCCESS worker {id} for {files_name}")
                # message = conn.recv(SIZE).decode(FORMAT)
                # print(message)
                # message = message.split(" ")
                # if message[-4] == "successful":
                #     f = open("./log.txt")
                #     text = message[-6] + message[-1]
                #     f.write(text)
                #     f.close()
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
        if name[:6] == "worker":
            print(f"worker {name[-1]} started")
            thread = threading.Thread(
                target=worker_handling, args=(conn, addr, name[-1]))
        if name == "client":
            print(name)
            thread = threading.Thread(
                target=client_handling, args=(conn, addr))
        thread.start()
        print("[ACTIVE CONNECTIONS]", threading.activeCount() - 1)


if __name__ == "__main__":
    # files_address = [f'{i}.json' for i in range(1, 10)]
    files_address = Queue()
    files_address_lock = Lock()
    send_address_lock = Lock()
    workers = [threading.Thread(target=worker, args=(i, )).start()
               for i in range(1, 6)]
    job_queue = Queue()
    t1 = threading.Thread(target=workerBlock, args=(job_queue, ))
    t1.start()
    start()
