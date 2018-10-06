import os
from json import load

import requests
from twython import TwythonStreamer
import csv


# Filter out unwanted data
def process_tweet(tweet):
    return {'text': tweet['text'], 'time': tweet['created_at']}


# Create a class that inherits TwythonStreamer
class MyStreamer(TwythonStreamer):
    def __init__(self, settings_file: str = '../res/twitter_api_credentials.json', database_interface=None):
        self.count = 0
        self.tweet_array = []
        self.database_interface = database_interface
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
        #self.disconnect()

    def fill_tweet_array(self, tweet):
        pass
        #self.database_interface.run_command("INSERT INTO temp_tweet_table(tweet,time) VALUES (%s,%s)",
                                            # (tweet['text'], tweet['time']), should_return=False)
