from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from Utility.connected_process import ConnectedProcess


class SentimentIndex(ConnectedProcess):
    def __init__(self, database_interface=None, message_pipes=None):
        super(SentimentIndex).__init__(name='PSAS Sentiment', database_interface=database_interface,
                                       message_pipe=message_pipes)
        self.TWEET_COUNT = 5  # Temporarily keep only a certain number of tweets
        self.tweets = []
        self.analyzer = SentimentIntensityAnalyzer()
        self.should_exit = False

    def _message_listener(self):
        msg = ''
        while not msg == 'EXIT':
            msg = self.message_pipes.get_pipes()['sentiment_index']['pipe_out'].recv()
            if 'tweet' in msg:
                self.compute_sentiment(msg['tweet'], msg['feature'].split(',')[0])

        self.should_exit = True
        self._close()

    # Temporary function for pulling full tweets from database
    def pull_tweets(self):
        self.tweets = self.database_interface.run_command(
            "SELECT * FROM temp_tweet_table ORDER BY time ASC FETCH FIRST 10 ROWS ONLY")
        for tweet in self.tweets:
            vs = self.analyzer.polarity_scores(tweet[1])
            print(tweet[1], vs['compound'])

    def compute_sentiment(self, tweet, table_name):
        """
        Calculates the sentiment score and saves the value to the database
        :param tweet: tweet string to compute sentiment from
        :param table_name: name of table to store data to
        """
        vs = self.analyzer.polarity_scores(tweet[1])
        self.database_interface.run_command("INSERT INTO %s(time,tweet) VALUES (%s,%s)",
                                            (table_name, vs, tweet['text']),
                                            should_return=False)

    def _close(self):
        """
        Called after exit poison pill is received
        """
        for thread in self.threads:
            thread.join()
