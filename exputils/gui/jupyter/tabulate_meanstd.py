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
from tabulate import tabulate as original_tabulate

def tabulate_meanstd(data=None, config=None, **kwargs):
    """
    Plots a table over several datasource.

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

        primary_content_function = np.nanmean,

        secondary_content_function = np.nanstd,

        flip_rows_and_cols = False,

        tabulate=eu.AttrDict(
            tablefmt='html', #
            numalign='right',
        ),

        cell_format = '{:.3f} ({:.3f})',

        top_left_cell_content = '',

        default_row_label = '<row_idx>',
        default_column_label = '<column_idx>',

        labels=[],  # holds all labels in a specific structure

    )
    config = eu.combine_dicts(kwargs, config, default_config)

    # remove the secondary information from the cell_format if the secondary information is set to None and the cell_format was not changed
    if config.secondary_content_function is None and config.cell_format == default_config.cell_format:
        config.cell_format = '{}'

    if data is None:
        data = np.array([])

    # format data in form [rows][columns][elems_per_trace:numpy.ndarray]
    # subplot is a single table
    if isinstance(data, np.ndarray):
        data = [[data]]
    elif isinstance(data, list) and isinstance(data[0], np.ndarray):
        data = [data]
    elif not isinstance(data, list) and not isinstance(data[0], list) and not isinstance(data[0][0], np.ndarray):
        raise ValueError('Unsupported type of data!')

    # handle different input formats of labels
    if config.labels:
        # if only labels for columns are given, then add an empty label for the sub figure
        if isinstance(config.labels, list) and not isinstance(config.labels[0], tuple):
            config.labels = [('', config.labels)]

    row_headers = []
    column_headers = []

    primary_data = []
    secondary_data = []

    # interate over rows (subplots)
    for row_idx, row_data in enumerate(data):

        primary_data.append([])
        secondary_data.append([])

        # define label of the row
        if config.labels:
            row_label = config.labels[row_idx][0]
        else:
            row_label = config.default_row_label
        row_label = eu.misc.replace_str_from_dict(str(row_label), {'<row_idx>': row_idx})
        row_headers.append(row_label)

        # collect the data and labels for each trace
        for column_idx, cur_data in enumerate(row_data):

            # get column_header from labels of first column
            if row_idx == 0:

                # define label of the row
                if config.labels:
                    column_label = config.labels[row_idx][1][column_idx]
                    if isinstance(column_label, tuple):
                        column_label = column_label[0]
                else:
                    column_label = config.default_column_label
                column_label = eu.misc.replace_str_from_dict(str(column_label), {'<column_idx>': column_idx})
                column_headers.append(column_label)

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

            # try:
            if data_points[0] is not None:
                primary_data[row_idx].append(config.primary_content_function(data_points))

                if config.secondary_content_function:
                    secondary_data[row_idx].append(config.secondary_content_function(data_points))
                else:
                    secondary_data[row_idx].append(None)
            else:
                primary_data[row_idx].append(None)
                secondary_data[row_idx].append(None)



    # plot the results
    n_rows = len(primary_data)
    n_columns = len(primary_data[0])
    if config.flip_rows_and_cols:
        n_rows = len(primary_data[0])
        n_columns = len(primary_data)
        tmp = row_headers
        row_headers = column_headers
        column_headers = tmp

    table_content = [[None] * (n_columns + 1) for _ in range(n_rows + 1)]
    table_content[0][0] = config.top_left_cell_content


    # set row and column headers
    for row_idx in range(n_rows):
        table_content[row_idx + 1][0] = row_headers[row_idx]
    for column_idx in range(n_columns):
        table_content[0][column_idx + 1] = column_headers[column_idx]

    # fill table
    for row_idx in range(n_rows):
        for column_idx in range(n_columns):

            data_1_idx = row_idx
            data_2_idx = column_idx
            if config.flip_rows_and_cols:
                data_1_idx = column_idx
                data_2_idx = row_idx

            if primary_data[data_1_idx][data_2_idx] is None:
                cell_data = ''
            else:
                if isinstance(config.cell_format, str):
                    cell_data = config.cell_format.format(
                        primary_data[data_1_idx][data_2_idx],
                        secondary_data[data_1_idx][data_2_idx])
                else:
                    cell_data = eu.misc.call_function_from_config(
                        config.cell_format,
                        primary_data[data_1_idx][data_2_idx],
                        secondary_data[data_1_idx][data_2_idx])

            table_content[row_idx + 1][column_idx + 1] = cell_data

    table = original_tabulate(
        table_content,
        headers='firstrow',
        **config.tabulate)

    return table
