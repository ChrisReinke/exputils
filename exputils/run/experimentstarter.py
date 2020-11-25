import glob
import os
import subprocess
import time
import exputils

def start_slurm_experiments(directory=None, start_scripts='*.slurm', is_parallel=True, verbose=False, post_start_wait_time=0):

    return start_experiments(directory=directory,
                             start_scripts=start_scripts,
                             start_command='sbatch {}',
                             is_parallel=is_parallel,
                             is_chdir = True, # added, otherwise the sbatch does not work
                             verbose=verbose,
                             post_start_wait_time=post_start_wait_time)


def start_torque_experiments(directory=None, start_scripts='*.torque', is_parallel=True, verbose=False, post_start_wait_time=0):

    return start_experiments(directory=directory,
                             start_scripts=start_scripts,
                             start_command='qsub {}',
                             is_parallel=is_parallel,
                             is_chdir = True, # added, otherwise the sbatch does not work
                             verbose=verbose,
                             post_start_wait_time=post_start_wait_time)


def start_experiments(directory=None, start_scripts='*.sh', start_command='{}', is_parallel=True, is_chdir=False, verbose=False, post_start_wait_time=0, is_rerun=False):
    '''

    :param directory:
    :param start_scripts:
    :param start_command:
    :param is_parallel:
    :param is_chdir:
    :param verbose:
    :param post_start_wait_time:
    :param is_rerun: Should finished scripts be rerun. (default: False)
    :return:
    '''

    # TODO: do not restart experiments that have been added as jobs but have not been started yet

    if directory is None:
        directory = os.path.join('.', exputils.DEFAULT_EXPERIMENTS_DIRECTORY)

    # holds tuples of (startscript_path, status)
    scripts = []

    # find all start scripts
    files = glob.iglob(os.path.join(directory, '**', start_scripts), recursive=True)

    # find if they have a job status
    for file in files:

        status_file_path = file + '.status'

        if os.path.isfile(status_file_path):
            # read status
            with open(status_file_path, 'r') as f:
                lines = f.read().splitlines()
                status = lines[-1]
        else:
            status = 'none'

        scripts.append((file, status))


    # the processes that are started for each script
    processes = []

    ignored_scripts = []

    if is_chdir:
        cwd = os.getcwd()

    # start every found script
    for [script_path, status] in scripts:

        if is_rerun or (status is None or status.lower() == 'none' or status.lower() == 'not started' or status.lower() == 'error' or status.lower() == 'unfinished'):
            # start the script

            if verbose:
                print('start {!r} (status: {}) ...'.format(script_path, status))

            script_directory = os.path.dirname(script_path)

            if is_chdir:
                os.chdir(script_directory)
                process = subprocess.Popen(start_command.format(os.path.join('.', os.path.basename(script_path))).split())
            else:
                process = subprocess.Popen(start_command.format(script_path).split(), cwd=script_directory)

            # if not parallel, then wait until current process is finished
            if not is_parallel:
                process.wait()

            if post_start_wait_time > 0:
                time.sleep(post_start_wait_time)

            processes.append(process)

            if is_chdir:
                os.chdir(cwd)

        else:
            ignored_scripts.append((script_path, status))

    if verbose:

        if ignored_scripts:
            print('Ignored scripts:')

            for [script_path, status] in ignored_scripts:
                print('\t- {!r} (status: {})'.format(script_path, status))

    # wait until all processes are finished
    for process in processes:
        process.wait()