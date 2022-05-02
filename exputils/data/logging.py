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
    Adds a new value to the log. Values are stored in numpy arrays.

    :param log_to_tb: Should the value be logged to tensorboard if scalar?
    :param tb_global_step: Globale step for tensorboard.
    :param tb_walltime: Walltime for tensorboard.
    """
    log.add_value(name, value, log_to_tb, tb_global_step, tb_walltime)


def add_scalar(name, scalar, log_to_tb=None, tb_global_step=None, tb_walltime=None):
    """
    Adds a new value to the log. Values are stored in numpy arrays.

    :param log_to_tb: Should the value be logged to tensorboard?
    :param tb_global_step: Globale step for tensorboard.
    :param tb_walltime: Walltime for tensorboard.
    """
    log.add_scalar(name, scalar, log_to_tb, tb_global_step, tb_walltime)

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


def create_tensorboard(config=None, **kwargs):
    """
    Creates a tensorboard that can be used for logging.


    :param config: Tensorboard config. See torch.utils.tensorboard.SummaryWriter documentation.
    :param kwargs: Tensorboard config. See torch.utils.tensorboard.SummaryWriter documentation.
    :return: SummaryWriter
    """

    return log.create_tensorboard(config=config, **kwargs)


def activate_tensorboard(config=None, **kwargs):
    """
    Activates a tensorboard that can be used for logging.
    If it is activated, then when the function add_value is used and a scalar is given, the tensorboard automatically logs it too.
    Creates a tensorboard if non existed so far.

    :param config: Tensorboard config. See torch.utils.tensorboard.SummaryWriter documentation.
    :param kwargs: Tensorboard config. See torch.utils.tensorboard.SummaryWriter documentation.
    :return: SummaryWriter
    """

    return log.activate_tensorboard(config=config, **kwargs)


def deactivate_tensorboard():
    """
    Deactivates a tensorboard that can be used for logging.
    """

    return log.deactivate_tensorboard()


def tensorboard():
    """The tensorboard SummaryWriter that can be used to log data to the tensorboard."""

    return log.tensorboard