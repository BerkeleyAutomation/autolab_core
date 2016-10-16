"""
Class to handle experiment logging.
Authors: Jeff, Jacky
"""
from abc import ABCMeta, abstractmethod
import os
import shutil
import subprocess
from time import time

import numpy as np
import matplotlib.pyplot as plt

from csv_model import CSVModel

class ExperimentLogger:
    """Abstract class for experiment logging.

    Experiments are logged to CSV files, which are encapsulated with the 
    :obj:`CSVModel` class.
    """

    __metaclass__ = ABCMeta

    _MASTER_RECORD_FILENAME = 'experiment_records.csv'

    def __init__(self, experiment_root_path):
        """Initialize an ExperimentLogger.

        Parameters
        ----------
        experiment_root_path : :obj:`str`
            The root directory in which to save experiment files.
        """
        self.experiment_root_path = experiment_root_path

        self.master_record_filepath = os.path.join(self.experiment_root_path,
                                                   ExperimentLogger._MASTER_RECORD_FILENAME)
        self.master_record = CSVModel.get_or_create(self.master_record_filepath,
                                                    self.experiment_meta_headers_types)

        last_uid = self.master_record.get_cur_uid()
        self.id = ExperimentLogger.gen_experiment_id(last_uid)
        self._master_record_uid = self.master_record.insert(self.experiment_meta_dict)

        self.experiment_path = os.path.join(self.experiment_root_path, self.id)
        os.makedirs(self.experiment_path)

        # internal dir struct 
        self._dirs = {}

    @property
    def dirs(self):
        """:obj:`dict` : A dictionary mapping strings to dictionaries of
        strings. This represents the file system hierarchy under the root
        experimental directory.
        """
        return self._dirs.copy()

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

    def construct_internal_dirs(self, dirs, realize=False):
        """Add directories to the hierarchy under the experimental
        root directory.

        Parameters
        ----------
        dirs : :obj:`list` of :obj:`str`
            A list of nested directories, from outermost to innermost.
            The diretories will be created if they don't exist in order,
            with the first entry in the list existing directly within the
            experimental root directory.

        realize : bool
            If true, directories that don't already exist are created in the
            filesystem. Otherwise, they just exist internally in this object's
            records.
        """
        cur_dir = self._dirs
        for dir in dirs:
            if dir not in cur_dir:
                cur_dir[dir] = {}
            cur_dir = cur_dir[dir]
        if realize:
            self._realize_dirs(dirs)

    def construct_internal_dirs_group(self, group_dirs):
        """Add a set of nested directories to the hierarchy under the experimental
        root directory.

        Note
        ----
        The new directories are only created in this object's records, but not
        in the actual filesystem.

        Parameters
        ----------
        group_dirs : :obj:`list` of :obj:`list` of :obj:`str`
            A list of nested directories. Each nested directory structure is a
            list of directory names from outermost to innermost.
            The diretories will be created if they don't exist in order,
            with the first entry each list existing directly within the
            experimental root directory.
        """
        for dirs in group_dirs:
            self.construct_internal_dirs(dirs)

    def has_internal_dirs(self, dirs):
        """Does a hierarchy of internal directories exist within the root
        experimental directory?

        Note
        ----
        This only evaluates if the directory structure exists within this
        object's records, and NOT if it has been realized in the actual
        filesystem.

        Parameters
        ----------
        dirs : :obj:`list` of :obj:`str`
            A list of directory names. These are a nested set of directories
            from outermost to innermost, with the first directory lying within
            the root experimental directory.

        Returns
        -------
        bool
            True if the full list exists as a nested directory structure, and
            False if any directory is missing as the hierarchy is traversed.
        """
        cur_dir = self._dirs
        for dir in dirs:
            if dir not in cur_dir:
                return False
            cur_dir = cur_dir[dir]
        return True

    def dirs_to_path(self, dirs):
        """Get the path represented by the list of dirs.

        Parameters
        ----------
        dirs : :obj:`list` of :obj:`str`
            A list of directory names. These are a nested set of directories
            from outermost to innermost, with the first directory lying within
            the root experimental directory.

        Returns
        -------
        :obj:`str`
            An absolute path to the directory represented by the dirs list.
        """
        rel_path = '/'.join(dirs)
        abs_path = os.path.join(self.experiment_path, rel_path)
        return abs_path

    def remove_dirs(self, dirs):
        """Remove a full hierarcy of directories recursively.

        Parameters
        ----------
        dirs : :obj:`list` of :obj:`str`
            A list of directory names. These are a nested set of directories
            from outermost to innermost, with the first directory lying within
            the root experimental directory.

        Raises
        ------
        Exception
            If the given directory hierarchy doesn't exist.
        """
        if not self.has_internal_dirs(dirs):
            raise Exception("Directory has not been construted internally! {0}".format(dirs))

        path = self.dirs_to_path(dirs)
        if os.path.exists(path):
            subprocess.call(['trash', '-r', path])

        # remove the deepest node
        cur_dir = self.dirs
        for dir in dirs[:-1]:
            cur_dir = cur_dir[dir]
        cur_dir.pop(dirs[-1])

        for i in range(len(dirs) - 1):
            cur_dir = self._dirs
            depth = len(dirs) - i - 2
            for j in range(depth):
                cur_dir = cur_dir[dirs[j]]

            dir_to_remove = dirs[depth]
            if not cur_dir[dir_to_remove]:
                cur_dir.pop(dir_to_remove)
            else:
                break

    def copy_to_dir(self, src_file_path, target_dirs):
        """Copy a file to an experimental directory.

        Parameters
        ----------
        src_file_path : :obj:`str`
            The path to the file to copy.

        target_dirs : :obj:`list` of :obj:`str`
            A list of directory names. These are a nested set of directories
            from outermost to innermost, with the first directory lying within
            the root experimental directory. The given file will be copied into
            the last directory in this list.
        """
        abs_path = self._realize_dirs(target_dirs)
        basename = os.path.basename(src_file_path)
        target_file_path = os.path.join(abs_path, basename)

        shutil.copyfile(src_file_path, target_file_path)

    def copy_dirs(self, src_dirs_path, target_dirs):
        """Copy the contents of a target directory to the given experimental
        directory.

        Parameters
        ----------
        src_dirs_path : :obj:`str`
            The path to the directory to copy.

        target_dirs : :obj:`list` of :obj:`str`
            A list of directory names. These are a nested set of directories
            from outermost to innermost, with the first directory lying within
            the root experimental directory. The given file will be copied into
            the last directory in this list.

        Raises
        ------
        Exception
            If the directory indicated by target_dirs has not yet been
            constructed internally or is not empty externally within the
            filesystem.
        """

        if not self.has_internal_dirs(target_dirs):
            raise Exception("Directory has not been constructed internally! {0}".format(target_dirs))

        target_dirs_path = self.dirs_to_path(target_dirs)
        if os.path.exists(target_dirs_path):
            if len(os.listdir(target_dirs_path)) > 0:
                raise Exception("Target path for copying directories is not empty! Got: {0}".format(target_dirs_path))
            else:
                os.rmdir(target_dirs_path)
        shutil.copytree(src_dirs_path, target_dirs_path)

    @abstractmethod
    def experiment_meta_dict(self):
        """Returns the dict of meta information for this experiment.

        Returns
        -------
        :obj:`dict`
            The metadata for this experiment.
        """
        pass

    @abstractmethod
    def experiment_meta_headers_types(self):
        """Returns the headers and types of meta information for this experiment.
        """
        pass

    @staticmethod
    def gen_experiment_id(record_uid, n=10):
        """Generate a random string for naming experiments.

        Parameters
        ----------
        record_uid : :obj:`str`
            A UID for the experiment.

        n : int
            The number of characters to appear after the UID in the string.

        Returns
        -------
        :obj:`str`
            A string of the format {UID}_{random string}.
        """
        chrs = 'abcdefghijklmnopqrstuvwxyz'
        inds = np.random.randint(0, len(chrs), size=n)

        strings = ''.join([chrs[i] for i in inds])
        return '{0}_{1}'.format(record_uid, strings)

    @staticmethod
    def pretty_str_time(dt):
        """Get a pretty string for the given datetime object.

        Parameters
        ----------
        :obj:`datetime`
            A datetime object to format.

        Returns
        -------
        :obj:`str`
            The `datetime` formatted as {year}_{month}_{day}_{hour}_{minute}.
        """
        return "{0}_{1}_{2}_{3}:{4}".format(dt.year, dt.month, dt.day, dt.hour, dt.minute)

    def _realize_dirs(self, dirs):
        """Create filesystem directories for a directory hierarchy that has
        already been added internally.

        Parameters
        ----------
        dirs : :obj:`list` of :obj:`str`
            A list of directory names. These are a nested set of directories
            from outermost to innermost, with the first directory lying within
            the root experimental directory.

        Returns
        -------
        :obj:`str`
            The absolute path to the end of the newly-created directory
            hierarchy.

        Raises
        ------
        Exception
            If the directory structure represented by dirs does not yet exist
            internally within this object.
        """
        if not self.has_internal_dirs(dirs):
            raise Exception("Directory has not been constructed internally! {0}".format(dirs))
        abs_path = self.dirs_to_path(dirs)
        if not os.path.exists(abs_path):
            os.makedirs(abs_path)
        return abs_path

class EvaluateGraspsExperimentLogger(ExperimentLogger):
    """An experiment logger for evaluating grasps.
    """

    LABELINGS_HEADERS_TYPES = (
            ('experiment_id','str'),
            ('gripper_name','str'),
            ('object_key','str'),
            ('stp_id','str'),
            ('grasp_id','int'),
            ('y_offset_deg','float'),
            ('trial_num','int'),
            ('registration_duration','float'),
            ('grasp_duration','float'),
            ('trial_duration','float'),
            ('gripper_width','float'),
            ('path_lift_color_img','str'),
            ('path_lift_depth_img','str'),
            ('path_pose_histories','str'),
            ('path_state_histories','str'),
            ('path_video','str'),
            ('path_trial','str'),
            ('success','int')
        )

    def __init__(self, experiment_root_path, cfg, object_key, stp_id, supervisor):
        """Initialize an ExperimentLogger for evaluating grasps on objects.

        Parameters
        ----------
        experiment_root_path : :obj:`str`
            The root directory in which to save experiment files.

        cfg : :obj:`dict`
            The config dictionary for the experiments.

        object_key : :obj:`str`
            The string key for the object being grasped.

        stp_id : :obj:`str`
            The string id for the stable pose of the object.

        supervisor : :obj:`str`
            The string name of the supervisor type.
        """
        self.cfg = cfg
        self.supervisor = supervisor
        self.object_key = object_key
        self.stp_id = stp_id

        super(EvaluateGraspsExperimentLogger, self).__init__(experiment_root_path)

        labelings_path = os.path.join(self.experiment_root_path, 'labelings.csv')
        self._labels_model = CSVModel.get_or_create(labelings_path, EvaluateGraspsExperimentLogger.LABELINGS_HEADERS_TYPES)

    @property
    def experiment_meta_headers_types(self):
        """:obj:`tuple` of :obj:`tuple` of :obj:`str` : A tuple of tuples, each
        of which maps string header names to string type names.
        """
        return (
                ('experiment_id','str'),
                ('use','bool'),
                ('object_key','str'),
                ('stp_id','str'),
                ('time_started','str'),
                ('time_stopped','str'),
                ('duration','float'),
                ('supervisor','str'),
        )

    @property
    def experiment_meta_dict(self):
        """:obj:`dict` : The metadata of the experiment as a dictionary.
        """
        return {
                'experiment_id': self.id, 
                'use': True,
                'object_key': self.object_key,
                'stp_id': self.stp_id,
                'supervisor': self.supervisor
                }

    def get_dirs_to_grasp_trial(self, grasp_info):
        """Get a directory path list to save a grasp trial in.

        Parameters
        ----------
        grasp_info : :obj:`dict`
            A dictionary of information about the grasp. Must contain
            grasp_id, times_evaluated, and y_deg_offset fields.

        Returns
        -------
        :obj:`list` of :obj:`str`
            A list that represents the directory hierarchy to save information
            about the next grasp trial to. The format is
            grasp_{id}_offset_{y_offset}/trial_{trial_num}.
        """
        grasp_id = grasp_info['grasp_id']
        trial_num = grasp_info['times_evaled']
        y_offset_deg = grasp_info['y_offset_deg']

        y_offset_deg_str = str(y_offset_deg).replace('.', '_')
        dirs = ['grasp_{0}_offset_{1}'.format(grasp_id, y_offset_deg_str), 'trial_{0}'.format(trial_num)]
        return dirs

    def get_path_to_grasp_trial(self, grasp_info):
        """Get the actual path string to save a grasp trial in.

        Parameters
        ----------
        grasp_info : :obj:`dict`
            A dictionary of information about the grasp. Must contain
            grasp_id, times_evaluated, and y_deg_offset fields.

        Returns
        -------
        :obj:`str`
            The absolute path to the directory to save the grasp trial's
            information in.
        """
        dirs = self.get_dirs_to_grasp_trial(grasp_info)
        self.construct_internal_dirs(dirs, realize=True)

        trial_path = self.dirs_to_path(dirs)
        return trial_path

    def remove_grasp_trial_logs(self, grasp_info):
        """Remove the directories containing a given grasp trial.

        Parameters
        ----------
        grasp_info : :obj:`dict`
            A dictionary of information about the grasp. Must contain
            grasp_id, times_evaluated, and y_deg_offset fields.
        """
        dirs = self.get_dirs_to_grasp_trial(grasp_info)
        self.remove_dirs(dirs)

    def record_single_grasp_trial(self, grasp_info, color_im, depth_im, registration_duration, 
                                    grasp_duration, gripper_width, robot_arm, registration_figs,
                                    object_key, stp_id, trial_start):
        """Save data for a single grasp trial.

        Parameters
        ----------
        grasp_info : :obj:`dict`
            A dictionary of information about the grasp. Must contain
            grasp_id, times_evaluated, and y_deg_offset fields.

        color_im : :obj:`ColorImage`
            A color image for the grasp.

        depth_im : :obj:`DepthImage`
            A depth image for the grasp.

        registration_duration : :obj:`float`
            The duration of registration for the grasp (in seconds).

        grasp_duration : :obj:`float`
            The duration of grasp execution (in seconds).

        gripper_width : :obj:`float`
            The width of the gripper (in meters).

        robot_arm : :obj:`YuMiArm`
            An arm object for the robot of choice.

        registration_figs : :obj:`list` of :obj:`dict`
            A list of dictionaries containing object figures.

        object_key : :obj:`str`
            A key name for the object.

        stp_id : :obj:`str`
            A key name for the stable pose of the object.

        trial_start : float
            The time of the start of the trial.
        """
        trial_path = self.get_path_to_grasp_trial(grasp_info)

        # save motions
        pose_histories_filename = os.path.join(trial_path, 'pose_histories.yml')
        state_histories_filename = os.path.join(trial_path, 'state_histories.yml')
        robot_arm.flush_pose_histories(pose_histories_filename)
        robot_arm.flush_state_histories(state_histories_filename)

        # save lift images
        lift_color_path = os.path.join(trial_path, 'lift_color.npz')
        lift_depth_path = os.path.join(trial_path, 'lift_depth.npz')
        color_im.savefig(trial_path, 'lift_color', format=self.cfg['save_image_format'])
        color_im.save(lift_color_path)
        depth_im.savefig(trial_path, 'lift_depth', format=self.cfg['save_image_format'], cmap=plt.cm.gray)
        depth_im.save(lift_depth_path) 

        # save registration debug figs
        for registration_fig in registration_figs:
            fig = registration_fig['fig']
            figname = registration_fig['figname']
            fig.savefig(os.path.join(trial_path, figname))

        data = {
            'experiment_id': self.id,
            'gripper_name': self.cfg['gripper'],
            'object_key': object_key,
            'stp_id': stp_id,
            'grasp_id': grasp_info['grasp_id'],
            'y_offset_deg': float(grasp_info['y_offset_deg']),
            'trial_num': grasp_info['times_evaled'],
            'registration_duration': float(registration_duration),
            'grasp_duration': float(grasp_duration),
            'trial_duration': float(time() - trial_start),
            'gripper_width': float(gripper_width),
            'path_lift_color_img': lift_color_path,
            'path_lift_depth_img': lift_depth_path,
            'path_pose_histories': pose_histories_filename,
            'path_state_histories': state_histories_filename,
            'path_video': os.path.join(trial_path, 'video.avi'),
            'path_trial': trial_path,
        }

        self._labels_model.insert(data)

    @staticmethod
    def meta_info_exp(experiment_path, id):
        """Return the metainfo for a given experiment path.

        Parameters
        ----------
        experiment_path : :obj:`str`
            The root directory in which the experiment files exist.

        id : :obj:`str`
            The ID for the experiment we wish to retrieve metainfo for.

        Returns
        -------
        :obj:`tuple`
            The supervisor type, object key, and stable pose ID for the
            experiment.
        """
        masters_record = CSVModel.load(os.path.join(experiment_path, _MASTER_RECORD_FILENAME))
        row = masters_record.get_by_col('experiment_id', id)
        return row['supervisor'], row['object_key'], row['stp_id']
