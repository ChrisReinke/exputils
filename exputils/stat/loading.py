import os
import exputils
from glob import glob
import re
import numpy as np

# TODO: allow to load data from several campaigns

def load_experiment_descriptions(experiments_directory=None,
                                 experiment_directory_template=None,
                                 repetition_directory_template=None):

    if experiments_directory is None:
        experiments_directory = os.path.join('..', exputils.DEFAULT_EXPERIMENTS_DIRECTORY)

    if experiment_directory_template is None: experiment_directory_template = exputils.EXPERIMENT_DIRECTORY_TEMPLATE
    experiment_directory_template = re.sub('\{.*\}', '*', experiment_directory_template)

    if repetition_directory_template is None: repetition_directory_template = exputils.REPETITION_DIRECTORY_TEMPLATE
    repetition_directory_template = re.sub('\{.*\}', '*', repetition_directory_template)

    experiment_descriptions = exputils.AttrDict()

    exp_directories = glob(os.path.join(experiments_directory, experiment_directory_template))
    for exp_directory in np.sort(exp_directories):

        exp_id = re.findall(r'\d+', os.path.basename(exp_directory))[0]

        experiment_descr = exputils.AttrDict()
        experiment_descr.id = exp_id
        experiment_descr.name = 'exp {}'.format(exp_id)
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

        experiment_descriptions[exp_id] = experiment_descr

    return experiment_descriptions


def load_experiment_statistics(experiment_descriptions=None, statistics_directory=None):
    '''Loads the statistics for the given experiments descriptions. Ignores non-selected experiments.'''

    if experiment_descriptions is None:
        experiment_descriptions = load_experiment_descriptions()

    statistics = dict()
    for exp_id, exp_descr in experiment_descriptions.items():
        if 'is_load_data' not in exp_descr or exp_descr['is_load_data']:
            statistics[exp_id] = load_single_experiment_statistics(exp_descr['directory'], statistics_directory)

    return statistics, experiment_descriptions


def load_single_experiment_statistics(experiment_directory, statistics_directory=None):
    '''Loads the statistics from a single experiment.'''

    if statistics_directory is None:
        statistics_directory = exputils.DEFAULT_STATISTICS_DIRECTORY

    statistics = exputils.io.load_numpy_files(os.path.join(experiment_directory, statistics_directory))

    return statistics