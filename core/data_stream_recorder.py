"""
Class to record streams of data from a given object in separate process.
Author: Jacky Liang
"""
import os, sys, logging
from multiprocess import Process, Queue
from uuid import uuid4
import IPython
from joblib import dump, load

def _cache_to_file(cache_path, start, end, target_filename):
    all_data = []
    for i in range(start, end):
        data = load(os.path.join(cache_path, "{0}.jb".format(i)))
        all_data.extend(data)
    dump(data, target_filename, 3)

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
        self._data_qs = [Queue()]
        self._ok_q = None
        self._tokens_q = None

        self._id = uuid4()

        self._save_every = save_every
        self._cache_path = cache_path
        self._saving_cache = cache_path is not None
        if self._saving_cache:
            self._save_path = os.path.join(cache_path, self._id)
            if os.path.exists(self._cache_path):
                os.mkdirs(self._cache_path)

        self._start_data_segment = 0
        self._cur_data_segment = 0
        self._saving_ps = []

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
                        if self._saving_cache:
                            cur_data_q = self._data_qs[self._cur_data_segment]
                            self._save_cache(cur_data_q)
                            self._cur_data_segment += 1
                            self._data_qs.append(Queue())
                        self._save_cache()
                    elif cmd[0] == 'resume':
                        self._recording = True
                    elif cmd[0] == 'save':
                        self._save_data(cmd[1])
                    elif cmd[0] == 'params':
                        self._args = cmd[1]
                        self._kwargs = cmd[2]

                if self._recording and not self._ok_q.empty():
                    timestamp = self._ok_q.get()
                    self._tokens_q.put(("take", self._id))

                    data = self._data_sampler_method(*self._args, **self._kwargs)

                    cur_data_q = self._data_qs[self._cur_data_segment]
                    if self._saving_cache and self._cur_data_q.qsize() == self._save_every:
                        self._save_cache(cur_data_q)
                        self._cur_data_segment += 1
                        cur_data_q = Queue()
                        self._data_qs.append(cur_data_q)
                    cur_data_q.put((timestamp, data))

                    self._tokens_q.put(("return", self._id))

        except KeyboardInterrupt:
            logging.info("Shutting down data streamer on {0}".format(self._name))
            sys.exit(0)

    def _extract_q(self, q):
        vals = []
        while q.qsize() > 0:
            vals.append(q.get())
        return vals

    def _save_data(self, filename):
        if self._saving_cache:
            p = Process(target=_cache_to_file, args=(self._save_path, self._start_data_segment, self._cur_data_segment, filename))
            p.start()
            self._start_data_segment = self._cur_data_segment
        else:
            data = self._extract_q(self._data_qs[0])
            p = Process(target=dump, args=(data, filename, 3))
            p.start()

    def _save_cache(self, data_q):
        if not self._save_cache:
            raise Exception("Cannot save cache if no cache path was specified.")
        data = self._extract_q(data_q)
        p = Process(target=dump, args=(data, os.path.join(self._save_path, "{0}.jb".format(self._cur_data_segment)), 3))
        p.start()
        self._saving_ps.append(p)

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
        while not self._data_qs[self._cur_data_segment].empty():
            self._data_qs[self._cur_data_segment].get_nowait()

        self._args = args
        self._kwargs = kwargs

        self._recording = True
        self.start()

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
        if self._saving_cache:
            raise Exception("Cannot flush current data when saving to cache.")
        data = self._extract_q(self._data_q[0])
        return data

    def save_data(self, filename):
        if self._recording:
            raise Exception("Cannot flush data queue while recording!")
        self._cmds_q.put(("save", filename))

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
