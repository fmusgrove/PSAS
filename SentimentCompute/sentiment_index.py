from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from Utility.connected_process import ConnectedProcess


class SentimentIndex(ConnectedProcess):
    def __init__(self, database_interface=None, message_pipe=None):
        super(SentimentIndex).__init__(name='PSAS Sentiment', database_interface=database_interface,
                                       message_pipe=message_pipe)
        self.TWEET_COUNT = 5  # Temporarily keep only a certain number of tweets
        self.tweets = []
        self.analyzer = SentimentIntensityAnalyzer()
        self.should_exit = False

    def _message_listener(self):
        msg = ''
        while not msg == 'EXIT':
            msg = self.message_pipe['pipe_out'].recv()
            # Handle messages here

        self.should_exit = True
        self._close()

    # Temporary function for pulling full tweets from database
    def pull_tweets(self):
        self.tweets = self.database_interface.run_command(
            "SELECT * FROM temp_tweet_table ORDER BY time ASC FETCH FIRST 10 ROWS ONLY")
        for tweet in self.tweets:
            vs = self.analyzer.polarity_scores(tweet[1])
            print(tweet[1], vs['compound'])

    def compute_sentiment(self, tweet):
        """
        Calculates the sentiment score and saves the value to the database
        :param tweet: tweet string to compute sentiment from
        """
        pass

    def _start_work(self):
        """
        Main entry point for new process, ran on separate thread from _message_listener
        """
        pass

    def _close(self):
        """
        Called after exit poison pill is received
        """
        pass
