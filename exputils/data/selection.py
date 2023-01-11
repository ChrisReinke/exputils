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
import warnings
import numpy as np

# TODO: Feature - output_formats
# TODO: Feature - data_filter
# TODO: Feature - data_filter_inds

def select_experiment_data(experiment_data, datasources, experiment_ids='all', repetition_ids='all', output_format=('S', 'E', 'D'), data_filter=None, data_filter_inds=None, experiment_descriptions=None, config=None, **kwargs):
    '''
    Collects the data for specific datasources, experiments and repetitions from the experiment data dictionary.
    The output format of the collected data can be chosen.
    Also allows to filter data.


    Output format: 'S' - datasource, 'E' - experiment, 'D' - repetition/data

    Default: ('S','E','D')

    :param datasources: String or list of strings with specification of the data sources from which the data should be collected.
    :param experiment_ids: Experiment id, List of experiment ids, or 'all'. (Default: 'all')
    :param repetition_ids: Repetition id, List of repetition ids, or 'all', or 'none'. (Default: 'all')
                           'none' means that the data is not over repetitions.
    '''

    S, E, D = 'S', 'E', 'D'

    default_config = eu.AttrDict(
        datasource_label='<datasource>', # either string with template for all data sources or a list with a string for each label
        experiment_label='<name>',
        repetition_label='<short_name> - <repetition_id>',
    )
    config = eu.combine_dicts(kwargs, config, default_config)

    if not experiment_data:
        return []

    # handle input parameters

    # get data sources as a list
    if not isinstance(datasources, list):
        datasources = [datasources]

    if not isinstance(config.datasource_label, list):
        config.datasource_label = [config.datasource_label] * len(datasources)

    # get experiment_ids as a list of ids
    if experiment_ids is None:
        experiment_ids = ['all']
    elif not isinstance(experiment_ids, list):
        experiment_ids = [experiment_ids]
    if experiment_ids == ['all']:
        experiment_ids = list(experiment_data.keys())

    # get repetition_ids as a list of ids or a slice over all repetitions
    if repetition_ids is None:
        repetition_ids = ['none']
    elif not isinstance(repetition_ids, list):
        repetition_ids = [repetition_ids]


    # if data_filter is not None and data_filter:
    #     # go over all experiments and apply the filter to each of them individually
    #     experiment_filter_inds = dict()
    #
    #     for exp_id in experiment_ids:
    #
    #     # filter data according data_filter the given filter
    #         data_filter_inds = filter_single_experiment_data(rep_data, data_filter)
    #
    #         experiment_filter_inds[exp_id] = ...


    # collect the data for each datasource and experiment
    collected_data = []
    data_labels = []
    for datasource_idx, datasource in enumerate(datasources):

        is_transpose = False
        if datasource.endswith('\''):
            datasource = datasource[:-1]
            is_transpose = True

        # identify the type of data
        # 3 types exist:
        #   - exp_data: data directly for an experiment, does not contain single dataitems for repetitions
        #   - rep_data: data for each repetition
        #   - exp_rep_data: data under the experiment, that whos first data dimension is over repetitions
        if datasource.startswith('exp.'):
            if repetition_ids == 'none':
                data_type = 'exp_data'
            else:
                data_type = 'exp_rep_data'
        elif datasource.startswith('rep.'):
            data_type = 'rep_data'
        else:
            # check datatype automatically
            # first check if the data is in experiment data
            try:
                # try if the data can be loaded from the experiment data (check for first experiment)
                eu.misc.get_dict_variable(experiment_data[experiment_ids[0]], datasource)
                # yes --> experiment data
                if repetition_ids == ['none']:
                    data_type = 'exp_data'
                else:
                    data_type = 'exp_rep_data'

            except (KeyError, IndexError):
                # could not find datasource under experiment_data, thus assume it is under repetition_data
                data_type = 'rep_data'

        if data_type in ['rep_data', 'exp_rep_data'] and repetition_ids == ['none']:
            raise ValueError('Data for datasource {!r} is assumed to be of data_type {!r}. In this case it is not possible that repetition_ids are \'none\'!'.format(datasource, data_type))

        cur_experiments_data = []
        cur_experiments_labels = []

        for experiment_id in experiment_ids:

            rep_ids = []

            # check if the data exisits
            if experiment_id not in experiment_data:
                warnings.warn('Data {!r} for experiment {!r} does not exist! Data is set to None.'.format(datasource,
                                                                                                          experiment_id))
                cur_data = None
            else:

                if data_type == 'exp_data':
                    rep_ids = []
                    try:
                        cur_data = eu.misc.get_dict_variable(experiment_data[experiment_id], datasource)
                    except (KeyError, IndexError):
                        # data does not exists
                        warnings.warn('Data {!r} for experiment {!r} does not exist! Data is set to None.'.format(datasource,
                                                                                                                  experiment_id))
                        cur_data = None


                elif data_type == 'exp_rep_data':

                    # if all repetition ids should be taken, then use a slice operator
                    rep_ids = repetition_ids.copy()
                    if rep_ids == ['all']:
                        rep_ids = slice(None)

                    try:
                        cur_data = eu.misc.get_dict_variable(experiment_data[experiment_id], datasource)
                        cur_data = cur_data[rep_ids]
                    except (KeyError, IndexError):
                        # data does not exists
                        warnings.warn('Data {!r} for experiment {!r} does not exist! Data is set to None.'.format(datasource,
                                                                                                                  experiment_id))
                        cur_data = None

                elif data_type == 'rep_data':

                    # how to store the data depends on the datatype:
                    #   scalar --> 1D numpy array
                    #   nD numpy array --> (n+1)D numpy array with first dimension over repetitions
                    #   other object --> list

                    cur_repetition_data = experiment_data[experiment_id]['repetition_data']

                    rep_ids = repetition_ids.copy()
                    if rep_ids == ['all']:
                        n_loaded_repetitions = len(cur_repetition_data)
                        rep_ids = list(range(n_loaded_repetitions))

                    # go over each repetition and store data in a list
                    cur_data_per_rep = []
                    is_numpy_array_type = True
                    final_np_array_shape = []
                    is_data_exist_inds = []
                    for rep_id in rep_ids:

                        try:
                            cur_rep_data = eu.misc.get_dict_variable(cur_repetition_data[rep_id], datasource)
                            is_data_exist_inds.append(True)
                        except (KeyError, IndexError):
                            # data does not exists in this repetition
                            warnings.warn('Data {!r} for repetition {!r} of experiment {!r} does not exist.'.format(datasource, rep_id, experiment_id))
                            cur_rep_data = None
                            is_data_exist_inds.append(False)

                        cur_data_per_rep.append(cur_rep_data)

                        # detetct if the data can be put into an numpy array,
                        # and detect the maximum shape of the array
                        if is_numpy_array_type and is_data_exist_inds[-1]:

                            cur_np_array_shape = None
                            if np.isscalar(cur_rep_data):
                                cur_np_array_shape = [1]
                            elif isinstance(cur_rep_data, np.ndarray):
                                cur_np_array_shape = cur_rep_data.shape
                            else:
                                is_numpy_array_type = False

                            if cur_np_array_shape is not None:
                                # check if all data have same number of dimensions
                                if not final_np_array_shape:
                                    final_np_array_shape = cur_np_array_shape
                                elif len(final_np_array_shape) == len(cur_np_array_shape):
                                    final_np_array_shape = np.maximum(final_np_array_shape, cur_np_array_shape)
                                else:
                                    is_numpy_array_type = False

                    if is_numpy_array_type:
                        # if the data can be transformed into a numpy array
                        if len(final_np_array_shape) == 1 and final_np_array_shape[0] == 1:
                            # if the data per repetition is only a scalar, then do not create
                            # create an extra dimensions for it, this replicates the default beahvior of numpy
                            data_shape = [len(cur_data_per_rep)]
                        else:
                            data_shape = [len(cur_data_per_rep)] + list(final_np_array_shape)

                        cur_data = np.full(data_shape, np.nan)
                        for rep_idx, rep_data in enumerate(cur_data_per_rep):

                            # only set values if data exisited for the repetition
                            if is_data_exist_inds[rep_idx]:

                                # create the correct slicing to add the rep_data into the whole array
                                rep_data_shape = np.shape(rep_data)
                                if len(data_shape) == 1:
                                    slices = rep_idx
                                else:
                                    slices = tuple([rep_idx] + [slice(0, d) for d in rep_data_shape])

                                cur_data[slices] = rep_data
                    else:
                        # otherwise keep data in list form over repetitions
                        cur_data = cur_data_per_rep

                    # set data to None if no repetition had some data
                    if not np.any(is_data_exist_inds):
                        cur_data = None

            if is_transpose:
                cur_data = np.transpose(cur_data)

            cur_experiments_data.append(cur_data)

            # create label string for the experiment
            exp_str_replace_dict = {'experiment_id': experiment_id,
                                    'datasource': datasource}
            if experiment_descriptions is not None:
                exp_str_replace_dict['name'] = experiment_descriptions[experiment_id]['name']
                exp_str_replace_dict['short_name'] = experiment_descriptions[experiment_id]['short_name']
                exp_str_replace_dict['description'] = experiment_descriptions[experiment_id]['description']
                exp_str_replace_dict['directory'] = experiment_descriptions[experiment_id]['directory']

            experiment_label = eu.misc.replace_str_from_dict(
                config.experiment_label,
                exp_str_replace_dict,
                pattern_format='<{}>')

            # create label strings for each repetition
            repetition_labels = []
            if rep_ids:
                rep_str_replace_dict = {'experiment_id': experiment_id,
                                        'datasource': datasource}
                if experiment_descriptions is not None:
                    rep_str_replace_dict['name'] = experiment_descriptions[experiment_id]['name']
                    rep_str_replace_dict['short_name'] = experiment_descriptions[experiment_id]['short_name']
                    rep_str_replace_dict['description'] = experiment_descriptions[experiment_id]['description']
                    rep_str_replace_dict['directory'] = experiment_descriptions[experiment_id]['directory']

                if isinstance(rep_ids, slice):
                    # assume it is a slice(None), i.e. a slice over all possible repetitions
                    # then create ids
                    rep_ids = list(range(len(cur_data)))

                for rep_id in rep_ids:
                    rep_str_replace_dict['repetition_id'] = rep_id
                    repetition_label = eu.misc.replace_str_from_dict(
                        config.repetition_label,
                        rep_str_replace_dict,
                        pattern_format='<{}>')
                    repetition_labels.append(repetition_label)

            if repetition_labels:
                cur_experiments_labels.append((experiment_label, repetition_labels))
            else:
                cur_experiments_labels.append(experiment_label)

        collected_data.append(cur_experiments_data)

        # define the data source label
        datasource_label = eu.misc.replace_str_from_dict(
            config.datasource_label[datasource_idx],
            {'<datasource>': datasource})
        data_labels.append((datasource_label, cur_experiments_labels))


    # reformat the data according to the given data format
    if output_format != (S, E, D):
        raise NotImplementedError('Output format {!r} is not supported!'.format(output_format))
        #
        # reformated_data = []
        #
        # cur_level_data = []
        # for cur_data_level_format in output_format:
        #
        #     # just encapsulating list of 1 is given
        #     if cur_data_level_format == 1:
        #         cur_level_data.append([])
        #     else:
        #         pass


    return collected_data, data_labels

#
# def recursive_reformat_data(collected_data, output_format, SED_indexes=None):
#
#     if SED_indexes is None:
#         SED_indexes = [None, None, None] # [data source, experiment, repetition]
#
#     # if last level, then create a numpy array
#
#     def get_data_object_combinations(cur_level_format, SED_indexes):
#         S, E, D = 'S', 'E', 'D'
#         S_loc, E_loc, D_loc = 0, 1, 2
#
#         # does the current data level has a parent or not
#         # if yes, then take all possibilities
#         # if no, then just take the exisiting possibilities under the parent
#
#         # return list of tuples with DER
#
#         # if parent is a datasource, then
#
#         # identify the current combinations:
#         data_type_combinations = get_cur_level_format_combinations(cur_level_format) # 'ExD' --> ['E', 'D']
#
#         for data_type in data_type_combinations:
#
#             if data_type == S:
#
#                 if SED_indexes[S_loc] is not None:
#                     raise ValueError('Each data type can only used once! \'S\' was used several times.')
#
#                 if SED_indexes[E_loc] is None and SED_indexes[D_loc] is None:
#                     # get all data sources
#                      data_object_combinations = np.arange(len(collected_data))
#
#                 else:
#
#                     data_object_combinations = []
#
#                     if SED_indexes[E_loc] is not None:
#                         # look if the given experiment has data for the datasource
#                         for ds_idx in range(len(collected_data)):
#                             if __name__ == '__main__':
#                                 if collected_data[ds_idx][SED_indexes[E_loc]] ..
#
#
#                 pass
#             elif data_type == E:
#                 pass
#             elif data_type == D:
#                 pass
#             else:
#                 raise ValueError('Unknown data type')
#
#
#         return data_object_combinations
#
#
#
#
#
#     cur_level_format = output_format[0]
#
#     # just encapsulating list if 1 is given
#     if cur_level_format == 1:
#
#         if len(output_format) <= 1:
#             raise ValueError('Final element in output format can not be \'1\'!')
#
#         cur_data = recursive_reformat_data(collected_data,
#                                            output_format[1:],
#                                            SED_indexes)
#         reformated_data = [cur_data]
#
#     else:
#         # otherwise, identify which data should be represented by this level
#
#         data_object_combinations = get_data_object_combinations(cur_level_format, SED_indexes)
#
#         if len(output_format) > 1:
#             # check if last element is a slice over repetitions,
#             # if yes, then just grap them easily
#             reformated_data = np.array([])
#         else:
#             reformated_data = []
#
#         # go through the list data objects that are specified for this level
#         # could be data sources, experiments, repetitions or combinations of these
#         for data_object_combination in data_object_combinations:
#
#             # fill out the DER_indexes according to the given combinations:
#             if data_object_combination[0] is not None: SED_indexes[0] = data_object_combination[0]
#             if data_object_combination[1] is not None: SED_indexes[1] = data_object_combination[1]
#             if data_object_combination[2] is not None: SED_indexes[2] = data_object_combination[2]
#
#             if len(output_format) <= 1:
#                 # final level, get the data
#
#                 if len(data_object_combination) > 1:
#                     raise AssertionError('For the final level the number of data_object_combinations must be 1!')
#
#                 reformated_data = collected_data[SED_indexes[0]][SED_indexes[1]][SED_indexes[2]]
#
#             else:
#                 # not the final level, go one level down
#                 cur_data = recursive_reformat_data(collected_data,
#                                                    output_format[1:],
#                                                    SED_indexes)
#                 reformated_data.append(cur_data)
#
#
#     return reformated_data
