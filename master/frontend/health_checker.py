import os
from signal import SIGTERM
from time import sleep
from flask import Flask, jsonify, request
import sys
import multiprocessing
import requests
from tinydb import TinyDB, Query
from socket import socket

app = Flask(__name__)
manager = multiprocessing.Manager()

APP_NAME = ""

'''
In the database, store it like this?
app_name: {
    docker_image: docker_image,
    external_ip: ip_address assigned to this for accessing "ip:port",
    instances: ["instance_ip_addr"]
    machines: {
        "MachineIPAddr" : [Port of instance_id],
    }
    workers: {
        # TODO, will be here
    }
}
'''

def get_freeport():
    freeport = ""
    with socket() as s:
        s.bind(('', 0))
        freeport = s.getsockname()[1]
    return freeport


def start_health_check_app():
    global APP_NAME

    app_db = TinyDB("databases/app_" + APP_NAME + ".json")
    instances = app_db.table("instances").all()

    for i in range(2):
        if len(instances) == 1:
            # check if need to increase the load
            instance_id = instances[0]["instance_id"]
            machine_url = instances[0]["machine_url"]

            try:
                res = requests.get("http://localhost:8080/load")
                if res.ok:
                    print(res.text)
            except Exception as err:
                print("Error for Load came: ", err)
        else:
            # instances length 2, check if need to decrease the load
            print("TODO")
        # for instance in instances:
        #     print("Instance: ", instance)

            # Start a new thread for keep checking the instance
            # Right now it will work only considering two machines
        # Left TODO, will not be doing this idea forward

        sleep(3)
    

@app.route('/')
def index():
    return 'Hello HEALTH CHECKER'


if __name__ == "__main__":
    # Arguments app_name

    if len(sys.argv) > 1:
        APP_NAME = sys.argv[1]
        start_health_check_app()

        app.run(port="5010", host="0.0.0.0")
    else:
        print("Provide app_name in the argument")
