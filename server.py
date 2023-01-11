from socket import *
import os
import threading
from threading import Lock
from queue import Queue
from time import sleep
import multiprocessing
from worker import md5_worker
import re
from worker import style

IP = "127.0.0.1"
PORT = 9090
ADDR = (IP, PORT)
SIZE = 1024
FORMAT = 'utf-8'


def worker(i):
    globals()["worker%s" % i] = multiprocessing.Process(
        target=md5_worker, args=(i, ))
    # z = psutil.Process(globals()["worker%s" % i].pid)

    globals()["worker%s" % i].start()
    while True:
        if not globals()["worker%s" % i].is_alive():
            # print("!!!!!!!")
            
            # globals()["worker%s" % i].terminate()
            globals()["worker%s" % i] = multiprocessing.Process(
                target=md5_worker, args=(i, ))
            globals()["worker%s" % i].start()
            # break


def client_handling(conn, files_address):
    connected = True
    warnings = [0 for i in range(5)]
    while connected:
        file_name = conn.recv(SIZE).decode(FORMAT).split(" ")
        print(file_name)
        if file_name[1] == "1":
            # worker_lock.acquire()
            files_address.put(file_name[0])
            # print(list(files_address.queue))
            conn.send("Recieved".encode(FORMAT))
            
        # elif file_name[1] == "3":
        #     conn.send("OK".encode(FORMAT))
        else:
            mistake_lock.acquire()
            f = open("./worker_log.txt", "r")
            text = str(f.read())
            # print(text)
            worker = re.findall(r'%s was converted to %s.md5 by worker \d' % (
                file_name[0], file_name[0]), text).pop()
            f.close()
            warnings[int(worker[-1])-1] += 1
            message = f"{worker[-1]} {warnings[int(worker[-1])-1]}"
            
            # print("ZZZ")
            # globals()["psutil%s" % int(worker[-1])].suspend()
            # print("ZZZ")
            print(warnings)
            kill_lock.acquire()
            if warnings[int(worker[-1])-1] == 2:   
                if globals()["worker%s" % int(worker[-1])].is_alive():
                    globals()["worker%s" % int(worker[-1])].kill()
                    print("worker%s killed!!!" % int(worker[-1]))
                warnings[int(worker[-1])-1] = 0
            # else:
                # print("ZZZ")
                # globals()["psutil%s" % int(worker[-1])].resume()
            kill_lock.release()
            conn.send(message.encode(FORMAT))
            mistake_lock.release()
    conn.close()


def worker_handling(conn, id, files_address):
    connected = True
    while connected:
        # while not globals()["worker%s" % id].is_alive():
        #     pass
        files_name = ""
        # test_lock.acquire()
        for _ in range(1):
            files_name += files_address.get(block=True) + " "
        # test_lock.release()
        files_name = files_name.strip()
        try:
            
            send_address_lock.acquire()
            conn.send(files_name.encode(FORMAT))
            conn.recv(SIZE).decode(FORMAT)
            # for _ in files_name.split(" "):
            #     mmm = conn.recv(SIZE).decode(FORMAT)
            #     print(mmm.split(" ")[1])
            send_address_lock.release()

        except:
            
            connected = False
            send_address_lock.release()
            print(f"NOT SUCCESS worker {id} for {files_name}")
            print(files_name.split(" "))
            for item in files_name.split(" "):
                files_address.put(item)
                # sleep(0)


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
    files_address = Queue()
    while True:
        conn, addr = s.accept()
        name = conn.recv(SIZE).decode(FORMAT)
        if name[:6] == "worker":
            print(style.YELLOW + f"worker {name[-1]} started" + style.RESET)
            thread = threading.Thread(
                target=worker_handling, args=(conn, name[-1], files_address))
        if name == "client":
            print(name)
            thread = threading.Thread(
                target=client_handling, args=(conn, files_address))
        thread.start()
        print("[ACTIVE CONNECTIONS]", threading.activeCount() - 1)


if __name__ == "__main__":

    files_address_lock = Lock()
    send_address_lock = Lock()
    mistake_lock = Lock()
    kill_lock = Lock() 
    workers = [threading.Thread(target=worker, args=(i, )).start()
               for i in range(1, 6)]
    
    job_queue = Queue()
    test_lock = Lock()
    worker_lock = Lock()
    sem = Lock()
    start()
