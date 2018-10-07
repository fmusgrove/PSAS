from Database.db_interface import DBInterface
from TwitterAPI.twitter_firehose import TwitterFirehose
from multiprocessing.managers import BaseManager
from SentimentCompute.sentiment_index import SentimentIndex
from Utility.message_pipes import MessagePipes
from time import sleep

if __name__ == '__main__':
    # Base manager registration for DBInterface class
    BaseManager.register('DBInterface', DBInterface)
    BaseManager.register('MessagePipes', MessagePipes)
    base_manager = BaseManager()

    # Start the data proxy server
    base_manager.start()

    # Creating the DBInterface object will open the ssh tunnel, must be closed before exiting
    db_interface = base_manager.DBInterface('res/ssh_db_pw.json')  # PyCharm isn't aware of abstract classes...
    message_pipes = base_manager.MessagePipes()  # PyCharm isn't aware of abstract classes...

    sentiment_agent = SentimentIndex(db_interface, message_pipes)
    twitter_firehose = TwitterFirehose('res/twitter_api_credentials.json', 'bitcoin, btc', db_interface, message_pipes)

    sleep(60)
    message_pipes.get_pipes()['twitter_firehose']['pipe_in'].send('EXIT')
    message_pipes.get_pipes()['sentiment_index']['pipe_in'].send('EXIT')

    twitter_firehose.join()
    sentiment_agent.join()

    db_interface.close()
    # Shut down the process data-sharing server
    base_manager.shutdown()
