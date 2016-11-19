import IPython
from core import DataStreamRecorder, DataStreamSyncer
from time import time, sleep
import os
from perception import OpenCVCameraSensor

if __name__ == "__main__":
    cam = OpenCVCameraSensor(0)
    cam.start()

    timestamp = lambda : time()

    data_cam = DataStreamRecorder("webcam", cam.frames)
    data_time = DataStreamRecorder("time", timestamp)

    syncer = DataStreamSyncer([data_cam, data_time], frequency=30)
    syncer.start()

    sleep(3)

    syncer.pause()
    data_cam.save_data("webcam.jb")
    data_time.save_data("time.jb")

    IPython.embed()
    exit(0)
