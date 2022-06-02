import json
import os
import socket
from _thread import *

ServerSideSocket = socket.socket()
ThreadCount = 0

HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
PORT = 8081  # Port to listen on (non-privileged ports are > 1023)

try:
    ServerSideSocket.bind((HOST, PORT))
except socket.error as e:
    print(str(e))

print('Socket is listening..')
ServerSideSocket.listen(5)

def multi_threaded_client(conn):
    while True:
        data = json.loads(conn.recv(1024).decode())
        if not data:
            break

        cmd = data["cmd"]
        print(cmd)

        output = ""
        cwd = os.getcwd()
        if "cwd" in data:
            cdd = data["cwd"]
            if cdd != "":
                os.chdir(cdd)
            output = os.popen(cmd).read()
            os.chdir(cwd)
        else:
            output = os.popen(cmd).read()

        if output == "":
            conn.sendall("Done!".encode())

        conn.sendall(output.encode())

    conn.close()

while True:
    Client, address = ServerSideSocket.accept()
    print('Connected to: ' + address[0] + ':' + str(address[1]))
    start_new_thread(multi_threaded_client, (Client, ))
    ThreadCount += 1
    print('Thread Number: ' + str(ThreadCount))

ServerSideSocket.close()
