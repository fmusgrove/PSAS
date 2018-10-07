from json import load
from twython import TwythonStreamer
from unidecode import unidecode
from Utility.connected_process import ConnectedProcess


# Create a class that inherits TwythonStreamer
class TwitterFirehose(TwythonStreamer, ConnectedProcess):
    def __init__(self, settings_file: str = '../res/twitter_api_credentials.json', feature='twitter',
                 database_interface=None,
                 message_pipes=None):
        with open(settings_file, 'r', encoding='utf-8') as settings_data:
            settings = load(settings_data)
            # twitter api settings
            self.CONSUMER_KEY = settings['CONSUMER_KEY']
            self.CONSUMER_SECRET = settings['CONSUMER_SECRET']
            self.ACCESS_TOKEN = settings['ACCESS_TOKEN']
            self.ACCESS_SECRET = settings['ACCESS_SECRET']
        super(TwitterFirehose).__init__(self.CONSUMER_KEY, self.CONSUMER_SECRET, self.ACCESS_TOKEN, self.ACCESS_SECRET)
        super(TwitterFirehose).__init__(name='PSAS Twitter Firehose', database_interface=database_interface,
                                        message_pipes=message_pipes)
        self.count = 0
        self.tweet_array = []
        self.database_interface = database_interface
        self.feature = feature

    def _message_listener(self):
        msg = ''
        while not msg == 'EXIT':
            msg = self.message_pipes.get_pipes()['twitter_firehose']['pipe_out'].recv()
            # Handle messages here

        self.should_exit = True
        self._close()

    def _start_work(self):
        """
        Main entry point for new process, ran on separate thread from _message_listener
        """
        self.statuses.filter(track=self.feature)

    def _close(self):
        """
        Called after exit poison pill is received
        """
        self.disconnect()
        for thread in self.threads:
            thread.join()

    # Filter out unwanted data
    def process_tweet(self, tweet):
        """
        Return only tweet text and timestamp. Checks for truncation and returns full text
        :param tweet: tweet text string to process
        :return: dict(text, time)
        """
        if tweet['truncated']:
            data = unidecode(tweet['extended_tweet']['full_text'])
        else:
            data = unidecode(tweet['text'])
        return {'text': data, 'time': unidecode(tweet['created_at'])}

    def on_success(self, data):
        # Only collect tweets in English
        if 'lang' in data:
            if data['lang'] == 'en':
                tweet_data = self.process_tweet(data)
                self.message_pipes.get_pipes()['sentiment_index']['pipe_in'].send({'tweet': tweet_data,
                                                                                   'feature': self.feature})

    def on_error(self, status_code, data):
        print(status_code, data)
        # self.disconnect()

    def fill_tweet_array(self, tweet):
        # self.database_interface.run_command("INSERT INTO temp_tweet_table(time,tweet) VALUES (%s,%s)",
        #                                     (tweet['time'], tweet['text']), should_return=False)
        pass
