from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


class SentimentIndex:
    def __init__(self, database_interface=None):
        self.database_interface = database_interface

    def _message_listener(self):
        self.compute_sentiment(msg['tweet'], msg['features'].split(',')[0])

    def compute_sentiment(self, tweet, table_name):
        """
        Calculates the sentiment score and saves the value to the database
        :param tweet: tweet string to compute sentiment from
        :param table_name: name of table to store data to
        """
        vs = self.analyzer.polarity_scores(tweet['text'])
        print(vs['compound'])
        self.database_interface.run_command("INSERT INTO %s(timestamp,sentiment_metric) VALUES (%s,%s)",
                                            (table_name, tweet['time'], vs['compound']),
                                            should_return=False)
