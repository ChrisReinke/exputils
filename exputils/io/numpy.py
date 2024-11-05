##
## This file is part of the exputils package.
##
## Copyright: INRIA
## Year: 2022, 2023
## Contact: chris.reinke@inria.fr
##
## exputils is provided under GPL-3.0-or-later
##
from typing import Optional
import exputils as eu
import numpy as np
import os
from glob import glob
from exputils.misc.attrdict import AttrDict


def save_dict_to_numpy_files(data: dict,
                             path: Optional[str] = '.',
                             mode: Optional[str] = 'npy'):
    """Saves a dictionary with numpy arrays to numpy files (either .npy, .npz, or .npz compressed formats).

    Parameters:
        data (dict):
            Dictionary containing the data to be saved, with keys as filenames and values as data to be saved.
        path (str):
            Directory or file path where the numpy files will be saved.
            Default is the current directory.
        mode (str):
            Mode in which to save the data.
            Can be 'npy', 'npz', or 'cnpz'.
            Default is 'npy'.

    Raises:
        ValueError: If an invalid mode is provided.
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
        raise ValueError('Unknown numpy logging mode {!r}! Only \'npy\', \'npz\' and \'cnpz\' are allowed.'.format(mode))


def load_numpy_files(directory: str,
                    allowed_data_filter: Optional[list] = None,
                    denied_data_filter: Optional[list] = None,
                    allow_pickle: bool = True) -> AttrDict:
    """Loads numpy files from a specified directory into an AttrDict.

    Parameters:
        directory (str):
            The path to the directory containing the numpy files.
        allowed_data_filter (list, optional):
            A list of allowed file names to be loaded.
            If specified, only files with names in this list will be loaded.
        denied_data_filter (list, optional):
            A list of denied file names to be excluded from loading.
            If specified, files with names in this list will not be loaded.
        allow_pickle (bool):
            Whether to allow loading pickled (serialized) objects.
            Default is True. <br>
            :warning: This could allow arbitrary code execution. Only load files you trust!

    Raises:
        ValueError:
            If both allowed_data_filter and denied_data_filter are specified.
        FileNotFoundError:
            If the specified directory does not exist.
        Exception:
            If an error occurs during loading of a file.

    Returns:
        data (AttrDict):
            Dictionary with loaded data where the keys are file names without extensions
            and the values are the respective numpy arrays.
    """

    if allowed_data_filter is not None and denied_data_filter is not None:
        raise ValueError('in_data_filter and out_data_filter can not both be set, only one or none!')

    if not os.path.isdir(directory):
        raise FileNotFoundError('Directory {!r} does not exist!'.format(directory))

    data = AttrDict()

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
                stat_vals = AttrDict(np.load(file, allow_pickle=allow_pickle))
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


