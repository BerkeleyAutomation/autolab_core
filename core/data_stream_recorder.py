"""
Class to record streams of data from a given object in separate process.
Author: Jacky Liang
"""
import os, sys, logging
from multiprocess import Process, Queue
from uuid import uuid4
import IPython
from joblib import dump

class DataStreamRecorder(Process):

    def __init__(self, name, data_sampler_method, logging_level=logging.DEBUG, cache_path=None, save_every=50):
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
        Process.__init__(self)
        self._data_sampler_method = data_sampler_method
        self._logging_level = logging_level

        self._has_set_sampler_params = False
        self._recording = False

        self._name = name

        self._cmds_q = Queue()
        self._data_q = Queue()
        self._ok_q = None
        self._tokens_q = None

        self._id = uuid4()

        self._cur_data_segment = 0
        self._save_every = save_every
        self._cache_path = cache_path
        self._save_to_hdd = cache_path is not None
        if self._save_to_hdd:
            self._save_path = os.path.join(cache_path, self)
            if os.path.exists(self._cache_path):
                os.mkdirs(self._cache_path)

    def run(self):
        logging.getLogger().setLevel(self._logging_level)
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
                    timestamp = self._ok_q.get()
                    self._tokens_q.put(("take", self._id))
                    data = self._data_sampler_method(*self._args, **self._kwargs)
                    self._data_q.put((timestamp, data))
                    self._tokens_q.put(("return", self._id))

        except KeyboardInterrupt:
            logging.info("Shutting down data streamer on {0}".format(self._name))
            sys.exit(0)

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    def _set_qs(self, ok_q, tokens_q):
        self._ok_q = ok_q
        self._tokens_q = tokens_q

    def _flush(self):
        """ Returns a list of all current data """
        if self._recording:
            raise Exception("Cannot flush data queue while recording!")
        if self._save_to_hdd:
            raise Exception("Cannot flush current data when saving to cache.")
        data = []
        while self._data_q.qsize() > 0:
            data.append(self._data_q.get())
        return data

    def _start_recording(self, *args, **kwargs):
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

        self._args = args
        self._kwargs = kwargs

        self._recording = True
        self.start()

    def _stop(self):
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

    def _pause(self):
        """ Pauses recording """
        self._cmds_q.put(("pause",))
        self._recording = False

    def _resume(self):
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
