import exputils
import os

class Logger:
    '''

        Configuration:
            numpy_log_mode: String that defines how numpy data is logged.
                'npy': each property is loggend in an individual npy file
                'npz': all properties are combined in a npz file
                'cnpz': all properties are combined in a compressed npz file

            numpy_npz_filename: Name of the npz file if numpy data should be saved in a npz or compressed npz.

    '''

    def __init__(self, **config):

        self.directory = config.get('directory', None) # npy, npz
        self.numpy_log_mode = config.get('numpy_log_mode', 'npy') # npy, npz
        self.numpy_npz_filename = config.get('numpy_npz_filename', 'logging.npz')

        self.data = dict()

    @property
    def directory(self):
        directory = self._directory
        if directory is None:
             directory = exputils.DEFAULT_LOGS_DIRECTORY
        return directory

    @directory.setter
    def directory(self, value):
        self._directory = value

    def __getitem__(self, key):
        return self.data[key]


    def __contains__(self, item):
        return item in self.data


    def items(self):
        return self.data.items()


    def add_value(self, name, value):
        if name not in self.data:
            self.data[name] = []

        self.data[name].append(value)


    def get_log_directory(self, directory=None):
        if directory is None:
            if self.directory is None:
                directory = exputils.DEFAULT_LOGS_DIRECTORY
            else:
                directory = self.directory
        if directory is None:
            raise ValueError('A directory in which the log will be saved must be provided!')


    def save(self, directory=None):
        directory = self.directory if directory is None else directory

        if directory is None:
            raise ValueError('A directory in which the log will be saved must be provided!')

        if self.numpy_log_mode.lower() == 'npy':
            path = directory
        else:
            path = os.path.join(directory, self.numpy_npz_filename)

        exputils.io.save_dict_to_numpy_files(self.data, path, self.numpy_log_mode)


    def load(self, directory=None):
        directory = self.directory if directory is None else directory

        if directory is None:
            raise ValueError('A directory in which the log will be saved must be provided!')

        self.data = exputils.io.load_numpy_files(directory)