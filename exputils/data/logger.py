##
## This file is part of the exputils package.
##
## Copyright: INRIA
## Year: 2022, 2023
## Contact: chris.reinke@inria.fr
##
## exputils is provided under GPL-3.0-or-later
##
from exputils.misc.attrdict import AttrDict, combine_dicts
import exputils as eu
import numpy as np
import os
import copy
import warnings
from datetime import datetime
import re

# try to import tensorboard
try:
    import torch.utils.tensorboard
    is_exist_tensorboard_module = True
except ImportError:
    is_exist_tensorboard_module = False


def _get_safe_name(name):
    """Returns a name that is safe to save as a log entry."""
    return name.replace('/', '_')


class Logger:
    """
        Configuration:
            numpy_log_mode: String that defines how numpy data is logged.
                'npy': each property is loggend in an individual npy file
                'npz': all properties are combined in a npz file
                'cnpz': all properties are combined in a compressed npz file

            numpy_npz_filename: Name of the npz file if numpy data should be saved in a npz or compressed npz.
    """

    def default_config(self):
        dc = AttrDict(
            directory = None,
            numpy_log_mode = 'npy',
            numpy_npz_filename = 'logging.npz',

            tensorboard = AttrDict(
                log_dir = None,
                filename_suffix = '.tblog',
                purge_step=None,
                max_queue=10,
                flush_secs=120,
            )
        )
        return dc


    def __init__(self, config=None, **kwargs):
        self.config = combine_dicts(kwargs, config, self.default_config())

        self.numpy_data = dict()
        self.object_data = dict()

        self._tensorboard_writer = None
        self._is_tensorboard_active = False


    @property
    def directory(self):
        directory = self.config.directory
        if directory is None:
             directory = eu.DEFAULT_DATA_DIRECTORY
        return directory


    @directory.setter
    def directory(self, value):
        self.config.directory = value


    def __getitem__(self, key):
        key = _get_safe_name(key)

        if key in self.numpy_data:
            return self.numpy_data[key]
        elif key in self.object_data:
            return self.object_data[key]
        else:
            return None


    def __contains__(self, item):
        item = _get_safe_name(item)

        return (item in self.numpy_data) or (item in self.object_data)


    def items(self):
        return list(self.numpy_data.items()) + list(self.object_data.items())


    def clear(self, name=None):
        """
        Clears the data of the whole log or of a specific data element.

        :param name: If none, then the whole log is cleared, otherwise only the data element with the given name.
                     (default=None)
        """
        if name is not None:
            name = _get_safe_name(name)

        if name is None:
            self.numpy_data.clear()
            self.object_data.clear()
        else:
            if name not in self:
                raise ValueError('Unknown data element with name {!r}!'.format(name))

            if name in self.numpy_data:
                del self.numpy_data[name]

            if name in self.object_data:
                del self.numpy_data[name]


    def add_value(self, name, val, log_to_tb=None, tb_global_step=None, tb_walltime=None):

        safe_name = _get_safe_name(name)

        if safe_name not in self.numpy_data:
            self.numpy_data[safe_name] = []

        self.numpy_data[safe_name].append(val)

        if log_to_tb is True or (self._is_tensorboard_active and log_to_tb is not False):
            # identify if the value is a scalar, if yes, then add it to tensorboard
            if not isinstance(val, (list, tuple, np.ndarray)):
                self.tensorboard.add_scalar(name, val, tb_global_step, tb_walltime)
            else:
                warnings.warn('Can not log value for "{}" to tensorboard as it is not a scalar. Value: {}'.format(name, val))


    def add_scalar(self, name, scalar, log_to_tb=None, tb_global_step=None, tb_walltime=None):
        # same functionality as add_value, but is more consistent with the naming of tensorboard API
        self.add_value(name, scalar, log_to_tb=log_to_tb, tb_global_step=tb_global_step, tb_walltime=tb_walltime)


    def add_histogram(self, name, values, log_to_tb=None, tb_global_step=None, tb_walltime=None):

        safe_name = _get_safe_name(name)

        if safe_name not in self.numpy_data:
            self.numpy_data[safe_name] = []

        self.numpy_data[safe_name].append(values)

        if log_to_tb is True or (self._is_tensorboard_active and log_to_tb is not False):
            # values must be a numpy array
            values = np.array(values)
            self.tensorboard.add_histogram(name, values, global_step=tb_global_step, walltime=tb_walltime)


    def add_object(self, name, obj):
        """
        Adds an object to the log that will be saved in a dill file when the log is saved.

        :param name:
        :param obj:
        :return:
        """
        name = _get_safe_name(name)

        if name not in self.object_data:
            self.object_data[name] = []

        self.object_data[name].append(copy.deepcopy(obj))


    def add_single_object(self, name, obj, directory=None):
        """
        Adds a single object to the log by directly writing it to a file.
        Overwrites existing object data with the same name.
        """
        if directory is None:
            directory = self.directory

        name = _get_safe_name(name)

        file_path = os.path.join(directory, name)
        eu.io.save_dill(obj, file_path)


    def load_single_object(self, name):
        """
        Loads a single object from a file.

        :param name: Name of the object.
        :return: Loaded object.
        """
        name = _get_safe_name(name)

        file_path = os.path.join(self.directory, name)
        return eu.io.load_dill(file_path)


    def save(self, directory=None):
        directory = self.directory if directory is None else directory

        if directory is None:
            raise ValueError('A directory in which the log will be saved must be provided!')

        # make sure the dsirectory exists
        eu.io.makedirs(directory)

        # numpy data

        if self.config.numpy_log_mode.lower() == 'npy':
            path = directory
        else:
            path = os.path.join(directory, self.config.numpy_npz_filename)

        eu.io.save_dict_to_numpy_files(self.numpy_data, path, self.config.numpy_log_mode)

        # object data
        for obj_name, obj in self.object_data.items():
            file_path = os.path.join(directory, obj_name)
            eu.io.save_dill(obj, file_path)

        # save also tensorboard if one exists
        if self._tensorboard_writer is not None:
            self._tensorboard_writer.flush()


    def load(self, directory=None, load_objects=False):
        directory = self.directory if directory is None else directory

        if directory is None:
            raise ValueError('A directory in which the log will be saved must be provided!')

        self.numpy_data = eu.io.load_numpy_files(directory)

        # in the case that all data was logged into a npz file
        if len(self.numpy_data) == 1 and 'logging' in self.numpy_data:
            self.numpy_data = self.numpy_data['logging']

        for key, item in self.numpy_data.items():
            self.numpy_data[key] = item.tolist()

        if load_objects:
            self.object_data = eu.io.load_dill_files(directory)
        else:
            self.object_data = dict()


    @property
    def is_tensorboard_active(self):
        """Return True if a tensorboard is active and can be used, otherwise False."""
        return self._is_tensorboard_active


    @property
    def tensorboard(self):
        """Tensorboard SummaryWriter."""

        if self._tensorboard_writer is None:
            self.create_tensorboard()

        return self._tensorboard_writer


    def create_tensorboard(self, config=None, **kwargs):
        """Creates a tensorboard"""

        if not is_exist_tensorboard_module:
            raise ImportError('Tensorboard module torch.utils.tensorboard does not exist!')

        self.config.tensorboard = eu.combine_dicts(kwargs, config, self.config.tensorboard)

        # identify which experiment and repetition we are in, to set the tensorboard folder
        experiment_name = eu.misc.get_experiment_name()
        repetition_name = eu.misc.get_repetition_name()

        if self.config.tensorboard.log_dir is None:
            # create the logs in the experiment folder which is located on top of the repetition and experiment folder if they exist

            log_dir = ''

            if experiment_name is not None:
                log_dir = os.path.join(log_dir, '..')

            if repetition_name is not None:
                log_dir = os.path.join(log_dir, '..')

            log_dir = os.path.join(log_dir, 'tensorboard_logs')

            self.config.tensorboard.log_dir = log_dir

        # add the experiment and repetition name to the log path, to create sub logs for them
        if experiment_name is not None:
            experiment_name = re.sub('_0{1,5}', '_', experiment_name)
            experiment_name = experiment_name.replace('experiment', 'exp')
            self.config.tensorboard.log_dir = os.path.join(self.config.tensorboard.log_dir, experiment_name)
        if repetition_name is not None:
            repetition_name = re.sub('_0{1,5}', '_', repetition_name)
            repetition_name = repetition_name.replace('experiment', 'exp')
            self.config.tensorboard.log_dir = os.path.join(self.config.tensorboard.log_dir, repetition_name.replace('repetition', 'rep'))

        dt = datetime.now()
        self.config.tensorboard.log_dir = os.path.join(self.config.tensorboard.log_dir, dt.strftime('%y.%m.%d_%H.%M'))

        if self._tensorboard_writer is not None:
            self._tensorboard_writer.flush()
            warnings.warn('Tensorboard SummaryWriter existed already. Creating a new one ...')

        self._tensorboard_writer = torch.utils.tensorboard.SummaryWriter(**self.config.tensorboard)

        return self._tensorboard_writer


    def activate_tensorboard(self, config=None, **kwargs):
        """Activates the tensorboard to automatically also log values that are given to the log.
        If not tensorboard exists, one is created."""

        if self._tensorboard_writer is None:
            self.create_tensorboard(config=config, **kwargs)

        self._is_tensorboard_active = True

        return self._tensorboard_writer


    def deactivate_tensorboard(self):
        """Deactivates the tensorboard to automatically also log values that are given to the log."""
        if self._is_tensorboard_active:
            self._is_tensorboard_active = False
            self._tensorboard_writer.flush()
