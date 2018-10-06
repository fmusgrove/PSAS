class SentimentIndex:
    def __init__(self, database_interface=None):
        self.database_interface = database_interface
        self.TWEET_COUNT = 5  # Temporarily keep only a certain number of tweets
        self.tweets = []

    def pull_tweets(self):
        self.tweets = self.database_interface.run_command(
            "SELECT * FROM temp_tweet_table ORDER BY time ASC FETCH FIRST 10 ROWS ONLY")
        print(self.tweets)