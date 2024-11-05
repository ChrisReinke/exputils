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
import dill
import os
from glob import glob

DILL_FILE_EXTENSION = 'dill'

def save_dill(obj,
              file_path: str):
    """
    Serializes a Python object and saves it to a file using the [dill](https://pypi.org/project/dill/)
    serialization library.

    Parameters:
        obj (Any):
            The Python object to be serialized.
        file_path (str):
            The file path where the serialized object will be saved.

    <h4>Notes:</h4>

    - If the provided file path does not have the correct file extension for Dill files,
      the extension will be added automatically.
    - The necessary directories for the file path will be created if they do not exist.
    """
    if not file_path.endswith('.' + DILL_FILE_EXTENSION):
        file_path += '.' + DILL_FILE_EXTENSION

    eu.io.makedirs_for_file(file_path)
    with open(file_path, 'wb') as fh:
        dill.dump(obj, fh)


def load_dill(file_path: str) -> object:
    """
    Loads a serialized object from a file using the [dill](https://pypi.org/project/dill/) library.

    Parameters:
        file_path (str):
            The path to the file from which to load the object.
            The file extension is optionally added if not already present.

    Returns:
        obj (Any): The object that was deserialized from the file.

    <h4>Notes:</h4>

    - If the specified file does not exist, the function attempts to append
      the expected file extension (.dill) before throwing an error.
    - :warning: This could allow arbitrary code execution. Only load files you trust!
    """
    if not os.path.exists(file_path):
        if not file_path.endswith('.' + DILL_FILE_EXTENSION):
            file_path += '.' + DILL_FILE_EXTENSION

    with open(file_path, 'rb') as fh:
        obj = dill.load(fh)
    return obj


def load_dill_files(directory: str):
    """
    Loads all serialized objects from a directory using the [dill](https://pypi.org/project/dill/)
    library and returns them in a dictionary.

    Parameters:
        directory (str):
            The path to the directory containing dill-serialized files.

    Raises:
        FileNotFoundError: If the specified directory does not exist.

    Returns:
        data (AttrDict):
            An attribute dictionary where keys are the file names (without extensions) and
            values are the deserialized objects.

    <h4>Notes:</h4>

    - If the specified file does not exist, the function attempts to append
      the expected file extension (.dill) before throwing an error.
    - :warning: This could allow arbitrary code execution. Only load files you trust!
    """

    if not os.path.isdir(directory):
        raise FileNotFoundError('Directory {!r} does not exist!'.format(directory))

    data_dict = eu.AttrDict()

    for file in glob(os.path.join(directory, '*.' + DILL_FILE_EXTENSION)):
        data_name = os.path.splitext(os.path.basename(file))[0]
        data = load_dill(file)
        data_dict[data_name] = data

    return data_dict