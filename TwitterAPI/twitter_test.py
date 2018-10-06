import os
from json import load
from twython import TwythonStreamer
import csv
import time

# Filter out unwanted data
def process_tweet(tweet):
    d = {}
    d['text'] = tweet['text']
    d['time'] = tweet['created_at']
    return d


# Create a class that inherits TwythonStreamer
class MyStreamer(TwythonStreamer):
    def __init__(self, settings_file: str = '../res/twitter_api_credentials.json'):
        self.count = 0
        self.tweet_array = []
        with open(settings_file, 'r', encoding='utf-8') as settings_data:
            settings = load(settings_data)
            # twitter api settings
            self.CONSUMER_KEY = settings['CONSUMER_KEY']
            self.CONSUMER_SECRET = settings['CONSUMER_SECRET']
            self.ACCESS_TOKEN = settings['ACCESS_TOKEN']
            self.ACCESS_SECRET = settings['ACCESS_SECRET']
        super().__init__(self.CONSUMER_KEY, self.CONSUMER_SECRET, self.ACCESS_TOKEN, self.ACCESS_SECRET)


    def on_success(self, data):
        # Only collect tweets in English
        if 'lang' in data:
            if data['lang'] == 'en':
                tweet_data = process_tweet(data)
                self.fill_tweet_array(tweet_data)

    # Problem with the API
    def on_error(self, status_code, data):
        print(status_code, data)
        self.disconnect()

    # Save each tweet to csv file
    def save_to_csv(self, tweet):
        var = tweet.values()
        print(var)

        #  writer.writerow(list(var))

    def fill_tweet_array(self, tweet):
        if self.count < 100:
            self.count += 1
            tweet_values = tweet.values()
            if len(str(tweet_values)) > 50:
                self.tweet_array.append(tweet.values())
        else:
            MyStreamer.count = 0
            with open(r'saved_tweets.csv', 'w', encoding='utf-8') as file:
                writer = csv.writer(file)
                for row in self.tweet_array:
                    writer.writerow(row)


# Instantiate from our streaming class
stream = MyStreamer()
# Start the stream
stream.statuses.filter(track='trump')