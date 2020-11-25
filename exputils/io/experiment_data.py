import exputils as eu
import warnings
import numpy as np

#TODO: think about naming scheme of functions
def get_repetitions_data(experiment_data, data_sources, experiment_ids='all', repetition_ids='all',
                                  output_format=('S','E','D'), experiment_descriptions=None, config=None, **kwargs):
    return get_experiment_data(experiment_data,
                               data_sources,
                               experiment_ids=experiment_ids,
                               repetition_ids=repetition_ids,
                               output_format=output_format,
                               experiment_descriptions=experiment_descriptions,
                               config=config,
                               **kwargs)


def get_non_repetitions_data(experiment_data, data_sources, experiment_ids='all',
                             output_format=('S','E','D'), experiment_descriptions=None, config=None, **kwargs):
    return get_experiment_data(experiment_data,
                               data_sources,
                               experiment_ids=experiment_ids,
                               repetition_ids='none',
                               output_format=output_format,
                               experiment_descriptions=experiment_descriptions,
                               config=config,
                               **kwargs)

# TODO: maybe call it select_experiment_data
def get_experiment_data(experiment_data, datasources, experiment_ids='all', repetition_ids='all', output_format=('S', 'E', 'D'), experiment_descriptions=None, config=None, **kwargs):
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

    # TODO: handle also data that has no repetitions, e.g. some statistics that were already computed over repetitions
    S, E, D = 'S', 'E', 'D'

    default_config = eu.AttrDict(
        datasource_label='<datasource>', # either string with template for all data sources or a list with a string for each label
        experiment_label='<name>',
        repetition_label='<id>',
    )
    config = eu.combine_dicts(kwargs, config, default_config)
    str_replace_pattern_format = '<{}>'

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
    if repetition_ids == ['all']:
        repetition_ids = slice(None)

    # collect the data for each datasource and experiment
    collected_data = []
    data_labels = []
    for datasource_idx, datasource in enumerate(datasources):
        cur_experiments_data = []
        cur_experiments_labels = []

        for experiment_id in experiment_ids:
            try:
                cur_data = eu.misc.get_dict_variable(experiment_data[experiment_id], datasource)

                if repetition_ids != ['none']:
                    cur_data = cur_data[repetition_ids]

            except (KeyError, IndexError):
                # data does not exists
                warnings.warn('Data {!r} for experiment {!r} does not exist!'.format(datasource, experiment_id))
                cur_data = None

            cur_experiments_data.append(cur_data)

            exp_str_replace_dict = {'id': experiment_id,
                                    'datasource': datasource}
            if experiment_descriptions is not None:
                exp_str_replace_dict['name'] = experiment_descriptions[experiment_id]['name']
                exp_str_replace_dict['short_name'] = experiment_descriptions[experiment_id]['short_name']
                exp_str_replace_dict['description'] = experiment_descriptions[experiment_id]['description']
                exp_str_replace_dict['directory'] = experiment_descriptions[experiment_id]['directory']

            experiment_label = eu.misc.replace_str_from_dict(
                config.experiment_label,
                exp_str_replace_dict,
                pattern_format=str_replace_pattern_format)

            cur_experiments_labels.append(experiment_label)

        collected_data.append(cur_experiments_data)

        # define the data source label
        datasource_label = eu.misc.replace_str_from_dict(
            config.datasource_label[datasource_idx],
            {'datasource': datasource},
            pattern_format=str_replace_pattern_format)
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
#                                     # TODO: check how the collected data looks like for such cases where an experiment has not the specified data source
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
