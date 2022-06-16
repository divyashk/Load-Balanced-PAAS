
import json
import socket

HOST = "192.168.196.27"  # The server's hostname or IP address
PORT = 8081  # The port used by the server

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    
    CWD = ""
    while(True):
        inp = input("priyam$ ")

        if inp == "exit" or inp == "quit":
            s.close()
            break

        if (inp != ""):
            obj = {
                "cmd" : inp,
                "cwd" : CWD
            }

            cmds = inp.split(" ")
            if cmds[0] == "cd":
                if len(cmds) > 1:
                    # To directory
                    CWD += cmds[1] + "/"
                else:
                    CWD = ""
            else:

                s.sendall(str(json.dumps(obj)).encode())
                data = s.recv(1024).decode()
                print(data)

