from socket import *
import threading
from queue import Queue
import multiprocessing
import re
import os
import logging

from worker import md5_worker, style


IP = "127.0.0.1"
PORT = 9090
ADDR = (IP, PORT)
SIZE = 1024
FORMAT = 'utf-8'

# Number of workers and mistakes they received
WORKER_NUMBER = 5
mistakes = [0 for _ in range(WORKER_NUMBER)]


def worker_live_preserver(i,):
    """
    A function to keep the worker alive
    """
    while True:
        globals()["worker%s" % i] = multiprocessing.Process(
            target=md5_worker, args=(i,))
        globals()["worker%s" % i].start()
        print(style.YELLOW + f"worker {i} started" + style.RESET)
        logger.info(f"worker {i} started")
        # Waits for the processing to finish
        globals()["worker%s" % i].join()


def commander_handling(conn, convert_queue):
    connected = True

    # Repeat this loop until the connection between server and commander
    # is established and connected is True
    while connected:
        # Receive a message from the commander
        message = conn.recv(SIZE).decode(FORMAT)

        # Extraction of file address and request type
        file_address, request_type = message.split(" ")

        # Get pure file name for logging
        file_name = re.findall(r'[0-9]*.json', file_address).pop()

        """
        If the value of the request_type variable was 1,
        it means that the commander wants the md5 file to be created
        by the server (worker) so that the commander can
        check the correctness of its content later.
        
        But if the value of the request_type variable was 0,
        it means that the commander has recognized
        the incorrectness of the md5 content of that file and tells
        the server to fine the worker who calculated its md5 content.
        """
        if request_type == "1":
            logger.info(f"The request to create {file_name}.md5 was received")
            print(f"The request to create {file_name}.md5 was received")

            # Add the file address to the queue of file server addresses
            convert_queue.put(file_address)

            # Send the "Received" response message to the commander
            conn.send("Recieved".encode(FORMAT))

        elif request_type == "0":
            logger.info(f"{file_name}.md5 report request received")
            print(f"{file_name}.md5 report request received")

            # Search amoung the worker_log_X files
            # and find the worker who calculated this md5 content
            # and put the ID of the worker who made the mistake
            # in the workerId variable
            for workerId in range(1, WORKER_NUMBER+1):
                if not os.path.isfile("./worker_log_%s.log" % workerId):
                    continue
                f = open("./worker_log_%s.log" % workerId, "r")
                text = str(f.read())
                file_name = re.findall(r'[0-9]*.json', file_address).pop()
                if re.findall(r'%s was converted to %s.md5' % (file_name, file_name), text):
                    f.close()
                    break
                f.close()

            # Add one to the mistakes of this worker
            mistakes[workerId-1] += 1
            message = f"{workerId} {mistakes[workerId-1]}"

            # If this worker makes its second mistake,
            # kill him and reduce the amount of his mistakes to zero
            if mistakes[workerId-1] == 2:
                if globals()["worker%s" % workerId].is_alive():
                    globals()["worker%s" % workerId].kill()
                    logger.critical("worker %s killed !!!" % workerId)
                    print("worker %s killed !!!" % workerId)
                mistakes[workerId-1] = 0

            # Send the response message containing the ID and number of mistakes
            # of the worker who made this mistake to the commander
            conn.send(message.encode(FORMAT))


def worker_handling(conn, id, convert_queue):
    connected = True

    # Repeat this loop until the connection between server and worker
    # is established and connected is True
    while connected:

        # The address of the files we want to give to the worker to create the md5 file
        file_addresses = ""
        for _ in range(5):
            # Getting an address from the server's address queue
            file_addresses += convert_queue.get(block=True) + " "
            if convert_queue.empty():
                break
        file_addresses = file_addresses.strip()

        try:
            # Send the addresses to the worker
            conn.send(file_addresses.encode(FORMAT))

            # Wait for the worker's response
            conn.recv(SIZE).decode(FORMAT)

        # If the connection is terminated and the worker process is killed
        except ConnectionResetError:
            # Set connected to False, so we exit the loop
            connected = False

            logger.error(f"NOT SUCCESS worker {id} for {file_addresses}")
            print(f"NOT SUCCESS worker {id} for {file_addresses}")

            # We will once again add the address of the files
            # that were sent when the worker was killed to the queue
            for item in file_addresses.split(" "):
                convert_queue.put(item)


def server():
    # Create a server socket
    s = socket(AF_INET, SOCK_STREAM)
    s.bind(ADDR)

    logger.info("[STARTING] server is listening ....")
    print("[STARTING] server is listening ....")

    # Make socket ready for accepting connection
    s.listen()

    # A queue to add the address of the files whose md5 file should be created
    convert_queue = Queue()

    while True:
        # Wait for the client to connect to the server
        conn, addr = s.accept()

        # Wait for the client to introduce itself
        introduction_msg = conn.recv(SIZE).decode(FORMAT)

        # If the client was a worker, create a thread to handle it
        if re.match(r"worker [0-9]*", introduction_msg):
            worker_id = introduction_msg.split(" ")[1]
            thread = threading.Thread(
                target=worker_handling, args=(conn, worker_id, convert_queue))

        # If the client was a commander, create a thread to handle it
        if introduction_msg == "commander":
            thread = threading.Thread(
                target=commander_handling, args=(conn, convert_queue))

        # Start the thread
        thread.start()


if __name__ == "__main__":

    # Logging configuration
    logging.basicConfig(filename="server.log", format='%(asctime)s.%(msecs)03d - %(message)s',
                        datefmt='%H:%M:%S', filemode='w', encoding='utf-8')

    # Create a logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # Creating threads to control worker processes
    [threading.Thread(target=worker_live_preserver, args=(i,)).start()
     for i in range(1, WORKER_NUMBER+1)]

    # Start the server
    server()
