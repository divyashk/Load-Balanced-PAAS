from time import sleep
from flask import Flask, jsonify, request
import os
import requests
import multiprocessing
from tinydb import TinyDB
from app import create_an_instance()

app = Flask(__name__)
manager = multiprocessing.Manager()

# stores the list of instances that are currently working
WORKING_WORKERS = manager.dict()
lock = multiprocessing.Lock()

MASTER_BACKEND = "http://localhost:4998"
PERIODIC_INTERVAL = 5 # The seconds interval on which we will keep checking if the instance is working or not


def test_instance(instance_url):
    ''' Makes a get request to the instance url, and return True if it is working '''
    print("Testing instance url: ", instance_url)

    try:
        res = requests.get(instance_url)
        if res.ok:
            return True
        else:
            return False
    except requests.exceptions.InvalidSchema:
        try:
            requests.get("http://" + str(instance_url))
        except:
            return False

    except requests.ConnectionError:
        return False

    return True


def create_instance(app_name):
    # 1. Will make a request to create an instanc for the app with app_name
    # 2. Creates another Worker
    # Returns a tuple(Success_Status, instance_id or error)

    print("Automatic instance creation for the app_name", app_name, " started!")
    success_status, instance_url_or_error = create_an_instance(app_name)

    if success_status:
        # Now create another worker for this todo
        # call create_worker(app_name, instance_id)
        print("Create a worker")
    else:
        print("Instance creation failed")



def delete_instance(instance_id):
    # Make a request to the master backend to delete the instance of app_name
    # Worker will be already deleted as it will throw
    # Returns a tuple(Success_Status, instance_id or error)
    # TODO, make an API call to resource manager to delete the instance

    print("Removed instance with instance id", instance_id)
    return True, instance_id


def handle_instance_failure(app_name, instance_id):
    # check if it is in the working instances or not
    # If it is, there is a failure
    global WORKING_WORKERS
    global lock

    print("Handling instance failure", instance_id)
    lock.acquire()
    WORKING_WORKERS.pop(instance_id)
    lock.release()

    # Create a new instance by requesting the own server only
    create_instance(app_name)
    print("App instane successfully created")


def create_worker(app_name, instance_id):
    global WORKING_WORKERS
    global lock

    ''' Returns True if creation of worker proxy is successfull '''
    try:
        fork_id = os.fork()
    except:
        return False

    if fork_id > 0:
        lock.acquire()
        WORKING_WORKERS[instance_id] = app_name
        lock.release()

        return True
    else:
        print("Child process and id is : ", os.getpid())

        sleep(5)  # Start checking only after 10 seconds
        # TODO, add atleast one call before checking
        # Now we will keep making some requests
        while True:
            if not test_instance(instance_id):
                # Worker with instance_id failed
                lock.acquire()
                print("WORKING WORKERS", WORKING_WORKERS)
                lock.release()
                break
            else:
                print("Instance ", instance_id, " working properly :)")
            sleep(PERIODIC_INTERVAL)

        # If the connection to the instane can't be done
        print("Worker ", instance_id, " failed!")

        # Creates a worker for the specified instance
        handle_instance_failure(app_name, instance_id)
        exit()  # End the forked process here only


def create_workers_for_all_apps():
    users_db = TinyDB("databases/users.json")
    apps = users_db.table("app_applications").all()
    for app_data in apps:
        if "health_check" in app_data and app_data["health_check"] == True:
            print("Health check started for ", app_data["app_name"])
            # Run the load_checker.py file for this

            app_db = TinyDB("databases/app_" + app_data["app_name"] + ".json")
            instances_data = app_db.table("instances").all()
            for instance_data in instances_data:
                if "instance_url" in instance_data:
                    create_worker(app_data["app_name"], instance_data["instance_url"])

            print("All workers for ", app_data["app_name"], " created")


@app.route('/')
def index_page():
    global WORKING_WORKERS

    ''' Returns the list of working workers '''
    return jsonify(WORKING_WORKERS=str(WORKING_WORKERS))


@app.route('/test_instance')
def test_instance_api():
    if "instance_url" not in request.args:
        return jsonify(success=False, error="instance_url not provided")

    instance_url = request.args["instance_url"]

    response = "Request failed to " + \
        str(instance_url) + ", Instance is not working!"
    if test_instance(instance_url):
        response = "Successful Request " + \
            str(instance_url) + ", Instance is working!"

    return jsonify(success=True, response=response)


if __name__ == "__main__":
    create_workers_for_all_apps()
    app.run(debug=True, host="0.0.0.0", port="4999")

