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
        self._session_start_time = None

        logging.getLogger().setLevel(logging_level)

    def run(self):
        try:
            while True:
                if not self._cmds_q.empty():
                    cmd = self._cmds_q.get()
                    if cmd[0] == "start":
                        for key in self._tokens:
                            self._tokens[key] = True
                    if cmd[0] == "stop":
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
        for ok_q in self._ok_qs.values():
            ok_q.put(time())

    def _try_ok(self):
        if False in self._tokens.values():
            return
        if self._T <= 0 or self._session_start_time is None or \
            time() - self._session_start_time > self._T:
            self._send_oks()
            self._session_start_time = time()

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

        ok_qs = {}
        for data_stream_recorder in data_stream_recorders:
            ok_q = Queue()
            ok_qs[data_stream_recorder.id] = ok_q
            data_stream_recorder.set_qs(ok_q, self._tokens_q)

        self._syncer = _DataStreamSyncer(frequency, ok_qs, self._cmds_q, self._tokens_q, logging_level)
        self._syncer.start()

    def start(self):
        """ Starts syncer operations """
        self._cmds_q.put(("start",))

    def stop(self):
        """ Stops syncer operations. Destroys syncer process. """
        self._cmds_q.put(("stop",))
        try:
            self._syncer.terminate()
        except Exception:
            pass
