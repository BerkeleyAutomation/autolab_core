"""
Class to record streams of data from a given object in separate process.
Author: Jacky Liang
"""
import os, sys, logging
from multiprocess import Process, Queue
from uuid import uuid4
import IPython

class _DataStreamRecorder(Process):

    def __init__(self, name, id, data_sampler_method, tokens_q, cmds_q, data_q, ok_q, args, kwargs, logging_level):
        Process.__init__(self)
        self._data_sampler_method = data_sampler_method
        self._tokens_q = tokens_q
        self._cmds_q = cmds_q
        self._data_q = data_q
        self._ok_q = ok_q
        self._args = args
        self._kwargs = kwargs

        self._recording = True
        self._id = id

        self._name = name

        logging.getLogger().setLevel(logging_level)

    def run(self):
        try:
            logging.info("Starting data recording on {0}".format(self._name))
            self._tokens_q.put(("return", self._id))
            while True:
                if not self._cmds_q.empty():
                    cmd = self._cmds_q.get()
                    if cmd[0] == 'stop':
                        break
                    elif cmd[0] == 'pause':
                        self._recording = False
                    elif cmd[0] == 'resume':
                        self._recording = True
                    elif cmd[0] == 'params':
                        self._args = cmd[1]
                        self._kwargs = cmd[2]

                if self._recording and not self._ok_q.empty():
                    print 'taking token with {0}'.format(self._name)
                    timestamp = self._ok_q.get()
                    self._tokens_q.put(("take", self._id))
                    data = self._data_sampler_method(*self._args, **self._kwargs)
                    self._data_q.put((timestamp, data))
                    self._tokens_q.put(("return", self._id))

        except KeyboardInterrupt:
            logging.info("Shutting down data streamer on {0}".format(self._name))
            sys.exit(0)

class DataStreamRecorder:

    def __init__(self, name, data_sampler_method, logging_level=logging.DEBUG):
        """ Initializes a DataStreamRecorder
        Parameters
        ----------
            name : string
                    User-friendly identifier for this data stream
            data_sampler_method : function
                    Method to call to retrieve data
            logging_level : logging level, optional
                    Logging level for internal recorder process
                    Defaults to logging.DEBUG
        """
        self._data_sampler_method = data_sampler_method
        self._logging_level = logging_level

        self._has_set_sampler_params = False
        self._recording = False

        self._name = name

        self._cmds_q = Queue()
        self._data_q = Queue()

        self._id = uuid4()

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    def set_qs(self, ok_q, tokens_q):
        self._ok_q = ok_q
        self._tokens_q = tokens_q

    def flush(self):
        """ Returns a list of all current data """
        if self._recording:
            raise Exception("Cannot flush data queue while recording!")
        data = []
        while self._data_q.qsize() > 0:
            data.append(self._data_q.get())
        return data

    def start(self, *args, **kwargs):
        """ Starts recording
        Parameters
        ----------
            *args : any
                    Ordinary args used for calling the specified data sampler method
            **kwargs : any
                    Keyword args used for calling the specified data sampler method
        """
        while not self._cmds_q.empty():
            self._cmds_q.get_nowait()
        while not self._data_q.empty():
            self._data_q.get_nowait()
        self._recorder = _DataStreamRecorder(self._name, self._id, self._data_sampler_method, self._tokens_q,
                                            self._cmds_q, self._data_q, self._ok_q, args, kwargs, self._logging_level)
        self._recorder.start()
        self._recording = True

    def stop(self):
        """ Stops recording. Returns all recorded data and their timestamps. Destroys recorder process."""
        self.pause()
        data = self.flush()
        self._cmds_q.put(("stop",))
        try:
            self._recorder.terminate()
        except Exception:
            pass
        self._recording = False
        return data

    def pause(self):
        """ Pauses recording """
        self._cmds_q.put(("pause",))
        self._recording = False

    def resume(self):
        """ Resumes recording """
        self._cmds_q.put(("resume",))
        self._recording = True

    def change_data_sampler_params(self, *args, **kwargs):
        """ Chanes args and kwargs for data sampler method
        Parameters
        ----------
            *args : any
                    Ordinary args used for calling the specified data sampler method
            **kwargs : any
                    Keyword args used for calling the specified data sampler method
        """
        self._cmds_q.put(('params', args, kwargs))
