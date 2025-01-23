from attr import dataclass
from typing import List, Optional, Tuple
import os
from .experimentstarter import get_scripts, get_script_status, STATUS_FILE_EXTENSION, _is_to_start_status
import re
import exputils as eu


@dataclass
class ScriptProperties:
    date: str = None
    time: str = None
    experiment_id: str  = None
    repetition_idx: int  = None
    script_path: str = None
    status: str = None


@dataclass
class ScriptStatistics:
    total: int = 0
    todo: int = 0
    running: int = 0
    finished: int = 0
    error: int = 0


def get_experiments_status(directory: Optional[str] = None,
                           status_file_extension: Optional[str] = None) -> Tuple[List[ScriptProperties], ScriptStatistics]:
    """
    Returns the status of all scripts for all experiments under a specific directory and summary
    statistics.

    This function only detects the status based on existing '*.status' files.
    Scripts for which a status file does not exist, are ignored.

    Arguments:
        directory (str):
            Path to directory under which experiments are located.
            Default is `'./experiments'`.

    Returns:
        script_properies (List[ScriptProperties]):
            List of scripts and their statuses in form of ScriptProperties.
            The properties have the following attributes: date, time, experiment_id, repetition_idx,
            script_path, status.

        statistics (ScriptStatistics):
            Summary statistics for each status (total, todo, running, finished, error).
    """

    if status_file_extension is None:
        status_file_extension = STATUS_FILE_EXTENSION

    #################
    # Walk through the directory to find all status files

    status_files = []
    for dirpath, _, filenames in os.walk(directory):
        for filename in filenames:
            if filename.endswith(status_file_extension):
                status_files.append(os.path.join(dirpath, filename))
    status_files = sorted(status_files)

    ##################
    # create script properties and statistics by going over each status file

    script_properties = []

    statistics = ScriptStatistics()

    # identify and count their statuses
    for file in status_files:
        with (open(file, 'r') as f):
            # read properties from the status file
            lines = f.readlines()
            status_message = lines[-2].strip().split(' ') + lines[-1].strip().split(' ')
            date, time, status = status_message[0], status_message[1], " ".join(status_message[2:]).lower()

            # save properties in respective dataclass
            prop = ScriptProperties()
            prop.date = date
            prop.time = time
            prop.status = status
            prop.script_path = file.replace(status_file_extension, '')

            # detect the experiment id
            # remove part in template that defines the number, for example: {:6d}
            experiment_substr = re.sub('{.*}', '', eu.EXPERIMENT_DIRECTORY_TEMPLATE)
            # search for the experiment sub_directory
            re_match = re.search('/(' + experiment_substr + '\d*)', prop.script_path)
            if re_match is not None:
                prop.experiment_id = re_match.group(1).replace(experiment_substr, '')

            # detect repetition id
            # remove part in template that defines the number, for example: {:6d}
            repetition_substr = re.sub('{.*}', '', eu.REPETITION_DIRECTORY_TEMPLATE)
            # search for the repetition sub_directory
            re_match = re.search('/(' + repetition_substr + '\d*)', prop.script_path)
            if re_match is not None:
                prop.repetition_idx = int(re_match.group(1).replace(repetition_substr, ''))

            script_properties.append(prop)

            # compute the statistics
            if status in ['todo', 'running', 'finished', 'error']:
                cur_stat = statistics.__getattribute__(status)
                statistics.__setattr__(status, cur_stat + 1)
            else:
                # all other status messages are considered as some info message while the script
                # is still running
                statistics.running += 1
            statistics.total += 1

    return script_properties, statistics


def get_number_of_scripts_to_execute(directory: Optional[str] = None,
                                     start_scripts: str = 'run_*.py') -> int:
    """
    Identifies the number of scripts that have to be executed in the experiments directory.
    Scripts that have to be executed have either the status 'none', 'todo', 'error', or 'unfinished'.

    Parameters:
        directory (str):
            Directory in which the start scripts are searched.
            Default is `'./experiments'`.
        start_scripts (str):
            Filename of the start script file that are searched under the given target directory.
            Can include '*' to search for scripts, for example 'run_*.py'.
            The default `'run_*'` will look for all files that start with 'run' and try to start them.

    Returns:
        n_scripts (int): Number of scripts that have to be executed.
    """

    scripts = get_scripts(directory=directory, start_scripts=start_scripts)

    n = 0
    for script in scripts:
        status = get_script_status(script)
        if _is_to_start_status(status):
            n += 1

    return n


def get_number_of_scripts(directory: Optional[str] = None,
                          start_scripts: str = 'run_*.py'):
    """
    Identifies the number of all scripts in the experiments directory regardless of their execution
    status.

    Parameters:
        directory (str):
            Directory in which the start scripts are searched.
            Default is `'./experiments'`.
        start_scripts (str):
            Filename of the start script file that are searched under the given target directory.
            Can include '*' to search for scripts, for example 'run_*.py'.
            The default `'run_*'` will look for all files that start with 'run' and try to start them.

    Returns:
        n_scripts (int): Number of scripts.
    """

    scripts = get_scripts(directory=directory, start_scripts=start_scripts)
    return len(scripts)