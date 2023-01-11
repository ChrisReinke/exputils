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
import numpy as np
import os
from glob import glob


def save_dict_to_numpy_files(data, path='.', mode = 'npy'):
    """
    Saves the data in a dictionary to numpy files. Either several npy or one npz (compressed or un-compressed).

    :param data: Dictionary with data.
    :param path: Path to folder if npy files are saved, or to the npz file.
    :param mode: Defines if npy files or one npz file are saved: 'npy', 'npz', 'cnpz' - compressed. (Default: 'npy')
    """

    # save logs in numpy format if they exist
    if mode.lower() == 'npy':
        eu.io.makedirs(path)
        for name, values in data.items():
            np.save(os.path.join(path, name), values)

    elif mode.lower() == 'npz':
        eu.io.makedirs_for_file(path)
        np.savez(path, **data)

    elif mode.lower() == 'cnpz':
        eu.io.makedirs_for_file(path)
        np.savez_compressed(path, **data)

    else:
        raise ValueError('Unknown numpy logging mode {!r}!'.format(mode))


def load_numpy_files(directory, allowed_data_filter=None, denied_data_filter=None, allow_pickle=True):
    """Loads data from all npy and npz files in a given directory."""

    if allowed_data_filter is not None and denied_data_filter is not None:
        raise ValueError('in_data_filter and out_data_filter can not both be set, only one or none!')

    if not os.path.isdir(directory):
        raise FileNotFoundError('Directory {!r} does not exist!'.format(directory))

    data = eu.AttrDict()

    for file in glob(os.path.join(directory, '*.npy')):
        stat_name = os.path.splitext(os.path.basename(file))[0]

        if eu.misc.is_allowed(stat_name, allowed_list=allowed_data_filter, denied_list=denied_data_filter):
            try:
                stat_val = np.load(file, allow_pickle=allow_pickle)
            except FileNotFoundError:
                raise
            except Exception as e:
                raise Exception('Exception during loading of file {!r}!'.format(file)) from e

            if len(stat_val.shape) == 0:
                stat_val = stat_val.dtype.type(stat_val)

            data[stat_name] = stat_val

    for file in glob(os.path.join(directory, '*.npz')):
        stat_name = os.path.splitext(os.path.basename(file))[0]
        if eu.misc.is_allowed(stat_name, allowed_list=allowed_data_filter, denied_list=denied_data_filter):
            try:
                stat_vals = eu.AttrDict(np.load(file, allow_pickle=allow_pickle))
            except FileNotFoundError:
                raise
            except Exception as e:
                raise Exception('Exception during loading of file {!r}!'.format(file)) from e

            # remove data that should not be loaded
            keys = [k for k, v in stat_vals.items() if not eu.misc.is_allowed(k, allowed_list=allowed_data_filter, denied_list=denied_data_filter)]
            for x in keys:
                del stat_vals[x]

            # numpy encapsulates scalars as darrays with an empty shape
            # recover the original type
            for substat_name, substat_val in stat_vals.items():
                if len(substat_val.shape) == 0:
                    stat_vals[substat_name] = substat_val.dtype.type(substat_val)

            data[stat_name] = stat_vals

    return data


