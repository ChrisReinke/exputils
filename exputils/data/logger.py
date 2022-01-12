from exputils.misc.attrdict import AttrDict, combine_dicts
import exputils as eu
import os
import copy

# TODO: Feature - tensorbord output
# TODO: Featrue - allow to log sub values, for example: agent.epsilon

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
            numpy_npz_filename = 'logging.npz'
        )
        return dc


    def __init__(self, config=None, **kwargs):
        self.config = combine_dicts(kwargs, config, self.default_config())

        self.numpy_data = dict()
        self.object_data = dict()


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
        if key in self.numpy_data:
            return self.numpy_data[key]
        elif key in self.object_data:
            return self.object_data[key]
        else:
            return None


    def __contains__(self, item):
        return (item in self.numpy_data) or (item in self.object_data)


    def items(self):
        return list(self.numpy_data.items()) + list(self.object_data.items())


    def clear(self, name=None):
        """
        Clears the data of the whole log or of a specific data element.

        :param name: If none, then the whole log is cleared, otherwise only the data element with the given name.
                     (default=None)
        """

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


    def add_value(self, name, value):
        if name not in self.numpy_data:
            self.numpy_data[name] = []

        self.numpy_data[name].append(value)


    def add_object(self, name, obj):
        """
        Adds an object ...

        :param name:
        :param obj:
        :return:
        """
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

        file_path = os.path.join(directory, name)
        eu.io.save_dill(obj, file_path)


    def load_single_object(self, name):
        """
        Loads a single object from a file.

        :param name: Name of the object.
        :return: Loaded object.
        """
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
