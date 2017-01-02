'''
Class to handle experiment logging.
Authors: Jeff, Jacky
'''
from abc import ABCMeta, abstractmethod
import os
import csv
import IPython
import shutil
import subprocess
from datetime import datetime
from time import time
import logging

import numpy as np
import matplotlib.pyplot as plt

from csv_model import CSVModel
from yaml_config import YamlConfig
from utils import gen_experiment_id

class ExperimentLogger:
    """Abstract class for experiment logging.

    Experiments are logged to CSV files, which are encapsulated with the 
    :obj:`CSVModel` class.
    """
    __metaclass__ = ABCMeta
    
    _MASTER_RECORD_FILENAME = 'experiment_record.csv'    

    def __init__(self, experiment_root_path, experiment_tag='experiment'):
        """Initialize an ExperimentLogger.

        Parameters
        ----------
        experiment_root_path : :obj:`str`
            The root directory in which to save experiment files.
        experiment_tag : :obj:`str`
            The tag to use when prefixing new experiments
        """
        self.experiment_root_path = experiment_root_path
        
        # open the master record
        self.master_record_filepath = os.path.join(self.experiment_root_path, ExperimentRecorder._MASTER_RECORD_FILENAME)
        self.master_record = CSVModel.get_or_create(self.master_record_filepath, self.experiment_meta_headers)
        
        # add new experiment to the master record
        self.id = ExperimentRecorder.gen_experiment_ref(experiment_tag)
        self._master_record_uid = self.master_record.insert(self.experiment_meta_data)

        # make experiment output dir
        self.experiment_path = os.path.join(self.experiment_root_path, self.id)
        if not os.path.exists(self.experiment_path):
            os.makedirs(self.experiment_path)

        # redirect logging statements to a file
        experiment_log = os.path.join(self.experiment_path, '%s.log' %(self.id))
        formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
        hdlr = logging.FileHandler(experiment_log)
        hdlr.setFormatter(formatter)
        logging.getLogger().addHandler(hdlr) 

    @staticmethod
    def gen_experiment_ref(experiment_tag, n=10):
        """ Generate a random string for naming.

        Parameters
        ----------
        experiment_tag : :obj:`str`
            tag to prefix name with
        n : int
            number of random chars to use

        Returns
        -------
        :obj:`str`
            string experiment ref
        """
        experiment_id = gen_experiment_id(n=n)
        return '{0}_{1}'.format(experiment_tag, experiment_id)
        
    def update_master_record(self, data):
        """Update a row of the experimental master record CSV with the given data.

        Parameters
        ----------
        uid : int
            The UID of the row to update.

        data : :obj:`dict`
            A dictionary mapping keys (header strings) to values, which
            represents the new row.
        """
        self.master_record.update_by_uid(self._master_record_uid, data)
        
    @abstractmethod
    def experiment_meta_headers(self):
        """Returns the dict of header names and types of meta information for the experiments

        Returns
        -------
        :obj:`dict`
            The metadata for this experiment.
        """
        pass

    @abstractmethod
    def experiment_meta_data(self):
        """Returns the dict of header names and value of meta information for the experiments

        Returns
        -------
        :obj:`dict`
            The metadata for this experiment.
        """
        pass
        
