import json
from flask import Flask
from Database.db_interface import DBInterface

app = Flask(__name__)


@app.route('/')
def hello_world():
    db_interface = DBInterface(should_tunnel=False)

    # Elon Musk Data
    elon_row = db_interface.run_command("SELECT * FROM elon_musk")
    elon_time = [str(row[0]) for row in elon_row]
    elon_metric = [row[1] for row in elon_row]

    # BTC Data
    btc_row = db_interface.run_command("SELECT * FROM bitcoin")
    btc_time = [str(row[0]) for row in btc_row]
    btc_metric = [row[1] for row in btc_row]

    # Kavanaugh Data
    kav_row = db_interface.run_command("SELECT * FROM kavanaugh")
    kav_time = [str(row[0]) for row in kav_row]
    kav_metric = [row[1] for row in kav_row]

    # Trump Data
    trump_row = db_interface.run_command("SELECT * FROM kavanaugh")
    trump_time = [str(row[0]) for row in trump_row]
    trump_metric = [row[1] for row in trump_row]

    return json.dumps({"Elon Musk": {"score": elon_metric,
                                     "timestamp": elon_time},
                       "Bitcoin": {"score": btc_metric,
                                   "timestamp": btc_time},
                       "Kavanaugh": {"score": kav_metric,
                                     "timestamp": kav_time},
                       "Trump": {"score": trump_metric,
                                 "timestamp": trump_time}
                       })


if __name__ == '__main__':
    app.run(host='0.0.0.0')
