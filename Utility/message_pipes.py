from multiprocessing import Pipe


class MessagePipes:
    def __init__(self):
        self.pipes = {}
        self.pipes['twitter_firehose'] = {}
        self.pipes['twitter_firehose']['pipe_in'], self.pipes['twitter_firehose']['pipe_out'] = Pipe()

    def get_pipes(self):
        return self.pipes
