from multiprocessing import Pipe


class MessagePipes:
    def __init__(self, table_names):
        self.features = table_names
        self.pipes = {}
        for table_name in table_names:
            self.pipes[f'{table_name}_firehose'] = {}
            self.pipes[f'{table_name}_firehose']['pipe_in'], self.pipes[f'{table_name}_firehose']['pipe_out'] = Pipe()

    def get_pipes(self):
        return self.pipes
