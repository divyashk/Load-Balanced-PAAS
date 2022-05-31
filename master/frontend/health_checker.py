import os
from signal import SIGTERM
from flask import Flask, jsonify, request
import sys
import multiprocessing
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
    app_db = TinyDB("databases/app_" + APP_NAME + ".json")
    instances = app_db.table("instances").all()

    
    if len(instances) == 1:
        instance_id = instances[0]["instance_id"]
        machine_url = instances[0]["machine_url"]
    else:
        # instances length 2
        
    # for instance in instances:
    #     print("Instance: ", instance)

        # Start a new thread for keep checking the instance
        # Right now it will work only considering two machines



@app.route('/')
def index():
    return 'Hello LOAD BALANCER'


if __name__ == "__main__":
    # Arguments app_name

    if len(sys.argv) > 1:
        APP_NAME = sys.argv[1]
        start_health_check_app()

        app.run(port=get_freeport(), host="0.0.0.0")
    else:
        print("Provide app_name in the argument")
