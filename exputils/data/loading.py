import os
import exputils as eu
from glob import glob
import re
import numpy as np
import warnings
import collections

# TODO: Feature - allow to load data from several campaigns
# TODO: Feature - allow to define a black_list or white_list of data that should not be loaded

def load_experiment_descriptions(experiments_directory=None,
                                 experiment_directory_template=None,
                                 repetition_directory_template=None):

    if experiments_directory is None:
        experiments_directory = os.path.join('..', eu.DEFAULT_EXPERIMENTS_DIRECTORY)

    if experiment_directory_template is None: experiment_directory_template = eu.EXPERIMENT_DIRECTORY_TEMPLATE
    experiment_directory_template = re.sub('\{.*\}', '*', experiment_directory_template)

    if repetition_directory_template is None: repetition_directory_template = eu.REPETITION_DIRECTORY_TEMPLATE
    repetition_directory_template = re.sub('\{.*\}', '*', repetition_directory_template)

    experiment_descriptions = eu.AttrDict()

    exp_directories = glob(os.path.join(experiments_directory, experiment_directory_template))
    for order, exp_directory in enumerate(np.sort(exp_directories)):

        exp_id = re.findall(r'\d+', os.path.basename(exp_directory))[0]

        experiment_descr = eu.AttrDict()
        experiment_descr.id = exp_id
        experiment_descr.name = 'exp {}'.format(exp_id)
        experiment_descr.order = order
        experiment_descr.is_load_data = True
        experiment_descr.directory = exp_directory
        experiment_descr.short_name = 'e{}'.format(exp_id)
        experiment_descr.description = ''

        # find repetition ids
        experiment_descr.repetition_ids = []
        repetition_directories = glob(os.path.join(exp_directory, repetition_directory_template))
        for rep_directory in np.sort(repetition_directories):
            rep_id = re.findall(r'\d+', os.path.basename(rep_directory))[0]
            experiment_descr.repetition_ids.append(int(rep_id))
        experiment_descr.repetition_ids.sort()

        experiment_descriptions[exp_id] = experiment_descr

    return experiment_descriptions


def load_experiment_data(experiment_descriptions=None, data_directory=None, is_load_repetition_data=True):
    '''Loads the data for the given experiments descriptions. Ignores non-selected experiments.'''

    if experiment_descriptions is None:
        experiment_descriptions = load_experiment_descriptions()

    # load experiments according to the order in the experiment_descriptions
    sorted_experiment_ids = eu.data.get_ordered_experiment_ids_from_descriptions(experiment_descriptions)

    data = collections.OrderedDict()
    for exp_id in sorted_experiment_ids:
        exp_descr = experiment_descriptions[exp_id]

        if 'is_load_data' not in exp_descr or exp_descr['is_load_data']:
            try:
                data[exp_id] = load_single_experiment_data(exp_descr['directory'], data_directory)
            except FileNotFoundError:
                if not exp_descr.repetition_ids or not is_load_repetition_data:
                    warnings.warn('Could not load statistics for experiment {!r} ({!r}). Skipped ...'.format(exp_id, exp_descr['directory']))

            # load data of each repetition
            if is_load_repetition_data:
                if eu.REPETITION_DATA_KEY in data:
                    warnings.warn('A statistic called {!r} was loaded for experiment data. Can not store repetition data under the same data source name. Skip to load repetition data. Please rename this statistic.'.format(eu.REPETITION_DATA_KEY))
                else:
                    cur_rep_statistics_dict = dict()
                    for rep_id in exp_descr.repetition_ids:
                        cur_rep_directory = os.path.join(exp_descr['directory'], eu.REPETITION_DIRECTORY_TEMPLATE.format(rep_id))
                        try:
                            cur_rep_statistics_dict[rep_id] = load_single_experiment_data(cur_rep_directory, data_directory)
                        except FileNotFoundError:
                            warnings.warn('Could not load data for repetition {} of experiment {!r} ({!r}). Skipped ...'.format(rep_id, exp_id, exp_descr['directory']))

                    if cur_rep_statistics_dict:
                        # in case no experimental level data exists
                        if exp_id not in data:
                            data[exp_id] = eu.AttrDict()

                        data[exp_id][eu.REPETITION_DATA_KEY] = cur_rep_statistics_dict

    return data, experiment_descriptions


def load_single_experiment_data(experiment_directory, data_directory=None):
    '''Loads the data from a single experiment.'''

    if data_directory is None:
        data_directory = eu.DEFAULT_DATA_DIRECTORY

    statistics = eu.io.load_numpy_files(os.path.join(experiment_directory, data_directory))

    # TODO: Refactor - make loading of npz files without the 'logging' sub-direcotry as a general cases
    if len(statistics) == 1 and 'logging' in statistics:
        statistics = statistics['logging']

    return statistics