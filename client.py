from socket import *
import threading
import os
import json
import hashlib

IP = "127.0.0.1"
PORT = 9090
ADDR = (IP, PORT)
SIZE = 1024
FORMAT = 'utf-8'

s = socket(AF_INET, SOCK_STREAM)
s.connect(ADDR)



# def fileGetter():
#     pass


def checker(file_name):
    
    not_md5_file = open(f"./TransactionFiles/{file_name}")
    
    if f"{file_name}.md5" in files_name:
        md5_file = open(f"./TransactionFiles/{file_name}.md5")
        md5_file_content = md5_file.read()
        md5_file.close()
        
        check_md5_file_content = str(json.load(not_md5_file)).encode()
        check_md5_file_content = hashlib.md5(check_md5_file_content).hexdigest()
        
        print(str(check_md5_file_content) == md5_file_content)
        not_md5_file.close()
    else:
        pass
    
    
def send_request():
    s.send("client".encode(FORMAT))
    while True:
        menu = s.recv(SIZE).decode(FORMAT)
        print(menu, end='')

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
    files_name = get_files_name("./TransactionFiles").split()
    files_name.sort(key=lambda item: item[-1], reverse=True)
    print(files_name)
    checker(files_name[1])
    send_request()
    s.close()
