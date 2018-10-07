import json
from flask import Flask
from Database.db_interface import DBInterface

app = Flask(__name__)


@app.route('/')
def hello_world():
    db_interface = DBInterface()
    row_data = db_interface.run_command("SELECT * FROM elon_musk")

    time = [str(row[0]) for row in row_data]
    metric = [row[1] for row in row_data]

    return json.dumps({"elon_musk": {"score": metric,
                                     "timestamp": time}})


if __name__ == '__main__':
    app.run(host='0.0.0.0')
