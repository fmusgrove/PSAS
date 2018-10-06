import atexit
from Database.db_interface import DBInterface
from TwitterAPI.twitter_test import MyStreamer
from multiprocessing.managers import BaseManager


def exit_handler():
    """
    Runs before exit, including if a KeyboardInterrupt is encountered
    """
    if db_interface is not None:
        print('Closing tunneled ssh connection to database...')
        db_interface.close()


atexit.register(exit_handler)

if __name__ == '__main__':
    # Base manager registration for DBInterface class
    BaseManager.register('DBInterface', DBInterface)
    base_manager = BaseManager()

    # Start the data proxy server
    base_manager.start()

    db_interface = base_manager.DBInterface('res/ssh_db_pw.json')  # PyCharm isn't aware of abstract classes...

    # Creating the DBInterface object will open the ssh tunnel, must be closed before exiting
    rows = db_interface.run_command("SELECT * FROM twitter")

    # db.run_command()
    # # Instantiate from our streaming class
    # stream = MyStreamer()
    # # Start the stream
    # stream.statuses.filter(track='trump')

    db_interface.close()
    # Shut down the process data-sharing server
    base_manager.shutdown()
