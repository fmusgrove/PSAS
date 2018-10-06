import atexit
from Database.db_interface import DBInterface
from TwitterAPI.twitter_test import MyStreamer


def exit_handler():
    """
    Runs before exit, including if a KeyboardInterrupt is encountered
    """
    if db is not None:
        print('Closing tunneled ssh connection to database...')


atexit.register(exit_handler)

if __name__ == '__main__':
    # Creating the DBInterface object will open the ssh tunnel, must be closed before exiting
    db = DBInterface('res/ssh_db_pw.json')
    rows = db.run_command("SELECT * FROM twitter").fetchall()
    db.run_command()
    # Instantiate from our streaming class
    stream = MyStreamer()
    # Start the stream
    stream.statuses.filter(track='trump')
    db.close()
