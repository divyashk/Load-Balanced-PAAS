from time import sleep
from flask import Flask, jsonify, request, render_template
import os
import requests
import multiprocessing

app = Flask(__name__)

manager = multiprocessing.Manager()

# stores the list of applications that are currently working and the values stored by them
WORKING_APPLICATIONS = manager.dict()
lock = multiprocessing.Lock()

'''
Docs: Every docker_image uploaded by the user has a unique docker_image_id provided by us
After deploying the container, and adding the image, the details of the docker will be in
the form of docker_details : { keys : values }
'''


def test_application(application_url):
    ''' Makes a get request to the application url, and return True if it is working '''
    print("Testing application url: ", application_url)

    try:
        requests.get(application_url)
    except requests.exceptions.InvalidSchema:
        try:
            requests.get("http://" + str(application_url))
        except:
            return False

    except requests.ConnectionError:
        return False

    return True


def create_docker_container(docker_image):
    '''
    Takes a docker image as input and creates a container based on that
    @params: docker image
    @returns: tuple(success_status, application_url_or_error)
    '''

    return True, "docker_id"


def create_application(app_name, docker_image):
    # 1. Will Start a container from the given docker image
    # 2. Update WORKING_APPLICATIONS
    # 3. Creates a Worker
    # Returns a tuple(Success_Status, application_id or error)

    global WORKING_APPLICATIONS
    global lock

    # Here try to create a new application from the provided docker image
    # res = requests.get("http://localhost:4999/create_application")

    ''' Returns True if creation of worker proxy is successfull '''
    try:
        fork_id = os.fork()
    except:
        return False, "System Could not Process, Fork Error"

    if fork_id > 0:
        lock.acquire()
        WORKING_APPLICATIONS[app_name] = manager.dict({
            "provisioned": False,
            "provisioning": True,
            "docker_image": docker_image
        })
        lock.release()

        print("Created application with new application id", app_name)
        return True, app_name
    else:
        print("Child process for app_name", app_name ," and id is : ", os.getpid())

        # TODO write the provisioning code here using the docker_image, also add the url for it
        sleep(5)
        lock.acquire()
        WORKING_APPLICATIONS[app_name]["provisioning"] = False
        WORKING_APPLICATIONS[app_name]["provisioned"] = True
        lock.release()

        print(WORKING_APPLICATIONS, "WORKING APPlictions")
        print("Provisioned app_name", app_name ," and id is : ", os.getpid())
        exit() # End the child process here, we will contact from another API to know the status


def delete_application(application_id):
    # Will make a request to resource manager
    # 2. Update the WORKING_APPLICATIONS
    # 3. Worker will be already deleted as it will throw
    # Returns a tuple(Success_Status, application_id or error)
    global WORKING_APPLICATIONS
    global lock

    lock.acquire()
    WORKING_APPLICATIONS.pop(application_id)
    lock.release()
    # TODO, make an API call to resource manager to delete the application

    print("Removed application with application id", application_id)
    return True, application_id


@app.route('/')
def index_page():
    global WORKING_APPLICATIONS

    ''' Returns the list of working applications '''
    # return jsonify(WORKING_APPLICATIONS=str(WORKING_APPLICATIONS), WORKING_WORKERS=str(WORKING_WORKERS))
    return render_template('index.html', WORKING_APPLICATIONS=WORKING_APPLICATIONS)


@app.route('/test_application')
def test_application_api():
    if "application_url" not in request.args:
        return jsonify(success=False, error="application_url not provided")

    application_url = request.args["application_url"]

    response = "Request failed to " + \
        str(application_url) + ", Instance is not working!"
    if test_application(application_url):
        response = "Successful Request " + \
            str(application_url) + ", Instance is working!"

    return jsonify(success=True, response=response)


@app.route('/create_application')
def create_application_api():
    # Make a request to the resource manager to create an application
    # and then start the worker proxy that looks over to that application
    # TODO, provide the docker image also here
    if "docker_image" not in request.args:
        return jsonify(success=False, error="docker_image not provided in request.args")

    if "app_name" not in request.args:
        return jsonify(success=False, error="app_name not provided in request.args")

    docker_image = request.args["docker_image"]
    app_name = request.args["app_name"]

    success_status, application_or_error = create_application(app_name, docker_image)
    if success_status:
        return jsonify(success=True, application_id=application_or_error)

    return jsonify(success=False, error=application_or_error)


@app.route('/delete_application')
def delete_application_api():
    if "application_id" not in request.args:
        return jsonify(success=False, error="application_id not provieded!")
    application_id = request.args["application_id"]

    # # Make a request to the resource manager to delete an application
    success_status, application_or_error = delete_application(application_id)
    if success_status:
        return jsonify(success=True, application_id=application_or_error)

    return jsonify(success=False, error=application_or_error)


if __name__ == "__main__":
    app.run(debug=True, port=4998)
