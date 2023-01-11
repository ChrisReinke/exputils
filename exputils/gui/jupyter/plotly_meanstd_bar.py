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
import plotly.subplots


def plotly_meanstd_bar(data=None, config=None, **kwargs):
    """
    param repetition_ids: Either scalar int with single id, list with several that are used for each experiment, or a dict with repetition ids per experiment.
    """
    default_config = eu.AttrDict(
        subplots=eu.AttrDict(
            rows=None,
            cols=None,
            print_grid=False
        ),
        init_mode='mean_std',  # mean_std, mean, elements
        layout=eu.AttrDict(

            default_xaxis=eu.AttrDict(),  # if several subplots, then these are the default values for all xaxis config in fig.layout
            default_yaxis=eu.AttrDict(),  # if several subplots, then these are the default values for all yaxis config in fig.layout

            xaxis=eu.AttrDict(),
            yaxis=eu.AttrDict(),

            boxmode='group',

            updatemenus=[
                dict(type="buttons",
                     active=0,
                     buttons=[
                         eu.AttrDict(
                             label='with std',
                             method='restyle',
                             args=[{'error_y.visible': True}]),
                         eu.AttrDict(
                             label='without std',
                             method='restyle',
                             args=[{'error_y.visible': False}]),
                     ],
                     direction='right',
                     pad={'t': 70},
                     x=1,
                     xanchor='right',
                     y=0,
                     yanchor='top'
                     ),
            ]
        ),

        default_trace=eu.AttrDict(
            legendgroup=None,
            error_y=eu.AttrDict(visible=True),
        ),
        default_subplot_traces=[],
        traces=[],

        labels=[],  # holds all labels in a specific structure

        default_trace_label='<trace_idx>',
        trace_labels=[],

        default_group_label='<group_idx>',
        group_labels=[],

        default_colors=plotly.colors.DEFAULT_PLOTLY_COLORS,
    )
    config = eu.combine_dicts(kwargs, config, default_config)

    default_string_replace_pattern = '<{}>'

    if data is None:
        data = np.array([])

    # format data in form [subplot_idx:list][trace_idx:list][elems_per_trace:numpy.ndarray]
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

    # subplot_titles
    if config.labels and ('subplot_titles' not in config.subplots or config.subplots.subplot_titles == []):
        config.subplots.subplot_titles = [subplot_labels[0] for subplot_labels in config.labels]

    # identify the number of subplots
    n_subplots = len(data)

    # if not defined, set rows and cols of subplots
    if config.subplots.rows is None and config.subplots.cols is None:
        config.subplots.rows = n_subplots
        config.subplots.cols = 1
    elif config.subplots.rows is not None and config.subplots.cols is None:
        config.subplots.cols = int(np.ceil(n_subplots / config.subplots.rows))
    elif config.subplots.rows is None and config.subplots.cols is not None:
        config.subplots.rows = int(np.ceil(n_subplots / config.subplots.cols))

    # handle init mode
    if config.init_mode == 'mean_std':
        config.layout.updatemenus[0]['active'] = 0
        config.default_trace.error_y.visible = True
    elif config.init_mode == 'mean':
        config.layout.updatemenus[0]['active'] = 1
        config.default_trace.error_y.visible = False

    # make figure with subplots
    fig = plotly.subplots.make_subplots(**config.subplots)

    traces = []

    # interate over subplots
    for subplot_idx, subplot_data in enumerate(data):

        subplot_traces = []

        # create for each experiment a trace
        for trace_idx, cur_data in enumerate(subplot_data):  # data source

            means = []
            stds = []
            group_labels = []

            if np.ndim(cur_data) == 0 or np.ndim(cur_data) == 1:
                means.append(np.nanmean(cur_data))
                stds.append(np.nanstd(cur_data))
                group_labels.append('')
            else:
                # collect data over elements
                for elem_idx, elem_data in enumerate(cur_data):  # data elements

                    # get element data which could be in matrix format or array format
                    if np.ndim(elem_data) == 1:
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

                    means.append(np.nanmean(cur_elem_data))
                    stds.append(np.nanstd(cur_elem_data))

                    # handle trace for mean values
                    group_label = config.default_group_label
                    if len(config.group_labels) > elem_idx:
                        group_label = config.group_labels[elem_idx]
                    group_label = eu.misc.replace_str_from_dict(str(group_label), {'<group_idx>': elem_idx})

                    group_labels.append(group_label)

            # handle trace for mean values
            if config.labels:
                trace_label = config.labels[subplot_idx][1][trace_idx][0]
            else:
                trace_label = config.default_trace_label
                if len(config.trace_labels) > trace_idx:
                    trace_label = config.trace_labels[trace_idx]
            trace_label = eu.misc.replace_str_from_dict(str(trace_label), {'<trace_idx>': trace_idx})

            trace_params = dict(
                x=group_labels,
                y=means,
                error_y=dict(type='data', array=stds),
                name=trace_label,
                marker_color=config.default_colors[trace_idx % len(config.default_colors)])

            trace_config = config.default_trace.copy()
            if len(config.default_subplot_traces) > subplot_idx:
                trace_config = eu.combine_dicts(config.default_subplot_traces[subplot_idx], trace_config)
            if len(config.traces) > trace_idx:
                trace_config = eu.combine_dicts(config.traces[trace_idx], trace_config)

            trace_params = eu.combine_dicts(trace_config, trace_params)

            # handle legendgroup
            trace_legendgroup = trace_params.legendgroup
            if isinstance(trace_legendgroup, str):
                trace_legendgroup = eu.misc.replace_str_from_dict(
                    trace_legendgroup,
                    {'<trace_idx>': trace_idx,
                     '<subplot_idx>': subplot_idx})
            trace_params.legendgroup = trace_legendgroup

            cur_trace = plotly.graph_objs.Bar(**trace_params)
            subplot_traces.append(cur_trace)

        traces.append(subplot_traces)

    # set for the std toggle buttons which traces should be hidden and which ones should be shown
    layout = config.layout

    # set default values for all layouts
    def set_axis_properties_by_default(axis_name, fig_layout, config_layout):
        # sets the axis properties to default values

        def set_single_axis_property_default(cur_axis_name, default_name):
            if cur_axis_name in fig_layout or cur_axis_name in config_layout:
                cur_config = config_layout[cur_axis_name] if cur_axis_name in config_layout else dict()
                config_layout[cur_axis_name] = eu.combine_dicts(cur_config, config_layout[default_name])

        default_name = 'default_' + axis_name

        set_single_axis_property_default(axis_name, default_name)
        set_single_axis_property_default(axis_name + '1', default_name)
        axis_idx = 2
        while True:
            cur_axis_name = axis_name + str(axis_idx)

            if cur_axis_name not in fig_layout and cur_axis_name not in config_layout:
                break

            set_single_axis_property_default(cur_axis_name, default_name)
            axis_idx += 1

    set_axis_properties_by_default('xaxis', fig['layout'], layout)
    set_axis_properties_by_default('yaxis', fig['layout'], layout)

    # remove default fields, because they are not true proerties of the plotly layout
    del (layout['default_xaxis'])
    del (layout['default_yaxis'])

    cur_row = 1
    cur_col = 1
    for subplot_idx in range(n_subplots):
        n_traces = len(traces[subplot_idx])

        fig.add_traces(traces[subplot_idx],
                       rows=[cur_row] * n_traces,
                       cols=[cur_col] * n_traces)

        if cur_col < config.subplots.cols:
            cur_col += 1
        else:
            cur_col = 1
            cur_row += 1

    fig['layout'].update(layout)

    return fig