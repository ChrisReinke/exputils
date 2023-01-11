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
import numpy as np
import scipy.stats
from tabulate import tabulate as original_tabulate
import IPython


def is_needed_pairwise_combination(idx1, idx2, pairwise_mode):
    is_needed = True
    if 'not_identity' in pairwise_mode and idx1 == idx2:
        is_needed = False
    elif 'upper_triangle' in pairwise_mode and idx1 > idx2:
        is_needed = False
    elif 'lower_triangle' in pairwise_mode and idx1 < idx2:
        is_needed = False

    return is_needed


def tabulate_pairwise(data=None, config=None, **kwargs):
    """
    Plots a pairwise comparison between data from experiments based on a pairwise function d = f(exp_a, exp_b).

    :param data:
    :param config:
        tabulate: Parameters for the tabulate function that plots the table.
                  See https://pypi.org/project/tabulate/ for possible parameters.
                  Some important ones:

            tablefmt: Format of the table. (Default='html')
                        "plain", "simple", "github", "grid", "fancy_grid", "pipe", "orgtbl", "jira", "presto", "pretty",
                        "psql",  "rst", "mediawiki", "moinmoin", "youtrack", "html", "unsafehtml", "latex", "latex_raw",
                        "latex_booktabs", "latex_longtable", "textile", "tsv"

    :param kwargs:
    :return:
    """

    default_config = eu.AttrDict(

        pairwise_function = eu.misc.mannwhitneyu_pvalue,

        pairwise_mode = 'full',    # which pairs are compared? 'full', 'full_not_identity', 'upper_triangle', 'upper_triangle_not_identiy', 'lower_triangle', 'lower_triangle_not_identiy'

        tabulate=eu.AttrDict(
            tablefmt='html', #
            numalign='right',
        ),

        cell_format = '{}',

        top_left_cell_content = '',

        labels=[],  # holds all labels in a specific structure

    )
    config = eu.combine_dicts(kwargs, config, default_config)

    allowed_pairwise_modes = ['full', 'full_not_identity', 'upper_triangle', 'upper_triangle_not_identity', 'lower_triangle', 'lower_triangle_not_identity']
    if config.pairwise_mode not in allowed_pairwise_modes:
        raise ValueError('Unknown configuration {!r} for pairwise_mode! Allowed values: {}'.format(config.pairwise_mode, allowed_pairwise_modes))

    if data is None:
        data = np.array([])

    # format data in form [subplot_idx:list][trace_idx:list][elems_per_trace:numpy.ndarray]
    # subplot is a single table
    if isinstance(data, np.ndarray):
        data = [[data]]
    elif isinstance(data, list) and isinstance(data[0], np.ndarray):
        data = [data]
    elif not isinstance(data, list) and not isinstance(data[0], list) and not isinstance(data[0][0], np.ndarray):
        raise ValueError('Unsupported type of data!')

    # handle different input formats of labels
    if config.labels:
        # if only labels for mean-traces are given, then add an empty label for the sub figure
        if isinstance(config.labels, list) and not isinstance(config.labels[0], tuple):
            config.labels = [('', config.labels)]
        # if no labels are given for elements, then create an empty list for element labels
        for ds_idx in range(len(config.labels)):
            for trace_idx in range(len(config.labels[ds_idx][1])):
                if not isinstance(config.labels[ds_idx][1][trace_idx], tuple):
                    config.labels[ds_idx][1][trace_idx] = (config.labels[ds_idx][1][trace_idx], [])

    # identify the number of subplots
    n_subplots = len(data)

    if n_subplots > 1:
        raise NotImplementedError('Only supports 1 subplot!')

    # interate over subplots
    for subplot_idx, subplot_data in enumerate(data):

        trace_labels = []
        data_per_trace = []

        # collect the data and labels for each trace
        for trace_idx, cur_data in enumerate(subplot_data):

            # handle trace for mean values
            if config.labels:
                trace_label = config.labels[subplot_idx][1][trace_idx][0]
            else:
                trace_label = config.default_trace_label
                if len(config.trace_labels) > trace_idx:
                    trace_label = config.trace_labels[trace_idx]
            trace_label = eu.misc.replace_str_from_dict(str(trace_label), {'<trace_idx>': trace_idx})
            trace_labels.append(trace_label)

            data_points = np.array([])

            if np.ndim(cur_data) == 0:
                data_points = np.array([cur_data])
            elif np.ndim(cur_data) == 1:
                data_points = cur_data
            else:
                # collect data over elements
                for elem_idx, elem_data in enumerate(cur_data):  # data elements

                    # get element data which could be in matrix format or array format
                    if np.ndim(elem_data) == 0:
                        cur_elem_data = np.array([elem_data])
                    elif np.ndim(elem_data) == 1:
                        cur_elem_data = elem_data
                    elif np.ndim(elem_data) == 2:
                        if elem_data.shape[0] == 1:
                            cur_elem_data = elem_data[0, :]
                        elif elem_data.shape[1] == 1:
                            cur_elem_data = elem_data[1, 0]
                        else:
                            raise ValueError('Invalid data format!')
                    else:
                        raise ValueError('Invalid data format!')

                    data_points = np.hstack((data_points, cur_elem_data))

            data_per_trace.append(data_points)


        n_traces = len(data_per_trace)

        # compute the pairwise function of all needed combinations
        pairwise_data = np.full((n_traces,n_traces), np.nan)
        for first_trace_idx in range(n_traces):
            for second_trace_idx in range(n_traces):
                # decide if data has to be compared based on the config.pairwise_mode
                if is_needed_pairwise_combination(first_trace_idx, second_trace_idx, config.pairwise_mode):
                    pairwise_data[first_trace_idx, second_trace_idx] = eu.misc.call_function_from_config(
                        config.pairwise_function,
                        data_per_trace[first_trace_idx],
                        data_per_trace[second_trace_idx],
                    )

        # plot the results
        row_shift = 1
        col_shift = 1
        n_rows_and_cols = n_traces + 1
        # we leave some header out for these two cases
        if config.pairwise_mode == 'upper_triangle_not_identity':
            col_shift = 0
            n_rows_and_cols = n_traces
        elif config.pairwise_mode == 'lower_triangle_not_identity':
            row_shift = 0
            n_rows_and_cols = n_traces

        table_content = [[None] * (n_rows_and_cols) for _ in range(n_rows_and_cols)]

        table_content[0][0] = config.top_left_cell_content

        # set top and side header
        for trace_idx in range(n_traces):
            if config.pairwise_mode == 'upper_triangle_not_identity':
                # top header
                if trace_idx > 0:
                    table_content[0][trace_idx + col_shift] = trace_labels[trace_idx]
                # side header
                if trace_idx < n_traces - 1:
                    table_content[trace_idx + row_shift][0] = trace_labels[trace_idx]

            elif config.pairwise_mode == 'lower_triangle_not_identity':
                # top header
                if trace_idx < n_traces - 1:
                    table_content[0][trace_idx + col_shift] = trace_labels[trace_idx]
                # side header
                if trace_idx > 0:
                    table_content[trace_idx + row_shift][0] = trace_labels[trace_idx]

            else:
                # top header
                table_content[0][trace_idx + col_shift] = trace_labels[trace_idx]
                # side header
                table_content[trace_idx + row_shift][0] = trace_labels[trace_idx]

        # fill table
        for first_trace_idx in range(n_traces):
            for second_trace_idx in range(n_traces):
                if is_needed_pairwise_combination(first_trace_idx, second_trace_idx, config.pairwise_mode):

                    if isinstance(config.cell_format, str):
                        cell_data = config.cell_format.format(pairwise_data[first_trace_idx, second_trace_idx])
                    else:
                        cell_data = eu.misc.call_function_from_config(
                            config.cell_format,
                            pairwise_data[first_trace_idx, second_trace_idx])

                    table_content[first_trace_idx + row_shift][second_trace_idx + col_shift] = cell_data

        table = original_tabulate(
            table_content,
            headers='firstrow',
            **config.tabulate)

        return table


if __name__ == '__main__':

    # scalar values
    data = [[3, 5, 6]]
    data_labels = [('ds1', ['exp1', 'exp2', 'exp2'])]

    tabulate_pairwise(data, labels=data_labels)