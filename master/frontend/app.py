from crypt import methods
from time import sleep
from flask import Flask, jsonify, request, render_template, session, redirect
import os
import requests
import multiprocessing
from tinydb import TinyDB, Query

app = Flask(__name__)
app.secret_key = "WhatAGoodCourseIsIt"
users_db = TinyDB('users.json')
manager = multiprocessing.Manager()

# stores the list of applications that are currently working and the values stored by them
users_lock = multiprocessing.Lock()

'''
Docs: Every docker_image uploaded by the user has a unique docker_image_id provided by us
After deploying the container, and adding the image, the details of the docker will be in
the form of docker_details : { keys : values }

Will have a seprate json file for each app, that stores its specific app information
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


def create_an_instance(app_name, docker_image=None):
    '''
    Takes a docker image as input and creates a container based on that
    @params: docker image
    @returns: tuple(success_status, application_url_or_error)
    '''

    if docker_image is None:
        # First find the docker_image stored by reading the app_"app_name".json file
        app_db = TinyDB("app_" + app_name + ".json")
        app_data = app_db.get()
        docker_image = app_data["docker_image"]

    return True, True
    try:
        fork_id = os.fork()
    except:
        return False, "System Could not Process, Fork Error"

    if fork_id > 0:
        users_lock.acquire()
        app_applications = users_db.table("app_applications")
        app_applications.insert({
            "app_name": app_name,
            "app_data": {
                "provisioned": False,
                "provisioning": True,
                "docker_image": docker_image },
            "user_id": session["user_id"]
        })
        users_lock.release()

        print("Created application with new application id", app_name)
        return True, app_name
    else:
        print("Child process for app_name", app_name ," and id is : ", os.getpid())

        # TODO, ensure this code does not run first than parent, else it gives error
        # TODO write the provisioning code here using the docker_image, also add the url for it
        sleep(1)

        success_status, app_url_or_error = create_an_instance(app_name, docker_image)
        users_lock.acquire()
        if success_status:
            try:
                app_applications = users_db.table("app_applications")
                query = Query()
                app_applications.update(set_nested(["app_data", 'provisioning'], False), query.app_name == app_name)
                app_applications.update(set_nested(["app_data", 'provisioned'], True), query.app_name == app_name)
                app_applications.update(set_nested(["app_data", "app_url"], app_url_or_error), query.app_name == app_name)
            except:
                users_lock.release()
        else:
            try:
                app_applications = users_db.table("app_applications")
                query = Query()
                app_applications.update(set_nested(["app_data", 'provisioning'], False), query.app_name == app_name)
                app_applications.update(set_nested(["app_data", 'provisioned'], False), query.app_name == app_name)
                app_applications.update(set_nested(["app_data", "error"], app_url_or_error), query.app_name == app_name)
            except:
                users_lock.release()
        users_lock.release()

        print("Provisioned app_name", app_name ," and id is : ", os.getpid())
        exit() # End the child process here, we will contact from another API to know the status


    # TODO PRANSHU AND DIVYASHEEL (TO ASK)
    # For testing right now creating a new python server file
    


def set_nested(path, val):
    def transform(doc):
        current = doc
        for key in path[:-1]:
            current = current[key]

        current[path[-1]] = val

    return transform


def does_application_exists(app_name):
    # success_status, Exists_error?
    users_lock.acquire()
    try:
        app_applications = users_db.table("app_applications")
        query = Query()
        if app_applications.get(query.app_name == app_name) is not None:
            users_lock.release()
            return True, True
        else:
            users_lock.release()
            return True, False
    except:
        users_lock.release()
        return False, "Could not scan applications"


def create_application(app_name, docker_image):
    # 1. Will Start a container from the given docker image
    # 2. Update WORKING_APPLICATIONS
    # Returns a tuple(Success_Status, application_id or error)
    global users_lock

    if "user_id" not in session:
        return False, "User not logged in!"

    # Here try to create a new application from the provided docker image
    # res = requests.get("http://localhost:4999/create_application")

    success_status, exists = does_application_exists(app_name)
    if (success_status):
        if exists:
            return False, "Application with this name already exists"
    else:
        return False, "Error, can't check applications exists"

    # First update in the database, add dashboard link and then create first instance
    # Find a port that will be used by this application

    dashboard_url = "http://localhost:4998/dashboard/" + str(app_name)
    app_url = str(app_name) + ".oursite.com"
    port = "Port of the hostmachine for this website"

    app_object = {
        "app_name": app_name,
        "docker_image": docker_image,
        "dashboard_url": dashboard_url,
        "app_url": app_url,
        "port": port,
        "user_id": session["user_id"]
    }

    users_lock.acquire()
    app_applications = users_db.table("app_applications")
    app_applications.insert(app_object)
    users_lock.release()

    app_db = TinyDB("app_" + str(app_name) + ".json" )
    app_db.insert(app_object)

    create_an_instance(app_name, docker_image=docker_image)

    print("Created application with new application id", app_name)
    return True, app_name


def delete_application(app_name):
    # Will make a request to resource manager
    # 2. Update the WORKING_APPLICATIONS
    # 3. Worker will be already deleted as it will throw
    # Returns a tuple(Success_Status, application_id or error)
    global users_lock

    users_lock.acquire()
    try:
        app_applications = users_db.table("app_applications")
        query = Query()
        app_applications.remove(query.app_name == app_name)
    except:
        users_lock.release()
        return False, app_name
    users_lock.release()

    # TODO, make an API call to resource manager to delete all the instances of this app

    print("Removed application with application id", app_name)
    return True, app_name


@app.route('/')
def index_page():
    if "user_id" not in session:
        return redirect("/login")

    app_applications = users_db.table("app_applications")
    query = Query()
    WORKING_APPLICATIONS = app_applications.search(query.user_id == session["user_id"])
    ''' Returns the list of working applications '''
    # return jsonify(WORKING_APPLICATIONS=str(WORKING_APPLICATIONS), WORKING_WORKERS=str(WORKING_WORKERS))
    return render_template('index.html', WORKING_APPLICATIONS=WORKING_APPLICATIONS)



@app.route('/login', methods=["POST", "GET"])
def login_page():
    if "user_id" in session:
        return redirect("/")

    if request.method == "POST":
        request_body = request.json

        user_data = {}
        req_fields = ["user_password", "user_id"]
        for req_field in req_fields:
            if req_field not in request_body:
                return jsonify(success=False, error=str(req_field) + " not provided!")
            user_data[req_field] = request_body[req_field]

        # Now check in the tinydb
        try:
            user_table = users_db.table('users')
            User = Query()
            user_queried_data = user_table.get(User.user_id == user_data["user_id"])
            if user_queried_data is None:
                return jsonify(success=False, error="UserId does not exists")
            else:
                # User exists
                if user_queried_data["user_password"] == user_data["user_password"]:
                    session["user_id"] = user_data["user_id"]
                    session["user_name"] = user_queried_data["user_name"]
                    session["user_type"] = "normal"
                    return jsonify(success=True)
                return jsonify(success=False, error="Password does not match!")

        except Exception as err:
            return jsonify(success=False, error=str(err))

    return render_template('login.html')


@app.route('/register', methods=["POST", "GET"])
def register_page():
    if "user_id" in session:
        return redirect("/")

    if request.method == "POST":
        request_body = request.json
        
        user_data = {}
        req_fields = ["user_name", "user_password", "user_id"]
        for req_field in req_fields:
            if req_field not in request_body:
                return jsonify(success=False, error=str(req_field) + " not provided!")
            user_data[req_field] = request_body[req_field]

        # Now set the data in the tinyDB
        try:
            user_table = users_db.table('users')
            User = Query()
            if user_table.get(User.user_id == user_data["user_id"]) is not None:
                return jsonify(success=False, error="Choose a different UserId")
            user_table.insert(user_data)
        except Exception as err:
            return jsonify(success=False, error=str(err))

        session["user_id"] = user_data["user_id"]
        session["user_name"] = user_data["user_name"]
        session["user_type"] = "normal"
        return jsonify(success=True)

    return render_template('register.html')

@app.route('/logout')
def logout_page():
    session.clear()
    return redirect('/login')

@app.route('/dashboard/<app_name>')
def dashboard_app_page(app_name):
    try:
        app_db = TinyDB("app_" + app_name + ".json")
        app_data = app_db.get(doc_id=1)
        if app is not None:
            return render_template('dashboard.html', app_data=app_data)
        else:
            return "No such app exists!"
    except Exception as err:
        return jsonify(success=False, error=str(err))

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
    if "app_name" not in request.args:
        return jsonify(success=False, error="app_name not provieded!")
    app_name = request.args["app_name"]

    # # Make a request to the resource manager to delete an application
    success_status, application_or_error = delete_application(app_name)
    if success_status:
        return redirect("/")
        # return jsonify(success=True, application_id=application_or_error)

    return jsonify(success=False, error=application_or_error)


if __name__ == "__main__":
    app.run(debug=True, port=4998)
