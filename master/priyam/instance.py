from flask import Flask
import sys

app = Flask(__name__)

@app.route('/')
def index():
    return 'Hello World'

if __name__ == "__main__":
    if len(sys.argv) > 1:
        app.run(port=sys.argv[1])
    else:
        print("Provide port number in the argument")
