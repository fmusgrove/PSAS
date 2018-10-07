from json import load
from twython import TwythonStreamer
from unidecode import unidecode
from Utility.connected_process import ConnectedProcess
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


# Create a class that inherits TwythonStreamer
class TwitterFirehose(ConnectedProcess, TwythonStreamer):
    def __init__(self, settings_file: str = '../res/twitter_api_credentials.json',
                 feature_data=None,
                 database_interface=None,
                 message_pipes=None):
        with open(settings_file, 'r', encoding='utf-8') as settings_data:
            settings = load(settings_data)
            # twitter api settings
            self.CONSUMER_KEY = settings['CONSUMER_KEY']
            self.CONSUMER_SECRET = settings['CONSUMER_SECRET']
            self.ACCESS_TOKEN = settings['ACCESS_TOKEN']
            self.ACCESS_SECRET = settings['ACCESS_SECRET']
        ConnectedProcess.__init__(self, name='Twitter Firehose', database_interface=database_interface,
                                  message_pipes=message_pipes)
        TwythonStreamer.__init__(self, app_key=self.CONSUMER_KEY, app_secret=self.CONSUMER_SECRET,
                                 oauth_token=self.ACCESS_TOKEN,
                                 oauth_token_secret=self.ACCESS_SECRET)
        self.count = 0
        self.database_interface = database_interface
        self.analyzer = SentimentIntensityAnalyzer()
        self.feature_data = feature_data
        self.tracking_features = ', '.join([feature for feature in feature_data.values()])
        self.tweet_time_slice = {table_name: [] for table_name in feature_data.keys()}

    def _message_listener(self):
        msg = ''
        while not msg == 'EXIT':
            msg = self.message_pipes.get_pipes()['twitter_firehose']['pipe_out'].recv()
            if msg == 'COMPUTE':
                self.compute_sentiment()

        self.should_exit = True
        self._close()

    def _start_work(self):
        """
        Main entry point for new process, ran on separate thread from _message_listener
        """
        self.statuses.filter(track=self.tracking_features)

    def _close(self):
        """
        Called after exit poison pill is received
        """
        print('Closing Twitter firehose')
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
                for table_name, features in self.feature_data.items():
                    for word in features.split(','):
                        if word in tweet_data['text']:
                            self.tweet_time_slice[table_name].append(tweet_data)

    def on_error(self, status_code, data):
        print(status_code, data)
        # self.disconnect()

    def compute_sentiment(self):
        """
        Calculates the sentiment score and saves the value to the database
        """
        for table_name, tweet_list in self.tweet_time_slice.items():
            if len(tweet_list) > 0:
                total = 0
                for tweet in tweet_list:
                    vs = self.analyzer.polarity_scores(tweet['text'])
                    total += vs['compound']

                average = total / len(tweet_list)
                print(average)
                self.tweet_time_slice[table_name] = []
                self.database_interface.run_command(
                    f"INSERT INTO {table_name} VALUES (current_timestamp, {average})", should_return=False)
