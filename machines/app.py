from time import sleep
from flask import Flask, render_template, jsonify, request , redirect , url_for, session
from werkzeug.utils import secure_filename
import docker
from zipfile import ZipFile
from socket import socket
import subprocess
import os
from stats import get_cpu_details, get_memory_details
from flask_socketio import SocketIO, emit


UPLOAD_FOLDER = 'zipfiles'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif' , 'zip'}
CONNECTED_CLIENTS = []


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
        s.bind(('',0))
        freeport = s.getsockname()[1]
    return freeport

@app.route('/')
def index_page():
    return render_template("index.html")


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

    output = os.popen(cmd).read()
    print(output)

    return jsonify(success=True, output=output)


@app.route('/build-from-hub', methods=['POST'])
def build_from_hub():
    # add current user to group docker, and also run "newgrp docker"
    repo = request.form['repo']
    print(repo)
    image = client.images.pull(repo)
    freeport = get_freeport()
    container = client.containers.run(repo + ':latest' , ports = {5000 : freeport} , detach=True)
    print(container)
    print(freeport)
    return jsonify(success=True, port=freeport)

@app.route('/build-from-zip', methods=['POST'])
def build_from_zip():
    # add current user to group docker, and also run "newgrp docker"
    if 'file' not in request.files:
        return {'message' : 'File not sent'}
    file = request.files['file']
    if file.filename == '':
        return {'message' : 'File not sent'}

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        filepath = os.path.join(app.config['UPLOAD_FOLDER'] , filename)
        appname = request.form["appname"]
        print(filepath)
        print(appname)
        with ZipFile(filepath , 'r') as zipObj:
            zipObj.extractall('extracted_zips/' + appname)
            zipImage = client.images.build(path = 'extracted_zips/' + appname)[0]
            zipImage.tag(appname , "latest")
            print(client.images.list())
        freeport = get_freeport()
        print(freeport)
        # container = client.containers.run(appname + ":latest" , ports = {5000 : freeport} , detach=True)
        container = client.containers.run(appname + ":latest", ports = {5000 : freeport} , detach=True)
        print(container.id , container.labels , container.image)
        print(client.containers.list())
        return jsonify(success=True, port=freeport)
    else:
        return jsonify(success=False)

app.run(port=8080, host="0.0.0.0")
