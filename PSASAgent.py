from Database.db_interface import DBInterface
from TwitterAPI.twitter_firehose import TwitterFirehose
from multiprocessing.managers import BaseManager
from SentimentCompute.sentiment_index import SentimentIndex
from Utility.message_pipes import MessagePipes
from time import sleep

if __name__ == '__main__':
    feature_data = {
        'elon_musk': 'elon, musk, elon musk'
        # 'hawkeyes': 'hawkeyes, iowa hawkeyes'
    }

    firehoses = {}
    # Base manager registration for DBInterface class
    BaseManager.register('DBInterface', DBInterface)
    BaseManager.register('MessagePipes', MessagePipes)
    base_manager = BaseManager()

    # Start the data proxy server
    base_manager.start()

    # Creating the DBInterface object will open the ssh tunnel, must be closed before exiting
    db_interface = base_manager.DBInterface('res/ssh_db_pw.json')  # PyCharm isn't aware of abstract classes...
    message_pipes = base_manager.MessagePipes(
        [key for key in feature_data.keys()])  # PyCharm isn't aware of abstract classes...

    # Start all parallel processes with appropriate pipe access
    for table_name in feature_data.keys():
        firehoses[table_name] = TwitterFirehose('res/twitter_api_credentials.json', feature_data[table_name],
                                                table_name,
                                                db_interface,
                                                message_pipes)
        firehoses[table_name].start()
        print(firehoses[table_name].features)

    # Main compute timing loop
    for i in range(60 * 5):
        sleep(60)
        for table_name in feature_data.keys():
            message_pipes.get_pipes()[f'{table_name}_firehose']['pipe_in'].send('COMPUTE')

    # Exit poison pill for all firehose processes
    for table_name in feature_data.keys():
        message_pipes.get_pipes()[f'{table_name}_firehose']['pipe_in'].send('EXIT')

    sleep(2)

    print('Joining processes...')
    for firehose in firehoses.values():
        firehose.join()

    db_interface.close()
    # Shut down the process data-sharing server
    base_manager.shutdown()
