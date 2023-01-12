##
## This file is part of the exputils package.
##
## Copyright: INRIA
## Year: 2022, 2023
## Contact: chris.reinke@inria.fr
##
## exputils is provided under GPL-3.0-or-later
##
import exputils as eu
from exputils.data.logger import Logger

# holds the global logger object
log = Logger()


def reset():
    """
    Resets the log to an empty exputils.data.Logger.
    """
    global log
    log = Logger()


def get_log():
    """
    Returns the current logger.
    """
    global log
    return log


def set_log(new_log):
    """
    Sets the given logger to be the global log
    """
    global log
    log = new_log


def set_directory(directory):
    """
    Sets the directory path for the log.
    """
    log.directory = directory


def get_directory():
    """
    Returns the directory path of the log.
    """
    return log.directory


def contains(name):
    """
    Returns True if items for the the given name exists in the log. Otherwise False.
    """
    return (name in log)


def clear(name=None):
    """
    Clears the data of the whole log or of a specific data element.

    :param name: If none, then the whole log is cleared, otherwise only the data element with the given name.
                 (default=None)
    """
    log.clear(name=name)


def get_item(name):
    """
    Returns the item from the log with the given name.
    """
    return log[name]


def add_value(name, value, log_to_tb=None, tb_global_step=None, tb_walltime=None):
    """
    Adds a new value to the log. Values are stored in numpy arrays. Allows to log in parallel to tensorboard if the value is a scalar.

    :param name (string): Name of the value. (Can use dividers '/' for tensorbard. They are replaced by '_' for the normal log. )
    :param value: Value to save.
    :param log_to_tb (bool): True if the value should be logged to tensorboard. False if not.
        If None, then it gets logged if the tensorboard is active. (default = None)
    :param tb_global_step (int): Tensorboards global step value to record. (default = None)
    :param tb_walltime (float): Optional tensorboard override of default walltime (time.time()) with seconds after epoch of event. (default = None)
    """
    log.add_value(name, value, log_to_tb, tb_global_step, tb_walltime)


def add_scalar(name, scalar, log_to_tb=None, tb_global_step=None, tb_walltime=None):
    """
    Adds a new scalar to the log. Scalars are stored in numpy arrays. Allows to log in parallel to tensorboard if the value is a scalar.

    :param name (string): Name of the value. (Can use dividers '/' for tensorbard. They are replaced by '_' for the normal log. )
    :param scalar: Value to save.
    :param log_to_tb (bool): True if the value should be logged to tensorboard. False if not.
        If None, then it gets logged if the tensorboard is active. (default = None)
    :param tb_global_step (int): Tensorboards global step value to record. (default = None)
    :param tb_walltime (float): Optional tensorboard override of default walltime (time.time()) with seconds after epoch of event. (default = None)
    """
    log.add_scalar(name, scalar, log_to_tb, tb_global_step, tb_walltime)


def add_histogram(name, values, log_to_tb=None, tb_global_step=None, tb_walltime=None):
    """
    Adds a new histogram to the log. Histograms data are stored in numpy arrays. Allows to log in parallel to tensorboard.

    :param: name (string): Name of the value. (Can use dividers '/' for tensorbard. They are replaced by '_' for the normal log. )
    :param values: Values to build histogram.
    :param log_to_tb (bool): True if the value should be logged to tensorboard. False if not.
        If None, then it gets logged if the tensorboard is active. (default = None)
    :param tb_global_step (int): Tensorboards global step value to record. (default = None)
    :param tb_walltime (float): Optional tensorboard override of default walltime (time.time()) with seconds after epoch of event. (default = None)
    """
    log.add_histogram(name, values, log_to_tb, tb_global_step, tb_walltime)


def get_values(name):
    """
    Returns the values for the given name. Values are stored in numpy arrays.
    """
    return log[name]


def add_object(name, obj):
    """
    Adds a new object to the log. Objects are stored in a list and saved as files using dill.
    """
    log.add_object(name, obj)


def get_objects(name):
    """
    Returns the objects for the given name. Objects are stored in a list.
    """
    return log[name]


def add_single_object(name, obj, directory=None):
    """
    Adds a single object to the log which is directly written to the hard drive and not stored in memory.
    The objects is saved via dill.
    """
    log.add_single_object(name, obj, directory=directory)


def items():
    """
    Returns the items in the log as a list of tuples with the name and values of the items.
    """
    return log.items()


def save(directory=None):
    """
    Saves the log to its defined directory.

    :param directory: Optional path to the directory.
    """
    log.save(directory=directory)


def load(directory=None, load_objects=False):
    """
    Loads the items from a log directory into the log.

    :param directory: Optional path to the directory.
    :param load_objects: If True then also objects (dill files) are loaded. Default: False.
    """
    log.load(directory=directory, load_objects=load_objects)


def load_single_object(name):
    """
    Loads a single object from a log and returns it.

    :return:
    """
    return log.load_single_object(name)


def set_config(config=None, **kwargs):
    """
    Sets the config of the log.

    :param config: Dictionary with config parameters.
    :param kwargs: Arguments list of config parameters.
    """
    log.config = eu.combine_dicts(kwargs, config, log.config)


####################################################
# TENSORBOARD

def tensorboard():
    """The tensorboard SummaryWriter that can be used to log data to the tensorboard.

    The logged data will only be stored in the tensorboard logs!

    Example:

    log.

    """
    return log.tensorboard


def create_tensorboard(config=None, **kwargs):
    """
    Creates a tensorboard that can be used for logging.

    :param config (dict): Dictionary with the configuration of the tensorboard. Has the same entries as the parameters below. (default = None)
    :param log_dir (string): Save directory location. Default is experiments/tensorboard_logs/exp_<experiment_id>/rep_<repetition_id>/<date>_<time>.
    :param purge_step (int): When logging crashes at step T+XT+XT+X and restarts at step TTT, any events whose global_step larger or equal to TTT
        will be purged and hidden from TensorBoard. Note that crashed and resumed experiments should have the same log_dir.
    :param: max_queue (int): Size of the queue for pending events and summaries before one of the ‘add’ calls forces a flush to disk. (default = 10)
    :param flush_secs (int): How often, in seconds, to flush the pending events and summaries to disk. (default = 120)
    :param filename_suffix (string): Suffix added to all event filenames in the log_dir directory. (default = '.tblog')

    :return: SummaryWriter of the tensorboard (See https://pytorch.org/docs/stable/tensorboard.html).
    """

    return log.create_tensorboard(config=config, **kwargs)


def activate_tensorboard(config=None, **kwargs):
    """
    Activates a tensorboard that can be used for logging.
    If it is activated, then when the function add_value/add_scalar is used and a scalar is given, the tensorboard automatically logs it too.
    Creates a tensorboard if non existed so far.

    :param config (dict): Dictionary with the configuration of the tensorboard. Has the same entries as the parameters below. (default = None)
    :param log_dir (string): Save directory location. Default is experiments/tensorboard_logs/exp_<experiment_id>/rep_<repetition_id>/<date>_<time>.
    :param purge_step (int): When logging crashes at step T+XT+XT+X and restarts at step TTT, any events whose global_step larger or equal to TTT
        will be purged and hidden from TensorBoard. Note that crashed and resumed experiments should have the same log_dir.
    :param: max_queue (int): Size of the queue for pending events and summaries before one of the ‘add’ calls forces a flush to disk. (default = 10)
    :param flush_secs (int): How often, in seconds, to flush the pending events and summaries to disk. (default = 120)
    :param filename_suffix (string): Suffix added to all event filenames in the log_dir directory. (default = '.tblog')

    :return: SummaryWriter of the tensorboard (See https://pytorch.org/docs/stable/tensorboard.html).
    """

    return log.activate_tensorboard(config=config, **kwargs)


def deactivate_tensorboard():
    """
    Deactivates a tensorboard. Afterwards, values will not be automatically logged via the add_value / add_scalar function to the tensorboard.
    """
    return log.deactivate_tensorboard()


def is_tensorboard_active():
    """Returns true, if the tensorboard is active."""
    return log.is_tensorboard_active



