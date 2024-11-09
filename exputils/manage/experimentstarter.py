##
## This file is part of the exputils package.
##
## Copyright: INRIA
## Year: 2022, 2023
## Contact: chris.reinke@inria.fr
##
## exputils is provided under GPL-3.0-or-later
##
import glob
import os
import subprocess
import time
from typing import Optional, Union

import exputils
import numpy as np
from datetime import datetime
import fasteners

STATUS_FILE_EXTENSION = '.status'


def start_slurm_experiments(directory=None, start_scripts='*.slurm', is_parallel=True, verbose=False, post_start_wait_time=0):

    return start_experiments(
        directory=directory,
        start_scripts=start_scripts,
        start_command='sbatch {}',
        parallel=is_parallel,
        verbose=verbose,
        post_start_wait_time=post_start_wait_time,
        write_status_files_automatically=False
    )


def start_torque_experiments(directory=None, start_scripts='*.torque', is_parallel=True, verbose=False, post_start_wait_time=0):

    return start_experiments(
        directory=directory,
        start_scripts=start_scripts,
        start_command='qsub {}',
        parallel=is_parallel,
        verbose=verbose,
        post_start_wait_time=post_start_wait_time,
        write_status_files_automatically=False
    )


def start_experiments(directory: Optional[str] = None,
                      start_scripts: Optional[str] = 'run_*.py',
                      start_command: Optional[str] = '{}',
                      parallel: Union[bool, int] = True,
                      is_chdir: bool = True,
                      verbose: bool = False,
                      post_start_wait_time: float = 0.,
                      write_status_files_automatically: bool = True):
    """
    Searches all the start scripts of experiments and/or repetitions in the experiments folder
    and executes them either in parallel or sequentially.

    It also documents their execution status (todo, running, finished, error) in a status file
    that allows it to identify if a script should be executed or not when used again on the
    same target directory.

    Parameters:
        directory (str):
            Directory in which the start scripts are searched.
            Default is `'./experiments'`.
        start_scripts (str):
            Filename of the start script file that are searched under the given target directory.
            Can include '*' to search for scripts, for example 'run_*.py'.
            The default `'run_*'` will look for all files that start with 'run' and try to start them.
        parallel (bool, int):
            Defines if scripts should be started in parallel and how many are allowed to run in parallel.
            If `False` then the scripts are started sequentially one after another.
            If `True` then the scripts are started and executed in parallel all at once.
            If an integer, then the number defines how many scripts can run in parallel.
        is_chdir (bool):
            Before starting a script, should the main process change to its working directory.
        verbose (bool):
            Should verbose output with more information given. Default is `False`.
        post_start_wait_time (float):
            Time waited before one process is started after another.
        write_status_files_automatically (bool):
            Should status files that document if scripts were started and executed be
            written by the manager. These are important to identify if an experiment or repetition
            did run already.
    """

    if directory is None:
        directory = os.path.join('.', exputils.DEFAULT_EXPERIMENTS_DIRECTORY)

    # handle number of parallel processes
    if isinstance(parallel, bool):
        if parallel:
            n_parallel = np.inf
        else:
            n_parallel = 1
    elif isinstance(parallel, int):
        if parallel <= 0:
            raise ValueError('Number of parallel processes must be larger 0!')
        else:
            n_parallel = parallel
    else:
        raise ValueError('Argument \'parallel\' must be either a bool or an integer number!')

    if is_chdir:
        cwd = os.getcwd()

    # get all scripts
    all_scripts = get_scripts(directory=directory, start_scripts=start_scripts)

    ignored_scripts = []
    todo_scripts = []
    # check their initial status and write one for the scripts that will be started
    for script in all_scripts:

        # lock processing of the script, so that no other running experimentstarter is updating its status in parallel
        with _get_script_lock(script):

            status = get_script_status(script)

            if status is None:
                if write_status_files_automatically:
                    _update_script_status(script, 'todo')
                todo_scripts.append(script)

            elif status.lower() != 'finished':
                todo_scripts.append(script)

            else:
                ignored_scripts.append((script, status))

    # start all in parallel if wanted
    if n_parallel == np.inf:
        n_parallel = len(todo_scripts)

    # started process and their corresponding scripts
    started_processes = []
    started_scripts = []
    finished_processes_idxs = []

    next_todo_script_idx = 0
    n_active_processes = 0

    # run as long as there is an active process or we did not finish all processes yet
    while n_active_processes > 0 or next_todo_script_idx < len(todo_scripts):

        # start as many processes as parallel processes are allowed
        for i in range(n_parallel - n_active_processes):

            # stop starting processes when all scripts are started
            if next_todo_script_idx < len(todo_scripts):

                script = todo_scripts[next_todo_script_idx]
                next_todo_script_idx += 1

                # lock processing of the script, so that no other running experimentstarter is starting it in parallel
                with _get_script_lock(script):

                    # check the script status, only start if needed
                    status = get_script_status(script)
                    if _is_to_start_status(status):

                        if write_status_files_automatically:
                            _update_script_status(script, 'running')

                        # start
                        script_directory = os.path.dirname(script)
                        script_path_in_its_working_directory = os.path.join('.', os.path.basename(script))

                        print('{} start {!r} (previous status: {}) ...'.format(datetime.now().strftime("%Y/%m/%d %H:%M:%S"), script, status))

                        process_environ = {
                            **os.environ,
                            "EU_STATUS_FILE": script_path_in_its_working_directory + STATUS_FILE_EXTENSION,
                        }

                        if is_chdir:
                            os.chdir(script_directory)
                            process = subprocess.Popen(start_command.format(script_path_in_its_working_directory).split(), env=process_environ)
                            os.chdir(cwd)
                        else:
                            process = subprocess.Popen(start_command.format(script).split(), cwd=script_directory, env=process_environ)

                        started_processes.append(process)
                        started_scripts.append(script)

                        if post_start_wait_time > 0:
                            time.sleep(post_start_wait_time)

                    else:
                        # do not start
                        ignored_scripts.append((script, status))

        # check the activity of the started processes
        n_active_processes = 0
        for p_idx, process in enumerate(started_processes):

            if p_idx not in finished_processes_idxs:

                if process.poll() is None:
                    n_active_processes += 1
                else:
                    finished_processes_idxs.append(p_idx)
                    if process.returncode == 0:
                        status = 'finished'
                    else:
                        status = 'error'

                    if write_status_files_automatically:
                        _update_script_status(started_scripts[p_idx], status)

                    print('{} finished {!r} (status: {})'.format(datetime.now().strftime("%Y/%m/%d %H:%M:%S"), started_scripts[p_idx], status))

        if n_active_processes > 0:
            time.sleep(0.5) # sleep half a second before checking again

    if verbose:
        if ignored_scripts:
            print('Ignored scripts:')
            for (script_path, status) in ignored_scripts:
                print('\t- {!r} (status: {})'.format(script_path, status))


def _is_to_start_status(status):
    """Returns true if the given status means that the script should be started, otherwise false."""
    return status is None or status.lower().startswith('todo') or status.lower().startswith('none') or status.lower().startswith('error') or status.lower().startswith('unfinished')


def _get_script_lock(script):
    """Create a lock for the given script that can be used to have exclusive access to write its status."""
    return fasteners.InterProcessLock(script + '.lock')


def _update_script_status(script, status):
    """
    Updates the status for the given script.

     :param script: Path to the script.
     :param status: New status.
    """

    status_file_path = script + STATUS_FILE_EXTENSION

    time_str = datetime.now().strftime("%Y/%m/%d %H:%M:%S")

    with open(status_file_path, 'a+') as file:
        file.write( time_str + "\n" + status + "\n")


def get_scripts(directory: Optional[str] = None,
                start_scripts: Optional[str] = 'run_*.py') -> list:
    """
    Searches all start scripts in the experiments directory.

    Parameters:
        directory (str):
            Directory in which the start scripts are searched.
            Default is `'./experiments'`.
        start_scripts (str):
            Filename of the start script file that are searched under the given target directory.
            Can include '*' to search for scripts, for example 'run_*.py'.
            The default `'run_*'` will look for all files that start with 'run' and try to start them.

    Returns:
        scripts (list): List of filepaths to the start scripts.
    """

    if directory is None:
        directory = os.path.join('.', exputils.DEFAULT_EXPERIMENTS_DIRECTORY)

    # find all start scripts
    scripts = glob.iglob(os.path.join(directory, '**', start_scripts), recursive=True)
    scripts = list(scripts)
    scripts.sort()

    return scripts


def get_script_status(script_file: str) -> Optional[str]:
    """
    Returns the execution status of a certain start script.

    Parameters:
        script_file (str): Path to the script file.

    Returns:
        status (str, None):
            Status as a string. Usually `'todo'`, `'error'`, `'running'`, or `'finished'`.
            `None` if no status exists.
    """
    status = None

    status_file_path = script_file + STATUS_FILE_EXTENSION

    if os.path.isfile(status_file_path):
        # read status
        with open(status_file_path, 'r') as f:
            lines = f.read().splitlines()
            if len(lines) > 0:
                status = lines[-1]

    return status


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




