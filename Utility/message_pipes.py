from multiprocessing import Pipe


class MessagePipes:
    def __init__(self):
        self.pipes = {}
        self.pipes['twitter_firehose'] = {}
        self.pipes['sentiment_index'] = {}
        self.pipes['twitter_firehose']['pipe_in'], self.pipes['twitter_firehose']['pipe_out'] = Pipe()
        self.pipes['sentiment_index']['pipe_in'], self.pipes['sentiment_index']['pipe_out'] = Pipe()

    def get_pipes(self):
        return self.pipes
