import json
from flask import Flask

app = Flask(__name__)


@app.route('/')
def hello_world():
    return json.dumps({'values': [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, ]})


if __name__ == '__main__':
    app.run()
