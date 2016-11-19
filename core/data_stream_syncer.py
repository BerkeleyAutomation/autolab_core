"""
Class to sync and rate limit multiple DataStreamRecorders
Author: Jacky Liang
"""
from multiprocess import Process, Queue
from time import time
import logging
import sys
import IPython

class _DataStreamSyncer(Process):

    def __init__(self, frequency, ok_qs, cmds_q, tokens_q, logging_level):
        Process.__init__(self)
        self._cmds_q = cmds_q
        self._tokens_q = tokens_q

        self._ok_qs = ok_qs
        self._tokens = {key : False for key in self._ok_qs.keys()}

        self._T = 1./frequency if frequency > 0 else 0
        self._ok_start_time = None
        self._pause = False

        logging.getLogger().setLevel(logging_level)

    def run(self):
        self._session_start_time = time()
        try:
            while True:
                if not self._cmds_q.empty():
                    cmd = self._cmds_q.get()
                    if cmd[0] == "reset_time":
                        self._session_start_time = time()
                    elif cmd[0] == 'pause':
                        self._pause = True
                        self._take_oks()
                    elif cmd[0] == 'resume':
                        self._pause = False
                    elif cmd[0] == "stop":
                        break
                if not self._tokens_q.empty():
                    motion, id = self._tokens_q.get()
                    if motion == "take":
                        self._tokens[id] = False
                    elif motion == "return":
                        self._tokens[id] = True
                self._try_ok()
        except KeyboardInterrupt:
            logging.debug("Exiting DataStreamSyncer")
            sys.exit(0)

    def _send_oks(self):
        t = self._ok_start_time - self._session_start_time
        for ok_q in self._ok_qs.values():
            ok_q.put(t)

    def _take_oks(self):
        for ok_q in self._ok_qs.values():
            while ok_q.qsize() > 0:
                ok_q.get_nowait()

    def _try_ok(self):
        if self._pause or False in self._tokens.values():
            return
        if self._T <= 0 or self._ok_start_time is None or \
            time() - self._ok_start_time > self._T:
            self._ok_start_time = time()
            self._send_oks()

class DataStreamSyncer:

    def __init__(self, data_stream_recorders, frequency=0, logging_level=logging.DEBUG):
        """
        Instantiates a new DataStreamSyncer

        Parameters
        ----------
            data_stream_recorders : list of DataStreamRecorders to sync
            frequency : float, optional
                    Frequency in hz used for ratelimiting. If set to 0 or less, will not rate limit.
                    Defaults to 0
            logging_level : logging level, optional
                    Logging level for internal syncer process
                    Defaults to logging.DEBUG
        """
        self._cmds_q = Queue()
        self._tokens_q = Queue()

        self._data_stream_recorders = data_stream_recorders
        ok_qs = {}
        for data_stream_recorder in self._data_stream_recorders:
            ok_q = Queue()
            ok_qs[data_stream_recorder.id] = ok_q
            data_stream_recorder._set_qs(ok_q, self._tokens_q)

        self._syncer = _DataStreamSyncer(frequency, ok_qs, self._cmds_q, self._tokens_q, logging_level)
        self._syncer.start()

    def start(self):
        """ Starts syncer operations """
        for recorder in self._data_stream_recorders:
            recorder._start()

    def stop(self):
        """ Stops syncer operations. Destroys syncer process. """
        self._cmds_q.put(("stop",))
        for recorder in self._data_stream_recorders:
            recorder._stop()
        try:
            self._syncer.terminate()
        except Exception:
            pass

    def pause(self):
        self._cmds_q.put(("pause",))
        for recorder in self._data_stream_recorders:
            recorder._pause()

    def resume(self, reset_time=False):
        self._cmds_q.put(("resume",))
        if reset_time:
            self.reset_time()
        for recorder in self._data_stream_recorders:
            recorder._resume()

    def reset_time(self):
        self._cmds_q.put(("reset_time",))

    def flush(self):
        data = {}
        for recorder in self._data_stream_recorders:
            data[recorder.name] = recorder._flush()
        return data
