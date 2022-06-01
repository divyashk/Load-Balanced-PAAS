from time import sleep
from flask import Flask
from flask import render_template, jsonify, request , redirect , url_for, session
from werkzeug.utils import secure_filename
import docker
from zipfile import ZipFile
from socket import socket
import subprocess
import os
from stats import get_cpu_details, get_memory_details
from flask_socketio import SocketIO, emit


UPLOAD_FOLDER = 'zipfiles'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'zip'}
CONNECTED_CLIENTS = []
ADMIN_PASSWORD = "admin"


client = docker.from_env()
app = Flask(__name__)
app.config["DEBUG"] = True
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
socketio = SocketIO(app)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_freeport():
    freeport = ""
    with socket() as s:
        s.bind(('', 0))
        freeport = s.getsockname()[1]
    return freeport


@app.route('/')
def index_page():
    return "Machine Home!"


@app.route('/term')
def term_page():
    ''' Pass the Admin password for the service '''
    if "password" not in request.args:
        return jsonify(success=False, error="password not provided!")

    if request.args["password"] == ADMIN_PASSWORD:
        return render_template('term.html')

    return jsonify(success=False, error="Wrong Password!")


@app.route('/stats', methods=["GET", "POST"])
def stats_page():
    if request.method == "POST":
        return jsonify(cpu_details=get_cpu_details(), memory_details=get_memory_details())

    return render_template('stats.html')


@app.route('/runcmd', methods=["POST"])
def run_cmd_on_machine():
    cmd = request.json["cmd"]
    if cmd is None:
        return jsonify(success=False, error="No command(cmd) provided")

    output = ""
    cwd = os.getcwd()
    if "cwd" in request.json:
        cdd = request.json["cwd"]
        if cdd != "":
            os.chdir(cdd)
        output = os.popen(cmd).read()
        os.chdir(cwd)
    else:
        output = os.popen(cmd).read()
    print(output)

    return jsonify(success=True, output=output)


@app.route('/build-from-hub', methods=['POST'])
def build_from_hub():
    # add current user to group docker, and also run "newgrp docker"
    repo = request.form['repo']
    dockerport = request.form['port']
    print(repo)
    image = client.images.pull(repo)
    freeport = get_freeport()
    container = client.containers.run(
        repo + ':latest', ports={dockerport: freeport}, detach=True)
    print(container)
    print(freeport)
    return jsonify(success=True, port=freeport , container_id=container.id)


@app.route('/build-from-zip', methods=['POST'])
def build_from_zip():
    # add current user to group docker, and also run "newgrp docker"
    if 'file' not in request.files:
        return {'message': 'File not sent'}
    file = request.files['file']
    if file.filename == '':
        return {'message': 'File not sent'}

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        appname = request.form["appname"]
        print(filepath)
        print(appname)
        with ZipFile(filepath, 'r') as zipObj:
            zipObj.extractall('extracted_zips/' + appname)
            zipImage = client.images.build(path='extracted_zips/' + appname)[0]
            zipImage.tag(appname, "latest")
            print(client.images.list())
        freeport = get_freeport()
        print(freeport)
        # container = client.containers.run(appname + ":latest" , ports = {5000 : freeport} , detach=True)
        container = client.containers.run(
            appname + ":latest", ports={5000: freeport}, detach=True)
        print(container.id, container.labels, container.image)
        print(client.containers.list())
        return jsonify(success=True, port=freeport)
    else:
        return jsonify(success=False)


app.run(port=8080, host="0.0.0.0")
