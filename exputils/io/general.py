##
## This file is part of the exputils package.
##
## Copyright: INRIA
## Year: 2022, 2023
## Contact: chris.reinke@inria.fr
##
## exputils is provided under GPL-3.0-or-later
##
import os

def makedirs(path: str):
    """
    Creates a directory and all intermediate directories if they do not exist in a file path.

    Parameters:
        path (str): The directory path to create.
    """

    if not os.path.isdir(path):
        os.makedirs(path)


def makedirs_for_file(filepath: str):
    """
    Creates the necessary directories for a given file path if they do not already exist.

    Parameters:
        filepath (str): The complete file path for which the directories are to be created.
    """

    directory_path, _ = os.path.split(filepath)
    makedirs(directory_path)

