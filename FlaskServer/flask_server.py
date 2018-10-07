import json
from flask import Flask

app = Flask(__name__)


@app.route('/')
def hello_world():
    return json.dumps({"fortnite": {"score": [75, 80, 76, 70],
                                    "timestamp": ["2018-10-06T19:20+01:00", "2018-10-06T19:20+01:00",
                                                  "2018-10-06T19:20+01:00", "2018-10-06T19:20+01:00"]}})


if __name__ == '__main__':
    app.run(host='0.0.0.0')
