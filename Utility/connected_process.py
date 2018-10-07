"""connected_process.py: Abstract class that inherits from process, contains references to the database interface
and a message pipe"""

from multiprocessing import Process
from threading import Thread
from abc import ABCMeta, abstractmethod


class ConnectedProcess(Process):
    __metaclass__ = ABCMeta

    def __init__(self, name='Unnamed Connected Process', database_interface=None, message_pipe=None):
        super(ConnectedProcess, self).__init__(name=name)
        self.daemon = True
        self.database_interface = database_interface
        self.message_pipe = message_pipe
        self.threads = {}

    def run(self):
        """
        Called after the process is forked and running
        """

        # Instantiate message listener thread
        self.threads['messageListener'] = Thread(target=self._message_listener, name='messageListener')

        # Currently only one thread, but may have more in the future
        for thread in self.threads.values():
            thread.daemon = True
            thread.start()

        self._start_work()

    @abstractmethod
    def _message_listener(self):
        """
        Listens for messages sent from the message relay pipe on its own thread
        """
        raise NotImplementedError("Must override method _message_listener")

    @abstractmethod
    def _start_work(self):
        """
        Callback after the process is running and the message listener is active, runs from the process' main thread
        """
        raise NotImplementedError("Must override method _start_work")
