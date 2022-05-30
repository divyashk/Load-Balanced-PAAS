import os
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

@app.route('/')
def index_page():
    return render_template("index.html")


@app.route('/runcmd', methods=["POST"])
def run_cmd_on_machine():
    cmd = request.json["cmd"]
    if cmd is None:
        return jsonify(success=False, error="No command(cmd) provided")

    output = os.popen(cmd).read()
    print(output)

    return jsonify(success=True, output=output)


if __name__ == "__main__":
    app.run(debug=True)
