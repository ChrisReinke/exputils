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
import sys
import exputils as eu
from glob import glob
import re
import numpy as np
import warnings
import collections
import importlib.util

# TODO: Feature - allow to load data from several campaigns

def load_experiment_descriptions(experiments_directory=None,
                                 allowed_experiments_id_list=None,
                                 denied_experiments_id_list=None,
                                 experiment_directory_template=None,
                                 repetition_directory_template=None):

    if experiments_directory is None:
        experiments_directory = os.path.join('..', eu.DEFAULT_EXPERIMENTS_DIRECTORY)

    if allowed_experiments_id_list is not None and denied_experiments_id_list is not None:
        raise ValueError('allowed_experiments_id_list and denied_experiments_id_list can not be set at the same time!')

    if experiment_directory_template is None: experiment_directory_template = eu.EXPERIMENT_DIRECTORY_TEMPLATE
    experiment_directory_template = re.sub('\{.*\}', '*', experiment_directory_template)

    if repetition_directory_template is None: repetition_directory_template = eu.REPETITION_DIRECTORY_TEMPLATE
    repetition_directory_template = re.sub('\{.*\}', '*', repetition_directory_template)

    experiment_descriptions = eu.AttrDict()

    exp_directories = glob(os.path.join(experiments_directory, experiment_directory_template))
    for order, exp_directory in enumerate(np.sort(exp_directories)):

        try:
            exp_id = re.findall(r'\d+', os.path.basename(exp_directory))[0]
        except IndexError as err:
            raise ValueError('The experiments_directory (\'{}\') seems not to have experiment folders!'.format(experiments_directory)) from err

        is_add_experiment_descr = True
        if allowed_experiments_id_list is not None and exp_id not in allowed_experiments_id_list:
            is_add_experiment_descr = False
        elif denied_experiments_id_list is not None and exp_id in denied_experiments_id_list:
            is_add_experiment_descr = False

        if is_add_experiment_descr:
            experiment_descr = eu.AttrDict()
            experiment_descr.id = exp_id
            experiment_descr.name = 'exp {}'.format(exp_id)
            experiment_descr.order = order
            experiment_descr.is_load_data = True
            experiment_descr.directory = exp_directory
            experiment_descr.short_name = 'e{}'.format(exp_id)
            experiment_descr.description = ''

            # find repetition directories and ids
            repetition_directories = glob(os.path.join(exp_directory, repetition_directory_template))
            experiment_descr.repetition_directories = repetition_directories
            if experiment_descr.repetition_directories:
                experiment_descr.repetition_directories.sort()

            experiment_descr.repetition_ids = []
            for rep_directory in np.sort(repetition_directories):
                rep_id = re.findall(r'\d+', os.path.basename(rep_directory))[0]
                experiment_descr.repetition_ids.append(int(rep_id))
            experiment_descr.repetition_ids.sort()

            experiment_descriptions[exp_id] = experiment_descr

    return experiment_descriptions


def load_experiment_data(experiment_descriptions=None, experiments_directory=None, allowed_experiments_id_list=None, denied_experiments_id_list=None,
                         data_directory=None, is_load_repetition_data=True,
                         pre_allowed_data_filter=None, pre_denied_data_filter=None, post_allowed_data_filter=None, post_denied_data_filter=None,
                         on_experiment_data_loaded=None, on_repetition_data_loaded=None):
    """
    Loads experimental data from experiments and their repetitions.

    :param experiments_directory:  Path to the directory that contains the experiments. (default = './experiments')
    :param allowed_experiments_id_list: List of experiment ids that are only allowed to be loaded, not other will be loaded. (default = None)
    :param denied_experiments_id_list: List of experiment ids that will not be loaded, all other will. (default = None)
    :param experiment_descriptions: Descriptions about the experiments that should be loaded. If it contains a is_load_data property, then this
                                    is checked if the experiment should be loaded or not. (default = None)
    :param data_directory: Relative path of the data directories under the experiments and repetitions. (default = '/data')
    :param is_load_repetition_data: Should the data of repetitions be loaded. (default = True)
    :param pre_allowed_data_filter: List of data items that should only be loaded before the on_experiment_data_loaded and on_repetition_data_loaded
                                    functions are called. (default = None)
    :param pre_denied_data_filter: List of data items that should not be loaded before the on_experiment_data_loaded and on_repetition_data_loaded
                                   functions are called. (default = None)
    :param post_allowed_data_filter: List of data items that are only allowed after the on_experiment_data_loaded and on_repetition_data_loaded
                                     functions are called. (default = None)
    :param post_denied_data_filter: List of data items that are removed after the on_experiment_data_loaded and on_repetition_data_loaded
                                    functions are called. (default = None)
    :param on_experiment_data_loaded: List of functions that will be called after experiment data is loaded. (default = None)
                                      Form of the functions: func(experiment_id, experiment_data)
    :param on_repetition_data_loaded: List of functions that will be called after repetition data is loaded. (default = None)
                                      Form of the functions: func(experiment_id, repetition_id, repetition_data)
    :return: Data and experiment descriptions.

    """

    if experiments_directory is not None and experiment_descriptions is not None:
        raise ValueError('Can not set experiment_directory and experiment_descriptions at the same time!')

    if experiment_descriptions is not None and (allowed_experiments_id_list is not None or denied_experiments_id_list is not None):
        raise ValueError('experiment_descriptions and (allowed_experiments_id_list or denied_experiments_id_list) can not be set at the same time!')

    if allowed_experiments_id_list is not None and denied_experiments_id_list is not None:
        raise ValueError('allowed_experiments_id_list and denied_experiments_id_list can not be set at the same time!')

    if experiment_descriptions is None:
        experiment_descriptions = load_experiment_descriptions(
                experiments_directory=experiments_directory,
            allowed_experiments_id_list=allowed_experiments_id_list,
            denied_experiments_id_list=denied_experiments_id_list
        )
    else:
        experiment_descriptions = experiment_descriptions

    if on_experiment_data_loaded is None:
        on_experiment_data_loaded = []

    if on_repetition_data_loaded is None:
        on_repetition_data_loaded = []

    # load experiments according to the order in the experiment_descriptions
    sorted_experiment_ids = eu.data.get_ordered_experiment_ids_from_descriptions(experiment_descriptions)

    data = collections.OrderedDict()
    for exp_id in sorted_experiment_ids:
        exp_descr = experiment_descriptions[exp_id]

        if 'is_load_data' not in exp_descr or exp_descr['is_load_data']:
            try:
                data[exp_id] = load_single_experiment_data(
                    exp_descr['directory'],
                    data_directory=data_directory,
                    allowed_data_filter=pre_allowed_data_filter,
                    denied_data_filter=pre_denied_data_filter)

                for callback_function in on_experiment_data_loaded:
                    callback_function(exp_id, data[exp_id])

                _filter_data(data[exp_id], post_allowed_data_filter, post_denied_data_filter)

            except FileNotFoundError:
                if not exp_descr.repetition_ids or not is_load_repetition_data:
                    warnings.warn('Could find data for experiment {!r} ({!r}). Skipped ...'.format(exp_id, exp_descr['directory']))

            except Exception as e:
                raise Exception('Exception during loading of data for experiment {!r} ({!r})!'.format(exp_id, exp_descr['directory'])) from e

            # load data of each repetition
            if is_load_repetition_data:
                if eu.REPETITION_DATA_KEY in data:
                    warnings.warn('A statistic called {!r} was loaded for experiment data. Can not store repetition data under the same data source name. Skip to load repetition data. Please rename this statistic.'.format(eu.REPETITION_DATA_KEY))
                else:
                    cur_rep_statistics_dict = dict()
                    for rep_id in exp_descr.repetition_ids:
                        cur_rep_directory = os.path.join(exp_descr['directory'], eu.REPETITION_DIRECTORY_TEMPLATE.format(rep_id))
                        try:
                            cur_rep_statistics_dict[rep_id] = load_single_experiment_data(
                                cur_rep_directory,
                                data_directory=data_directory,
                                allowed_data_filter=pre_allowed_data_filter,
                                denied_data_filter=pre_denied_data_filter)

                            for callback_function in on_repetition_data_loaded:
                                callback_function(exp_id, rep_id, cur_rep_statistics_dict[rep_id])

                            _filter_data(cur_rep_statistics_dict[rep_id], post_allowed_data_filter, post_denied_data_filter)

                        except FileNotFoundError:
                            warnings.warn('Could not find data for repetition {} of experiment {!r} ({!r}). Skipped ...'.format(rep_id, exp_id, exp_descr['directory']))

                        except Exception as e:
                            raise Exception('Exception during loading of data for repetition {} of experiment {!r} ({!r})!'.format(rep_id, exp_id, exp_descr['directory'])) from e

                    if cur_rep_statistics_dict:
                        # in case no experimental level data exists
                        if exp_id not in data:
                            data[exp_id] = eu.AttrDict()

                        data[exp_id][eu.REPETITION_DATA_KEY] = cur_rep_statistics_dict

    return data, experiment_descriptions


def load_single_experiment_data(experiment_directory, data_directory=None, allowed_data_filter=None, denied_data_filter=None, allow_pickle=True):
    """Loads the data from a single experiment."""

    if data_directory is None:
        data_directory = eu.DEFAULT_DATA_DIRECTORY

    # need to allow also logging to be able to load data that is in logging.npz files
    if allowed_data_filter is not None:
        allowed_data_filter.append('logging')

    statistics = eu.io.load_numpy_files(
        os.path.join(experiment_directory, data_directory),
        allowed_data_filter=allowed_data_filter,
        denied_data_filter=denied_data_filter,
        allow_pickle=allow_pickle)

    # TODO: Refactor - make loading of npz files without the 'logging' sub-directory as a general cases
    if 'logging' in statistics:
        statistics.update(statistics['logging'])
        del statistics['logging']

    return statistics


def _filter_data(data, allowed_data_list, denied_data_list):
    # get the data_elements that should be deleted
    delete_keys = [k for k in data.keys() if not eu.misc.is_allowed(k, allowed_list=allowed_data_list, denied_list=denied_data_list)]
    for delete_key in delete_keys:
        del data[delete_key]


def load_experiment_python_module(module_path, experiment_id=None, repetition_id=None, experiments_directory=None, exec_module=True,
                                  experiment_directory_template=None, repetition_directory_template=None,
                                  add_execution_directory_to_sys_path=True):
    """
    Loads a python module that is under a certain repetition of an experiment. Can be used to load for example the configuration of a repetition.

    Example:
        module = load_experiment_python_module('repetition_config.py', experiment_id=100, repetition_id=3)

    :param module_path: Name of the python module (including the '.py' ending).
    :param experiment_id: ID of the experiment. If not provided, then the module is assumed to be under the experiments directory.
    :param repetition_id: ID of the repetition. If not provided, then the module is assumed to be under the experiment directory.
    :param experiments_directory: Path to the experiments directory. (Default = '../experiments')
    :param exec_module: True if the module should be executed. (Default = True)
    :param experiment_directory_template: Alternative template string for experiment directories. (Default = 'experiment_{}')
    :param repetition_directory_template: Alternative template string for repetition directories. (Default = 'repetition_{}')
    :param add_execution_directory_to_sys_path: Should the directory in which the code was executed (experiment or repetition) be temporaily added
                                                to the python system path. This might be necessary if the loaded object has references to it.
                                                (Default = True)
    :return: Loaded module.
    """

    if experiments_directory is None:
        experiments_directory = os.path.join('..', eu.DEFAULT_EXPERIMENTS_DIRECTORY)

    full_module_path = experiments_directory

    # only add experiment subfolder if needed
    if experiment_id is not None:

        if experiment_directory_template is None:
            experiment_directory_template = eu.EXPERIMENT_DIRECTORY_TEMPLATE

        experiment_directory = experiment_directory_template.format(experiment_id)

        full_module_path = os.path.join(full_module_path, experiment_directory)

        # only add repetition subfolder if needed
        if repetition_id is not None:

            if repetition_directory_template is None:
                repetition_directory_template = eu.REPETITION_DIRECTORY_TEMPLATE

            repetition_directory = repetition_directory_template.format(repetition_id)

            full_module_path = os.path.join(full_module_path, repetition_directory)

    # construct the full path to the module
    full_module_path = os.path.join(full_module_path, module_path)

    filename = os.path.basename(module_path)
    module_name = filename.replace('.py', '')

    spec = importlib.util.spec_from_file_location(module_name, full_module_path)

    # creates a new module based on spec
    module = importlib.util.module_from_spec(spec)

    if exec_module:
        # add the directory in which the code was executed to system path
        if add_execution_directory_to_sys_path:
            sys.path.append(os.path.dirname(full_module_path))

        spec.loader.exec_module(module)

        if add_execution_directory_to_sys_path:
            sys.path.pop()

    return module


def load_experiment_data_single_object(name, experiment_id=None, repetition_id=None, experiments_directory=None, data_directory=None,
                                       experiment_directory_template=None, repetition_directory_template=None,
                                       add_execution_directory_to_sys_path=True):
    """
    Loads a object (a dill file) that is saved in the data directory of an experiment or repetition. Such objects are saved using the
    log.add_single_object() function.geht es

    Example:
        log.add_single_object('my_object', obj)
        obj = load_experiment_data_single_object('my_object', experiment_id=100, repetition_id=3)

    :param name: Name of the object or the dill file (including the '.dill' ending is optional).
    :param experiment_id: ID of the experiment. If not provided, then the object is assumed to be under the experiments data directory.
    :param repetition_id: ID of the repetition. If not provided, then the object is assumed to be under the experiment data directory.
    :param experiments_directory: Path to the experiments directory. (Default = '../experiments')
    :param data_directory: Name of the data directory. (Default = 'data')
    :param experiment_directory_template: Alternative template string for experiment directories. (Default = 'experiment_{}')
    :param repetition_directory_template: Alternative template string for repetition directories. (Default = 'repetition_{}')
    :param add_execution_directory_to_sys_path: Should the directory in which the code was executed (experiment or repetition) be temporaily added
                                                to the python system path. This might be necessary if the loaded object has references to it.
                                                (Default = True)
    :return: Loaded objected.
    """


    if experiments_directory is None:
        experiments_directory = os.path.join('..', eu.DEFAULT_EXPERIMENTS_DIRECTORY)

    full_execution_dir_path = experiments_directory

    # only add experiment subfolder if needed
    if experiment_id is not None:

        if experiment_directory_template is None:
            experiment_directory_template = eu.EXPERIMENT_DIRECTORY_TEMPLATE

        experiment_directory = experiment_directory_template.format(experiment_id)

        full_execution_dir_path = os.path.join(full_execution_dir_path, experiment_directory)

        # only add repetition subfolder if needed
        if repetition_id is not None:

            if repetition_directory_template is None:
                repetition_directory_template = eu.REPETITION_DIRECTORY_TEMPLATE

            repetition_directory = repetition_directory_template.format(repetition_id)

            full_execution_dir_path = os.path.join(full_execution_dir_path, repetition_directory)

    if data_directory is None:
        data_directory = eu.DEFAULT_DATA_DIRECTORY

    # construct the full path to the module
    full_dill_path = os.path.join(full_execution_dir_path, data_directory, name)

    # add the directory in which the code was executed to system path
    if add_execution_directory_to_sys_path:
        sys.path.append(full_execution_dir_path)

    obj = eu.io.dill.load_dill(full_dill_path)

    if add_execution_directory_to_sys_path:
        sys.path.pop()

    return obj
