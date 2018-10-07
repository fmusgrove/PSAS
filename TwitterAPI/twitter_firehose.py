from json import load
from twython import TwythonStreamer
from unidecode import unidecode
from Utility.connected_process import ConnectedProcess
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


# Create a class that inherits TwythonStreamer
class TwitterFirehose(ConnectedProcess, TwythonStreamer):
    def __init__(self, settings_file: str = '../res/twitter_api_credentials.json', features='twitter',
                 table_name='twitter',
                 database_interface=None,
                 message_pipes=None):
        with open(settings_file, 'r', encoding='utf-8') as settings_data:
            settings = load(settings_data)
            # twitter api settings
            self.CONSUMER_KEY = settings['CONSUMER_KEY']
            self.CONSUMER_SECRET = settings['CONSUMER_SECRET']
            self.ACCESS_TOKEN = settings['ACCESS_TOKEN']
            self.ACCESS_SECRET = settings['ACCESS_SECRET']
        ConnectedProcess.__init__(self, name=f'Twitter Firehose {table_name}', database_interface=database_interface,
                                  message_pipes=message_pipes)
        TwythonStreamer.__init__(self, app_key=self.CONSUMER_KEY, app_secret=self.CONSUMER_SECRET,
                                 oauth_token=self.ACCESS_TOKEN,
                                 oauth_token_secret=self.ACCESS_SECRET)
        self.count = 0
        self.database_interface = database_interface
        self.analyzer = SentimentIntensityAnalyzer()
        self.features = features
        self.table_name = table_name
        self.tweet_time_slice = []

    def _message_listener(self):
        msg = ''
        while not msg == 'EXIT':
            msg = self.message_pipes.get_pipes()[f'{self.table_name}_firehose']['pipe_out'].recv()
            if msg == 'COMPUTE':
                self.compute_sentiment()

        self.should_exit = True
        self._close()

    def _start_work(self):
        """
        Main entry point for new process, ran on separate thread from _message_listener
        """
        self.statuses.filter(track=self.features)

    def _close(self):
        """
        Called after exit poison pill is received
        """
        print(f'Closing firehose {self.table_name}')
        self.disconnect()

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
                self.tweet_time_slice.append(tweet_data)

    def on_error(self, status_code, data):
        print(status_code, data)
        # self.disconnect()

    def compute_sentiment(self):
        """
        Calculates the sentiment score and saves the value to the database
        """
        if len(self.tweet_time_slice) > 0:
            total = 0
            for tweet in self.tweet_time_slice:
                vs = self.analyzer.polarity_scores(tweet['text'])
                total += vs['compound']

            average = total / len(self.tweet_time_slice)
            print(average)
            self.tweet_time_slice = []
            self.database_interface.run_command(
                f"INSERT INTO {self.table_name} VALUES (current_timestamp, {average})", should_return=False)
