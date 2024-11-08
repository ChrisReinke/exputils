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
from typing import Optional

# holds the global logger object
log = Logger()


def reset():
    """
    Resets the log which deletes all data in the memory and resets all changed configuration such
    as the directory path of the log.

    :warning: Data that has been logged after the [save][exputils.data.logging.save] function
    was called will be lost.
    """
    global log
    log = Logger()


def get_log():
    # returns the current logger.
    global log
    return log


def set_log(new_log):
    #Sets the given logger to be the global log
    global log
    log = new_log


def set_directory(directory: str):
    """
    Sets the directory path under which the logs will be saved.
    The default is `./data`.

    If the directory does not exist it will be created.

    Parameters:
        directory (str):
            Path to the directory.

    """
    log.directory = directory


def get_directory() -> str:
    """
    Returns the path to the directory the log.

    Returns:
        directory (str):
            Path to the directory.
    """
    return log.directory


def contains(name: str) -> bool:
    """
    Check if a log entry for the given name exists.

    Parameters:
        name (str): The name to be checked in the log.

    Returns:
        is_contained (bool): True if a log for the name exists, otherwise False.
    """
    return (name in log)


def clear(name: Optional[str] = None):
    """
    Clears the data of all or a specific log entry.

    :warning: Data that has been logged after the [save][exputils.data.logging.save] function
    was called will be lost.

    Parameters:
        name (str):
            Name of the log entry.
            If no name is given, then all log entries will be cleared.
    """
    log.clear(name=name)


def get_item(name: str) -> object:
    """
    Returns the logged data for a certain entry.

    Parameters:
        name (str):
            Name of the log entry.

    Returns:
        Logged data. Usually in form of a numpy array.
    """
    return log[name]


def add_value(name: str,
              value,
              log_to_tb: Optional[bool] = None,
              tb_global_step: Optional[int] = None,
              tb_walltime: Optional[float] = None):
    """
    Adds a value to a log entry with optional parallel TensorBoard logging.

    Parameters:
        name (str):
            The name of the entry where the value is added.
        value (Any):
            The value to be added. Can be a scalar or an array.
        log_to_tb (bool):
            Defines of the value should be logged to TensorBoard in parallel to the standard log.
            If True, log the value to TensorBoard.
            If False, do not log the value to TensorBoard.
            If not specified, then it gets logged if TensorBoard is globally activated.
            See [activate_tensorboard][exputils.data.logging.activate_tensorboard] for more details.
        tb_global_step (int):
            If logging to TensorBoard is active, then this is the global step value to record with
            the value in TensorBoard.
        tb_walltime (float):
            If logging to TensorBoard is active, then this is an optional override for the walltime
            in TensorBoard.
    """
    log.add_value(name, value, log_to_tb, tb_global_step, tb_walltime)


def add_scalar(name: str,
              scalar,
              log_to_tb: Optional[bool] = None,
              tb_global_step: Optional[int] = None,
              tb_walltime: Optional[float] = None):
    """
    Adds a scalar value to a log entry with optional parallel TensorBoard logging.

    Note: Has the same functionality as [add_value][exputils.data.logging.add_value] and exists to
    have a similar named log function as TensorBoard.

    Parameters:
        name (str):
            The name of the entry where the value is added.
        scalar (Any):
            The scalar value to be added.
        log_to_tb (bool):
            Defines of the value should be logged to TensorBoard in parallel to the standard log.
            If True, log the value to TensorBoard.
            If False, do not log the value to TensorBoard.
            If not specified, then it gets logged if TensorBoard is globally activated.
            See [activate_tensorboard][exputils.data.logging.activate_tensorboard] for more details.
        tb_global_step (int):
            If logging to TensorBoard is active, then this is the global step value to record with
            the value in TensorBoard.
        tb_walltime (float):
            If logging to TensorBoard is active, then this is an optional override for the walltime
            in TensorBoard.
    """
    log.add_scalar(name, scalar, log_to_tb, tb_global_step, tb_walltime)


def add_histogram(name: str,
                  values,
                  log_to_tb: Optional[bool] = None,
                  tb_global_step: Optional[int] = None,
                  tb_walltime: Optional[float] = None):
    """
    Adds a histogram which is a one-dimensional array a log entry with optional parallel TensorBoard
    logging.

    This allows to add the values as a histogram plot to TensorBoard.

    Parameters:
        name (str):
            The name of the entry where the value is added.
        values (Any):
            The array of values to be added.
        log_to_tb (bool):
            Defines of the value should be logged to TensorBoard in parallel to the standard log.
            If True, log the value to TensorBoard.
            If False, do not log the value to TensorBoard.
            If not specified, then it gets logged if TensorBoard is globally activated.
            See [activate_tensorboard][exputils.data.logging.activate_tensorboard] for more details.
        tb_global_step (int):
            If logging to TensorBoard is active, then this is the global step value to record with
            the value in TensorBoard.
        tb_walltime (float):
            If logging to TensorBoard is active, then this is an optional override for the walltime
            in TensorBoard.
    """
    log.add_histogram(name, values, log_to_tb, tb_global_step, tb_walltime)


def get_values(name: str):
    """
    Returns the logged data for a certain entry.

    Note: Has the same functionality as [get_item][exputils.data.logging.get_item] and exists to
    have a similar named log function as TensorBoard.

    Parameters:
        name (str):
            Name of the log entry.

    Returns:
        Logged data. Usually in form of a numpy array.
    """
    return log[name]


def add_object(name: str,
               obj: object):
    """
    Adds an object to a log entry. Objects are stored in a list and saved as dill files.

    Parameters:
        name (str):
            The name of the log entry where the object is added.
        obj (object):
            The object to be added to the log.
    """
    log.add_object(name, obj)


def get_objects(name: str) -> list:
    """
    Returns the logged objects for a certain entry.

    Args:
        name (str): Name of the log entry.

    Returns:
        objects (list): Logged objects.
    """
    return log[name]


def add_single_object(name: str,
                      obj: object,
                      directory: Optional[str] = None):
    """
    Logs a single object which is directly written to a dill file and not stored in memory.

    Parameters:
        name (str):
            The name of the object which is used for the filename.
        obj (object):
            The object to be logged.
        directory (str):
            Optional directory path where the dill file for the object is saved.
            Default is the log directory.
    """
    log.add_single_object(name, obj, directory=directory)


def items() -> list:
    """
    Returns all log entries as a list of tuples with the name and values of the entries.

    Returns:
        entries (list): All logged entries.
    """
    return log.items()


def save(directory: Optional[str] = None):
    """
    Saves the log.
    All logged values are stored in memory and only written to disk when this function is called.

    Parameters:
        directory (str):
            Optional directory path where the dill file for the object is saved.
            Default is the log directory.
    """
    log.save(directory=directory)


def load(directory: Optional[str] = None,
         load_objects: bool = False):
    """
    Loads entries from a log directory into the log.
    Afterwards the loaded entries can be accessed via the [items][exputils.data.logging.items] and
    [get_item][exputils.data.logging.get_item] functions.

    Parameters:
        directory (str):
            Optional directory path where the dill file for the object is saved.
            Default is the log directory.
        load_objects (bool):
            True if objects (dill files) that are in the directory should also be loaded.
            Default is False to avoid unintended large loads of objects.
    """
    log.load(directory=directory, load_objects=load_objects)


def load_single_object(name: str) -> object:
    """
    Loads a single object from the log folder and returns it.
    The object is not stored in the log memory.

    Parameters:
        name (str):
            Name of the object which is used for the filename.
            Either with or without the `'.dill'` extension.

    Returns:
        obj (object): Loaded object.
    """
    return log.load_single_object(name)


def set_config(config: Optional[dict] = None,
               **kwargs):
    # sets the config of the underlying Logger object
    # see logger.py for more information
    log.config = eu.combine_dicts(kwargs, config, log.config)


####################################################
# TENSORBOARD

def tensorboard():
    """
    Returns the tensorboard SummaryWriter object used to log values to TensorBoard.

    Returns:
        writer (SummaryWriter): TensorBoard SummaryWriter object.
    """
    return log.tensorboard


def create_tensorboard(config: Optional[dict] = None,
                       **kwargs):
    """
    Creates the SummaryWriter object used to log values to TensorBoard.
    This allows to set its configuration parameters.

    For more details see: https://pytorch.org/docs/stable/tensorboard.html

    Parameters:
        config (dict):
            Optional dictionary with the configuration of the SummaryWriter.
            Has the same entries as the set of "Other Parameters" below.

    Other Parameters:
        log_dir (str):
            Directly location of the TensorBoard log files.
            Default is `experiments/tensorboard_logs/exp_\<experiment_id>/rep_\<repetition_id>/\<date>_\<time>.`
        purge_step (int):
            When logging crashes at step T+XT+XT+X and restarts at step TTT, any events whose
            global_step larger or equal to TTT will be purged and hidden from TensorBoard.
            Note that crashed and resumed experiments should have the same log_dir.
        max_queue (int):
            Size of the queue for pending events and summaries before one of the ‘add’ calls forces
            a flush to disk. (default = 10)
        flush_secs (int):
            How often, in seconds, to flush the pending events and summaries to disk. (default = 120)
        filename_suffix (string):
            Suffix added to all event filenames in the log_dir directory. (default = '.tblog')

    Returns:
        writer (SummaryWriter): TensorBoard SummaryWriter object.
    """

    return log.create_tensorboard(config=config, **kwargs)


def activate_tensorboard(config: Optional[dict] = None,
                         **kwargs):
    """
    Activates parallel TensorBoard logging.
    When it is activated, then the logging functions (
    [add_value][exputils.data.logging.add_value],
    [add_scalar][exputils.data.logging.add_scalar],
    [add_histogram][exputils.data.logging.add_histogram])
    will automatically log each value also in TensorBoard if not otherwise specified for them.

    Creates a TensorBoard SummaryWriter if non is created yet with the [create_tensorboard][exputils.data.logging.create_tensorboard] function.
    If non is created then the configureation of the writer can be defined by the parameters of this function.
    For more details see: https://pytorch.org/docs/stable/tensorboard.html

    Other Parameters:
        log_dir (str):
            Directly location of the TensorBoard log files.
            Default is `experiments/tensorboard_logs/exp_\<experiment_id>/rep_\<repetition_id>/\<date>_\<time>.`
        purge_step (int):
            When logging crashes at step T+XT+XT+X and restarts at step TTT, any events whose
            global_step larger or equal to TTT will be purged and hidden from TensorBoard.
            Note that crashed and resumed experiments should have the same log_dir.
        max_queue (int):
            Size of the queue for pending events and summaries before one of the ‘add’ calls forces
            a flush to disk. (default = 10)
        flush_secs (int):
            How often, in seconds, to flush the pending events and summaries to disk. (default = 120)
        filename_suffix (string):
            Suffix added to all event filenames in the log_dir directory. (default = '.tblog')

    Returns:
        writer (SummaryWriter): TensorBoard SummaryWriter object.
    """

    return log.activate_tensorboard(config=config, **kwargs)


def deactivate_tensorboard():
    """
    Deactivates tensorboard logging.
    Afterwards, values will not be automatically logged via the add_value / add_scalar function
    to the tensorboard.
    """
    return log.deactivate_tensorboard()


def is_tensorboard_active() -> bool:
    """Returns true, if the tensorboard is active.

    Returns:
        is_active (bool): True if the tensorboard is active, otherwise False.
    """
    return log.is_tensorboard_active



