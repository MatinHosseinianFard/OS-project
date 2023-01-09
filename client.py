from socket import *
import os

IP = "127.0.0.1"
PORT = 9090
ADDR = (IP, PORT)
SIZE = 1024
FORMAT = 'utf-8'

s = socket(AF_INET, SOCK_STREAM)
s.connect(ADDR)


def send_request():
    s.send("client".encode(FORMAT))
    while True:
        # menu = s.recv(SIZE).decode(FORMAT)
        # print(menu, end='')

        request = input()
        s.send(request.encode(FORMAT))

        if request == "1":
            response = '\n\033[93m------'
            response += s.recv(SIZE).decode(FORMAT) + "\n------\033[0m\n"
            print(response)

        elif request == "2":
            files_name = input("txt files name : ")
            files_name = files_name.split(" ")
            content = ""
            for file_name in files_name:
                if file_name[-5:] == ".json":
                    content += file_name + " "
                else:
                    content += file_name + ".json" + " "
            
            s.send(content.strip().encode(FORMAT))

        elif request == "3":
            break


def get_files_name(basepath):
    files_name = ""
    # List all files in a directory using os.listdir
    for entry in os.listdir(basepath):
        if os.path.isfile(os.path.join(basepath, entry)):
            files_name += f"\n{entry}"

    return files_name


if __name__ == "__main__":
    send_request()
    s.close()
