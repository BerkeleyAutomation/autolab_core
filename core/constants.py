"""
Global constants for the ALAN codebase
Author: Jeff Mahler
"""
METERS_TO_MM = 1000.0
MM_TO_METERS = 1.0 / METERS_TO_MM

SUPPORTED_IMAGE_EXTS = ['.png', '.jpg']
MAX_DEPTH = 1.5 # maximum expected depth reading
MAX_IR = 65535 # maximum possible ir reading

CAFFE_CNN_CHANNEL_SWAP = (2, 1, 0)
CAFFE_CNN_CHANNELS = 3

TF_EXTENSION = '.tf'
INTR_EXTENSION = '.intr'