from Database.db_interface import DBInterface
from TwitterAPI.twitter_firehose import TwitterFirehose
from multiprocessing.managers import BaseManager
from SentimentCompute.sentiment_index import SentimentIndex
from Utility.message_pipes import MessagePipes
from time import sleep

if __name__ == '__main__':
    feature_data = {
        # 'elon_musk': 'elon, musk, elon musk',
        'banksy': 'banksy',
        'bitcoin': 'bitcoin, btc',
        'trump': 'trump, donald trump',
        'kavanaugh': 'kavanaugh',
        'packers': 'green bay packers',
        'twitter': 'twitter, twtr'
    }

    # Base manager registration for DBInterface class
    BaseManager.register('DBInterface', DBInterface)
    BaseManager.register('MessagePipes', MessagePipes)
    base_manager = BaseManager()

    # Start the data proxy server
    base_manager.start()

    # Creating the DBInterface object will open the ssh tunnel, must be closed before exiting
    db_interface = base_manager.DBInterface('res/ssh_db_pw.json')  # PyCharm isn't aware of abstract classes...
    message_pipes = base_manager.MessagePipes()  # PyCharm isn't aware of abstract classes...

    # Setup and start Twitter firehose
    twitter_firehose = TwitterFirehose('res/twitter_api_credentials.json', feature_data, db_interface,
                                       message_pipes)
    twitter_firehose.start()

    # Main compute timing loop
    for i in range(60 * 5):
        sleep(60)
        message_pipes.get_pipes()['twitter_firehose']['pipe_in'].send('COMPUTE')

    # Exit poison pill for Twitter firehose process
    message_pipes.get_pipes()['twitter_firehose']['pipe_in'].send('EXIT')

    sleep(2)

    print('Joining processes...')
    twitter_firehose.join()

    db_interface.close()
    # Shut down the process data-sharing server
    base_manager.shutdown()
