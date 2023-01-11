##
## This file is part of the exputils package.
##
## Copyright: INRIA
## Year: 2022, 2023
## Contact: chris.reinke@inria.fr
##
## exputils is provided under GPL-3.0-or-later
##
import numpy as np
import os
import glob
import zipfile
import exputils
import re

def calc_repetition_statistics(statistics, load_experiment_data_func,  *args, statistics_directory=None,
                               recalculate_statistics=False, verbose=False, repetition_directory_template=None,
                               experiment_directory_template=None):
    '''
    Calculates statistics of a single repetition of an experiment.

    :param statistics: List with tuples of the form: (statistic name, statistic function)
    :param args: Directoryies in which the experiments are for which the statistics should be computed.
    :param results_directory:
    :param statistics_directory:
    :return:
    '''

    if len(args) == 0:
        experiments = ['.']
    elif len(args) == 1 and isinstance(args[0], list):
        experiments = args[0]
    else:
        experiments = list(args)

    if repetition_directory_template is None: repetition_directory_template = exputils.REPETITION_DIRECTORY_TEMPLATE
    repetition_directory_template = re.sub('\{.*\}', '', repetition_directory_template)

    if experiment_directory_template is None: experiment_directory_template = exputils.EXPERIMENT_DIRECTORY_TEMPLATE
    experiment_directory_template = re.sub('\{.*\}', '', experiment_directory_template)

    if statistics_directory is None: statistics_directory = exputils.DEFAULT_DATA_DIRECTORY

    def get_data(data, experiment_folder):
        '''Loads the data if the data is not already loaded'''
        if data is None:
            data = load_experiment_data_func(experiment_folder)
        return data

    # identify the experiment folders
    experiment_folders = []
    for folder in experiments:

        found_folders = []

        # make sure the folder has folder form, i.e. with final '/'
        # then take the base directory and search in it
        # this makes sure, that also the direct given folder is looked after, e.g. './experiment_000001' would also be identified
        basedir = os.path.dirname(os.path.join(folder, ''))
        directory_name = os.path.basename(os.path.dirname(basedir))

        # look if directory itself is a repetition experiment
        if directory_name.find(repetition_directory_template) >=0 and os.path.isdir(basedir):
            found_folders.append(basedir)

        # look if there are repetition folders somewhere inside the directory
        if not found_folders:
            for foldername in glob.iglob(os.path.join(basedir,'**',repetition_directory_template + '*'), recursive=True):
                if os.path.isdir(foldername):
                    found_folders.append(foldername)

        # if there are no repetitions, then search for experiment folder
        if not found_folders:
            if directory_name.find('experiment_') >= 0 and os.path.isdir(basedir):
                found_folders.append(basedir)

        if not found_folders:
            for foldername in glob.iglob(os.path.join(basedir, '**', experiment_directory_template + '*'), recursive=True):
                if os.path.isdir(foldername):
                    found_folders.append(foldername)

        if not found_folders:
            # assume the given folder is the the one
            found_folders.append(folder)

        experiment_folders.extend(found_folders)

    # calc statistic if it does not exist already
    for experiment_folder in sorted(experiment_folders):

        data = None

        directory = os.path.join(experiment_folder, statistics_directory)

        if not os.path.isdir(directory):
            os.makedirs(directory)

        if verbose:
            print('Calculate statistics for {!r}:'.format(experiment_folder))

        for statistic_definition in statistics:

            if isinstance(statistic_definition, tuple):
                statistic_name = statistic_definition[0]
                statistic_func = statistic_definition[1]
                statistic_type = statistic_definition[2] if len(statistic_definition) > 2 else 'numpy'
            elif isinstance(statistic_definition, dict):
                statistic_name = statistic_definition['name']
                statistic_func = statistic_definition['function']
                statistic_type = statistic_definition['type'] if 'type' in statistic_definition else 'numpy'
            else:
                raise ValueError('Unknown format for statistic definition {!r}!'.format(statistic_definition))

            # calculate statistics if they do not exist
            filepath_npy = os.path.join(directory, '{}.npy'.format(statistic_name))
            filepath_npz = os.path.join(directory, '{}.npz'.format(statistic_name))
            filepath_zip = os.path.join(directory, '{}.zip'.format(statistic_name))
            directory_path = os.path.join(directory, statistic_name)

            if (not os.path.isfile(filepath_npy) and not os.path.isfile(filepath_npz) and not os.path.isfile(filepath_zip) and not os.path.isdir(directory_path)) or recalculate_statistics:

                if verbose:
                    print('\t{} ...'.format(statistic_name))

                data = get_data(data, experiment_folder)

                if statistic_type == 'numpy':
                    stat = statistic_func(statistic_name, data)

                    if isinstance(stat, dict):
                        np.savez(filepath_npz, **stat)
                    else:
                        np.save(filepath_npy, stat)

                elif statistic_type == 'zip':

                    stat = statistic_func(statistic_name, data)

                    if not isinstance(stat, dict):
                        raise ValueError('Only dictionaries are accepted as data type for zip statistics!')

                    zf = zipfile.ZipFile(filepath_zip,
                                         mode='w',
                                         compression=zipfile.ZIP_DEFLATED,
                                         )
                    try:
                        for sub_stat_name, sub_stat in stat.items():
                            zf.writestr(sub_stat_name, sub_stat)

                    finally:
                        zf.close()

                elif statistic_type == 'directory':
                    if not os.path.isdir(directory_path):
                        os.mkdir(directory_path)
                    statistic_func(statistic_name, data, directory_path)

                else:
                    ValueError('Unknown statistic type {!r}!'.format(statistic_type))



def calc_statistics_over_repetitions(statistics, *args, load_data_func=None, recalculate_statistics=False, verbose=False, repetition_directory_template=None, statistics_directory=None):
    '''
    Calculates the statistics over several repetitions of an experiments.

    :param statistics: List with tuples of the form: (statistic name, statistic function)
    :param args: Directories in which the experiments are for which the statistics should be computed.
    :param results_directory:
    :param statistics_directory:
    :return:
    '''

    if len(args) == 0:
        experiments = ['.']
    elif len(args) == 1 and isinstance(args[0], list):
        experiments = args[0]
    else:
        experiments = list(args)

    if load_data_func is None: load_data_func = load_data_from_repetitions

    if repetition_directory_template is None: repetition_directory_template = exputils.REPETITION_DIRECTORY_TEMPLATE
    repetition_directory_template = re.sub('\{.*\}', '*', repetition_directory_template)

    if statistics_directory is None: statistics_directory = exputils.DEFAULT_DATA_DIRECTORY

    def get_data(data, experiment_folder):
        '''Loads the data if the data is not already loaded'''
        if data is None:
            data = load_data_func(experiment_folder)
        return data

    # identify the experiment folders, i.e. folders that have repetition folders as subfolders
    experiment_directories = dict()
    for folder in experiments:

        # make sure the folder has folder form, i.e. with final '/'
        # then take the base directory and search in it
        # this makes sure, that also the direct given folder is looked after, e.g. './experiment_000001' would also be identified
        basedir = os.path.dirname(os.path.join(folder, ''))
        
        # look if there are repetition folders somewhere inside the directory
        for repetition_directory in glob.iglob(os.path.join(basedir,'**', repetition_directory_template), recursive=True):
            if os.path.isdir(repetition_directory):
                # remember the parent folder, i.e. the experiment folder
                experiment_directory = os.path.dirname(repetition_directory)
                
                if experiment_directory not in experiment_directories:
                    experiment_directories[experiment_directory] = set()

                experiment_directories[experiment_directory].add(repetition_directory)

    # calc statistic if it does not exist already
    for experiment_directory, repetition_directories in experiment_directories.items():

        data = None

        trg_directory = os.path.join(experiment_directory, statistics_directory)
        exputils.io.makedirs(trg_directory)

        if verbose:
            print('Calculate statistics for {!r}:'.format(experiment_directory))

        for statistic_name, statistic_func in statistics:

            # calculate statistics if they do not exist
            filename_npy = '{}.npy'.format(statistic_name)
            filename_npz = '{}.npz'.format(statistic_name)

            filepath_npy = os.path.join(trg_directory, filename_npy)
            filepath_npz = os.path.join(trg_directory, filename_npz)
            if (not os.path.isfile(filepath_npy) and not os.path.isfile(filepath_npz)) or recalculate_statistics:

                if verbose:
                    print('\t{} ...'.format(statistic_name))

                data = get_data(data, repetition_directories)

                stat = statistic_func(statistic_name, data)

                if isinstance(stat, dict):
                    np.savez(filepath_npz, **stat)
                else:
                    np.save(filepath_npy, stat)


def load_data_from_repetitions(repetition_directories, data_subdirectory=None):
    '''Loads the data from all subdirectories of the given repetition directories.'''

    # use default logs directory to define where the data is
    if data_subdirectory is None: data_subdirectory = exputils.DEFAULT_DATA_DIRECTORY

    # collect data from each repetition
    data = dict()
    for repetition_directory in sorted(repetition_directories):

        # get id of the repetition from its foldername
        numbers_in_string = [int(s) for s in os.path.basename(repetition_directory).split('_') if s.isdigit()]
        repetition_id = numbers_in_string[0]

        data[repetition_id] = exputils.io.load_numpy_files(os.path.join(repetition_directory, data_subdirectory))

    return data


# def collect_1D_values(name, data):
#
#     # gather information about number of repetitions and the max data length
#     n_reps = -1
#     max_data_length = -np.inf
#     for rep_id, rep_data in data.items():
#         n_reps = max(n_reps, rep_id)
#         max_data_length = max(max_data_length, rep_data[name].shape[0])
#     n_reps += 1
#
#     # collect data from all repetitions
#     collected_data = np.full((n_reps, max_data_length), np.nan)
#     for rep_id, rep_data in data.items():
#         collected_data[rep_id, :] = rep_data[name]
#
#     # save data
#     stats = dict()
#     stats['data'] = collected_data
#     stats['means'] = np.nanmean(collected_data, axis=0)
#     stats['stds'] = np.nanstd(collected_data, axis=0)
#     stats['n_repetitions'] = len(data)
#     stats['tags'] = ['repetitions']
#
#     return stats
#
#
# def collect_counters(name, data):
#
#     # check if the counter is the same for each repetition
#     # if yes, just save it once,
#     is_same_counter = True
#
#     counters = None
#     n_reps = -1
#     max_data_length = -np.inf
#     for rep_id, rep_data in data.items():
#         n_reps = max(n_reps, rep_id)
#         max_data_length = max(max_data_length, rep_data[name].shape[0])
#
#         if counters is None:
#             counters = rep_data[name]
#
#         elif not np.array_equal(counters, rep_data[name]):
#             is_same_counter = False
#
#     n_reps += 1
#
#     # if no, save it for each episode using np.nan to fill non
#     if not is_same_counter:
#         counters = np.full((n_reps, max_data_length), np.nan)
#         for rep_id, rep_data in data.items():
#             counters[rep_id, :] = rep_data[name]
#
#     return counters