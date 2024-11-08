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
from exputils.misc.attrdict import AttrDict
from typing import Optional
from types import ModuleType


# TODO: Feature - allow to load data from several campaigns

def load_experiment_descriptions(experiments_directory: Optional[str] = None,
                                 allowed_experiments_id_list: Optional[list] = None,
                                 denied_experiments_id_list: Optional[list] = None,
                                 experiment_directory_template: Optional[str] = None,
                                 repetition_directory_template: Optional[str] = None) -> AttrDict:
    """
    Loads and returns descriptions of experiments from a specified experiments directory.

    Arguments:
        experiments_directory (str): Path to the experiments directory.
            Defaults to "..\DEFAULT_EXPERIMENTS_DIRECTORY".
        allowed_experiments_id_list (list): List of experiment IDs to be loaded.
            Cannot be used with denied_experiments_id_list.
            Default: All experiments are considered.
        denied_experiments_id_list (list): List of experiment IDs to be excluded.
            Cannot be used with allowed_experiments_id_list.
            Default: All experiments are considered.
        experiment_directory_template (str): Template string for the name of experiment directories.
            The template should include a placeholder for the experiment id.
            Example: 'experiment_{:06d}' for experiment folders with ids with at least six digits.
            Defaults to EXPERIMENT_DIRECTORY_TEMPLATE.
        repetition_directory_template (str): Template string for the name of experiment directories.
            The template should include a placeholder for the repetition id.
            Example: 'repetition_{:06d}' for repetition folders with ids with at least six digits.
            Defaults to REPETITION_DIRECTORY_TEMPLATE.

    Returns:
        AttrDict: A dictionary containing descriptions of the experiments.
        The keys are the experiment ids and the values are dictionaries with the follwing properties:

            - id: experiment id.
            - name: Name of the experiment. Default: 'exp <experiment id\>'.
            - short_name: A short name for display purposes. Default: 'e<experiment id\>'.
            - order: Sort order of experiments if they should be displayed in a GUI.
            - directory: Full path to experiment directory.
            - description: Description of the experiment. Default: ''.
            - repetition_ids: List of repetition ids.
            - repetition_directories : List of full paths to repetition directories.
    """

    if experiments_directory is None:
        experiments_directory = os.path.join('..', eu.DEFAULT_EXPERIMENTS_DIRECTORY)

    if allowed_experiments_id_list is not None and denied_experiments_id_list is not None:
        raise ValueError('allowed_experiments_id_list and denied_experiments_id_list can not be set at the same time!')

    if experiment_directory_template is None: experiment_directory_template = eu.EXPERIMENT_DIRECTORY_TEMPLATE
    experiment_directory_template = re.sub('\{.*\}', '*', experiment_directory_template)

    if repetition_directory_template is None: repetition_directory_template = eu.REPETITION_DIRECTORY_TEMPLATE
    repetition_directory_template = re.sub('\{.*\}', '*', repetition_directory_template)

    experiment_descriptions = AttrDict()

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
            experiment_descr = AttrDict()
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


def load_experiment_data(experiment_descriptions: Optional[AttrDict]=None,
                         experiments_directory: Optional[str]=None,
                         allowed_experiments_id_list: Optional[list]=None,
                         denied_experiments_id_list: Optional[list]=None,
                         data_directory: Optional[str]=None,
                         is_load_repetition_data: bool=True,
                         pre_allowed_data_filter: Optional[list]=None,
                         pre_denied_data_filter: Optional[list]=None,
                         post_allowed_data_filter: Optional[list]=None,
                         post_denied_data_filter: Optional[list]=None,
                         on_experiment_data_loaded: Optional[list]=None,
                         on_repetition_data_loaded: Optional[list]=None,
                         allow_pickle: bool = True) -> tuple[AttrDict, AttrDict]:
    """
    Loads logged data from experiments and their repetitions in form of nested dictionaries and numpy arrays.

    [//]: # (TODO: give an example of a file structure and how it is loaded)

    Parameters:
        experiment_descriptions (AttrDict):
            Predefined descriptions of the experiments.
            The descriptions contain the paths to all experiments and their repetitions that should be loaded.
            See [`load_experiment_descriptions`][exputils.data.loading.load_experiment_descriptions] for details.
            Can not be set together with experiments_directory.
        experiments_directory (str):
            Path to the experiments directory.
            Defaults to `'..\experiments'`.
            Can not be set together with experiment_descriptions.
        allowed_experiments_id_list (list):
            List of allowed experiment IDs.
            Only these will be loaded.
            Can not be set together with denied_experiments_id_list.
        denied_experiments_id_list (list):
            List of denied experiment IDs.
            All experiments besides these will be loaded.
            Can not be set together with allowed_experiments_id_list.
        data_directory (str):
            Relative path of the data directories under the experiments and repetitions.
            Defaults to `'./data'`.
        is_load_repetition_data (bool):
            Flag to indicate if repetition data should be loaded.
            Defaults to `True`.
        pre_allowed_data_filter (list):
            List of datasources that will be loaded before the loading callback functions
            (see `on_experiment_data_loaded` and `on_repetition_data_loaded`) are called.
            Thus this data will be given to the callback functions.
            If defined then only these datasources will be loaded.
            The list contains strings with names of datasources.
        pre_denied_data_filter (list):
            List of datasources that will NOT be loaded before the loading callback functions
            (see `on_experiment_data_loaded` and `on_repetition_data_loaded`) are called.
            Thus this data will NOT be given to the callback functions.
            If defined then all existing datasources besides the ones specified will be loaded.
            The list contains strings with names of datasources.
        post_allowed_data_filter (list):
            List of datasources that will be added to the data dictionary that is returned after
            loading and the loading callback functions (see `on_experiment_data_loaded` and `on_repetition_data_loaded`)
            are called.
            If defined then only these datasources will be returned.
            The list contains strings with names of datasources.
        post_denied_data_filter (list):
            List of datasources that will NOT be added to the data dictionary that is returned after
            loading and the loading callback functions (see `on_experiment_data_loaded` and `on_repetition_data_loaded`)
            are called.
            If defined then all existing datasources besides the ones specified will be returned.
            The list contains strings with names of datasources.
        on_experiment_data_loaded (list):
            List of callback functions executed when experiment data is loaded.
            Can be used to modify the data by changing or adding elements.
            Form of the functions: func(exp_id: int, exp_data: AttrDict) -> AttrDict.
        on_repetition_data_loaded (list):
            List of callback functions executed when repetition data is loaded.
            Can be used to modify the data by changing or adding elements.
            Form of the functions: func(exp_id: int, exp_data: AttrDict) -> AttrDict.
        allow_pickle (bool):
            Indicates if loading of pickled objects is allowed.
            Defaults to True. <br>
            :warning: This could allow arbitrary code execution. Only load files you trust!

    Returns:
        data (AttrDict):
            Loaded data.
        experiment_descriptions (AttrDict):
            Experiment descriptions of the loaded data.
            See [`load_experiment_descriptions`][exputils.data.loading.load_experiment_descriptions] for details.
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
                    denied_data_filter=pre_denied_data_filter,
                    allow_pickle=allow_pickle)

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
                                denied_data_filter=pre_denied_data_filter,
                                allow_pickle=allow_pickle)

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
                            data[exp_id] = AttrDict()

                        data[exp_id][eu.REPETITION_DATA_KEY] = cur_rep_statistics_dict

    return data, experiment_descriptions


def load_single_experiment_data(experiment_directory: str,
                                data_directory: Optional[str] = None,
                                allowed_data_filter: Optional[list] = None,
                                denied_data_filter: Optional[list] = None,
                                allow_pickle: bool = True) -> AttrDict:
    """
    Loads data for a single experiment which includes all its repetition data.

    Parameters:
        experiment_directory (str):
            Path to the experiment directory.
        data_directory (str):
            Relative path of the data directories under the experiments and repetitions.
            Defaults to `'./data'`.
        allowed_data_filter (list):
            List of datasource names (strings) that will be loaded.
            If defined then only these datasources will be loaded.
        denied_data_filter (list):
            List of datasource names (strings) that will NOT be loaded.
            If defined then all datasources besides the specified ones will be loaded.
        allow_pickle (bool):
            Indicates if loading of pickled objects is allowed.
            Defaults to True. <br>
            :warning: This could allow arbitrary code execution. Only load files you trust!

    Returns:
        data (AttrDict):
            A dictionary containing the loaded data.
    """

    if data_directory is None:
        data_directory = eu.DEFAULT_DATA_DIRECTORY

    # need to allow also logging to be able to load data that is in logging.npz files
    if allowed_data_filter is not None:
        allowed_data_filter.append('logging')

    data = eu.io.load_numpy_files(
        os.path.join(experiment_directory, data_directory),
        allowed_data_filter=allowed_data_filter,
        denied_data_filter=denied_data_filter,
        allow_pickle=allow_pickle)

    # TODO: Refactor - make loading of npz files without the 'logging' sub-directory as a general cases
    if 'logging' in data:
        data.update(data['logging'])
        del data['logging']

    return data


def _filter_data(data, allowed_data_list, denied_data_list):
    # get the data_elements that should be deleted
    delete_keys = [k for k in data.keys() if not eu.misc.is_allowed(k, allowed_list=allowed_data_list, denied_list=denied_data_list)]
    for delete_key in delete_keys:
        del data[delete_key]


def load_experiment_data_single_object(name: str,
                                       experiment_id: Optional[int] = None,
                                       repetition_id: Optional[int] = None,
                                       experiments_directory: Optional[str] = None,
                                       data_directory: Optional[str] = None,
                                       experiment_directory_template: Optional[str] = None,
                                       repetition_directory_template: Optional[str] = None,
                                       add_execution_directory_to_sys_path: bool = True) -> object:
    """
    Loads single object that was logged via the [add_single_object][exputils.data.logging.add_single_object].
    function and saved as a dill file. The file that is either located under the experiments, or a
    single experiment or repetition directory.

    :warning: This could allow arbitrary code execution. Only load files you trust!

    Example:
        ```python
        loaded_obj = load_experiment_data_single_object(
            'my_object',  # name of the object
            experiment_id=100,
            repetition_id=1
        )
        print(loaded_obj)
        ```

    Parameters:
        name (str):
            The name of the object which is the name of the dill file with or without extension.
        experiment_id (int):
            An optional identifier for a specific experiment.
            If not provided, then the object is loaded from the experiments directory.
        repetition_id (int):
            An optional identifier for a specific repetition of the experiment.
            If not provided, then the object is loaded from the experiments or experiment directory.
        experiments_directory (str):
            The root directory where all experiments are stored.
            Defaults to `..\experiments`.
        data_directory (str):
            Relative path of the data directories under the experiments and repetitions.
            Defaults to `'./data'`.
        experiment_directory_template (str):
            Name template of experiment directories.
            Defaults to `'experiment_{:06d}'`.
        repetition_directory_template (str): Template for constructing the repetition directory. Defaults to None.
            Name template of repetition directories.
            Defaults to `'repetition_{:06d}'`.
        add_execution_directory_to_sys_path (bool):
            Whether to add the execution directory to the system path temporailly while loading the object.
            This can be necessary if the object has relational import statements.
            By adding the directory where the object is located temporailly to the python path,
            these import statments can be processed correctly.
            Defaults to True.

    Returns:
        object: The loaded experiment data object.
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


def load_experiment_python_module(module_path: str,
                                  experiment_id: Optional[int] = None,
                                  repetition_id: Optional[int] = None,
                                  experiments_directory: Optional[str] = None,
                                  exec_module: bool = True,
                                  experiment_directory_template: Optional[str] = None,
                                  repetition_directory_template: Optional[str] = None,
                                  add_execution_directory_to_sys_path: bool = True) -> ModuleType:
    """
    Loads a Python module dynamically that is either located under the experiments, or a single
    experiment or repetition directory.
    This can be used to load for example the configuration file of a repetition.

    Example:
        ```python
        # load the configuration file of a repetition and print its config dictionary
        config_module = load_experiment_python_module(
            'repetition_config.py',  # name of the configuration file
            experiment_id=100,
            repetition_id=3
        )
        print(config_module.config)
        ```

    :warning: This could allow arbitrary code execution. Only load files you trust!

    Parameters:
        module_path (str):
            The realtive path to the python module file either under the experiments, experiment, or
            repetition directory.
            Which level depends on if an experiment_id and a repetition_id are provided or not.
        experiment_id (int):
            An optional identifier for a specific experiment.
            If not provided, then the module is loaded from the experiments directory.
        repetition_id (int):
            An optional identifier for a specific repetition of the experiment.
            If not provided, then the module is loaded from the experiments or experiment directory.
        experiments_directory (str):
            The root directory where all experiments are stored.
            Defaults to `..\experiments`.
        exec_module (bool):
            If True, the module will be executed after being loaded which means it will be imported.
            Defaults to True.
        experiment_directory_template (str):
            Name template of experiment directories.
            Defaults to `'experiment_{:06d}'`.
        repetition_directory_template (str): Template for constructing the repetition directory. Defaults to None.
            Name template of repetition directories.
            Defaults to `'repetition_{:06d}'`.
        add_execution_directory_to_sys_path (bool):
            If True, the script's execution directory will be added to sys.path.
            Defaults to True.

    Returns:
        module (ModuleType): The loaded Python module object.

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
