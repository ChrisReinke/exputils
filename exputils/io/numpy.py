import exputils
import numpy as np
import os
from glob import glob


def save_dict_to_numpy_files(data, path='.', mode = 'npy'):
    '''
    Saves the data in a dictionary to numpy files. Either several npy or one npz (compressed or un-compressed).

    :param data: Dictionary with data.
    :param path: Path to folder if npy files are saved, or to the npz file.
    :param mode: Defines if npy files or one npz file are saved: 'npy', 'npz', 'cnpz' - compressed. (Default: 'npy')
    '''
    exputils.io.makedirs(path)

    # save logs in numpy format if they exist
    if mode.lower() == 'npy':
        exputils.io.makedirs(path)
        for name, values in data.items():
            np.save(os.path.join(path, name), values)

    elif mode.lower() == 'npz':
        exputils.io.makedirs_for_file(path)
        np.savez(path, **data)

    elif mode.lower() == 'cnpz':
        exputils.io.makedirs_for_file(path)
        np.savez_compressed(path, **data)

    else:
        raise ValueError('Unknown numpy logging mode {!r}!'.format(mode))



def load_numpy_files(directory):
    '''Loads data from all npy and npz files in a given directory.'''

    if not os.path.isdir(directory):
        raise ValueError('Directory {!r} does not exist!'.format(directory))

    data = dict()

    for file in glob(os.path.join(directory, '*.npy')):
        stat_name = os.path.splitext(os.path.basename(file))[0]
        stat_val = np.load(file)

        if len(stat_val.shape) == 0:
            stat_val = stat_val.dtype.type(stat_val)

        data[stat_name] = stat_val

    for file in glob(os.path.join(directory, '*.npz')):
        stat_name = os.path.splitext(os.path.basename(file))[0]
        stat_vals = dict(np.load(file))

        # numpy encapsulates scalars as darrays with an empty shape
        # recover the original type
        for substat_name, substat_val in stat_vals.items():
            if len(substat_val.shape) == 0:
                stat_vals[substat_name] = substat_val.dtype.type(substat_val)

        data[stat_name] = stat_vals

    return data