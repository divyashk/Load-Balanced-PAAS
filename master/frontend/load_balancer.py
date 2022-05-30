import os
from signal import SIGTERM
from flask import Flask, jsonify, request
import sys
import multiprocessing
from tinydb import TinyDB, Query
from tinydb.table import Document

app = Flask(__name__)
manager = multiprocessing.Manager()

WORKING_MACHINES = manager.list()
WORKING_INSTANCES = manager.dict()
GLOBAL_VARS = manager.dict()

lock = multiprocessing.Lock()

db = TinyDB('load_balancer.json')

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


def create_instance():
    # tuple -> success, instance_id or error
    global lock
    global GLOBAL_VARS
    global WORKING_INSTANCES

    try:
        fork_id = os.fork()
    except:
        return False, "Fork failed!"

    if fork_id > 0:
        lock.acquire()
        instance_id = "localhost:" + str(GLOBAL_VARS["CURRENT_PORT"])
        lock.release()
        return True, instance_id
    else:
        print("Child process and id is : ", os.getpid())
        process_pid = os.getpid()

        lock.acquire()
        current_port = GLOBAL_VARS["CURRENT_PORT"]
        print("Start an instance_port: ", current_port)

        # Instead start a new python app, TODO
        # os.system("python instance.py " + str(current_port))
        instance_id = "localhost:" + str(current_port)
        WORKING_INSTANCES[instance_id] = process_pid
        GLOBAL_VARS["CURRENT_PORT"] += 1
        lock.release()

        sys.argv = ["instance.py", str(current_port)]
        script = open("instance.py")
        code = script.read()
        # set the arguments to be read by script.py
        exec(code)

        return True, instance_id


def delete_instance(instance_id):
    global WORKING_INSTANCES
    global lock

    lock.acquire()
    if instance_id not in WORKING_INSTANCES:
        lock.release()
        return False, "No such instance exists!"

    instance_pid = WORKING_INSTANCES[instance_id]
    os.kill(instance_pid, SIGTERM)
    WORKING_INSTANCES.pop(instance_id)
    lock.release()

    return True, instance_id


@app.route('/')
def index():
    global WORKING_INSTANCES

    return jsonify(success=True, WORKING_INSTANCES=str(WORKING_INSTANCES))


@app.route('/deploy_application')
def create_instance_api():
    request_body = request.args
    req_fields = ["user_password", "user_id"]
    for req_field in req_fields:
        if req_field not in request_body:
            return jsonify(success=False, error=str(req_field) + " not provided!")

    success_status, instance_or_error = create_instance()
    if success_status:
        return jsonify(success=True, instance_id=instance_or_error)
    return jsonify(success=False, error=instance_or_error)


@app.route('/delete_instance')
def delete_instance_api():
    if "instance_id" not in request.args:
        return jsonify(success=False, error="instance_id not provided")

    instance_id = request.args["instance_id"]
    success_status, instance_or_error = delete_instance(instance_id)
    if success_status:
        return jsonify(success=True, instance_id=instance_or_error)
    return jsonify(success=False, error=instance_or_error)


def __init__():
    global GLOBAL_VARS
    global lock

    START_PORT = 5002
    MACHINES = ["192.168.9.125", "127.0.0.1"]

    lock.acquire()
    global_vars = db.table("global_vars")
    global_vars_object = global_vars.get(doc_id=0)
    if global_vars_object is None:
        global_vars.insert(Document({ "port" : START_PORT }, doc_id=0))
        GLOBAL_VARS["CURRENT_PORT"] = START_PORT
    else:
        if "port" not in global_vars_object:
            global_vars.insert(Document({ "port" : START_PORT }, doc_id=0))
            GLOBAL_VARS["CURRENT_PORT"] = START_PORT
        else:
            GLOBAL_VARS["CURRENT_PORT"] = global_vars_object["port"]

    for machine in MACHINES:
        WORKING_MACHINES.append()
    lock.release()


if __name__ == "__main__":
    __init__()
    print("GLOBAL_VARS", GLOBAL_VARS)
    app.run(port=4999)
