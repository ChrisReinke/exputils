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
import plotly
import plotly.subplots
import exputils as eu

# TODO: Feature - allow to first unselect certain experiments, and then switch to their elements, to just see the selected experiments
#       https://webappl.blogspot.com/2020/05/plotly-eventregister.html, see plotly_restyle event
#       I believe I need to create a Figure object for this purpose
# TODO: Feature - custom x values

def plotly_meanstd_scatter(data=None, config=None, **kwargs):
    """
    Plots a plotly scatter (Scattergl or Scatter) plot.

    :param data: Data to plot. Should be in the following forms:
        - [subplot_idx:list][trace_idx:list][elems_per_trace:numpy.ndarray]
        - [trace_idx:list][elems_per_trace:numpy.ndarray]
        - elems_per_trace:numpy.ndarray

    :param config: Dictionary with configuration of plot.
        moving_average: Display the moving average over the steps per trace-element.
            n: number of steps over which the average should be computed.

        data_filter:
            every_nth_step: Either a integer with the number of steps or a dictionary.
                            In case of a dictionary:
                step: Number of steps between taken values. (default=None)
                include_final_step: Should the final step (the final value) also be included even if outside the stepping. (default=False)


    :return: Plotly figure object that can be displayed using display(fig_obj).
    """
    default_config = eu.AttrDict(

        # allows to display the moving average per element over n steps
        moving_average=eu.AttrDict(
            n=1,
            mode='fill_start'
        ),

        data_filter=eu.AttrDict(
            every_nth_step=eu.AttrDict(
                step=None,
                include_final_step=False),
        ),

        subplots=eu.AttrDict(  # paramters for the 'plotly.subplots.make_subplots' function
            rows=None,
            cols=None,
            print_grid=False
        ),
        std=eu.AttrDict(
            style='shaded',  # or errorbar
            steps=1,
            visible=True
        ),
        init_mode='mean_std',  # mean_std, mean, elements
        plotly_format='webgl',  # webgl or svg
        error_type='std', # std or sem (standard error of the mean)
        layout=eu.AttrDict(

            default_xaxis=eu.AttrDict(),
            # if several subplots, then these are the default values for all xaxis config in fig.layout
            default_yaxis=eu.AttrDict(),
            # if several subplots, then these are the default values for all yaxis config in fig.layout

            xaxis=eu.AttrDict(),
            yaxis=eu.AttrDict(),

            updatemenus=[
                eu.AttrDict(type="buttons",
                         active=0,
                         buttons=[
                             eu.AttrDict(label='mean + std',
                                      method='restyle',
                                      args=[{'visible': []}]),
                             eu.AttrDict(label='mean',
                                      method='restyle',
                                      args=[{'visible': []}]),
                             eu.AttrDict(label='elements',
                                      method='restyle',
                                      args=[{'visible': []}]),
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

        default_trace=eu.AttrDict(),

        default_mean_trace=eu.AttrDict(
            legendgroup='<subplot_idx>-<trace_idx>',  # subplot_idx, trace_idx
            hoverinfo='text+x',
        ),
        default_subplot_mean_traces=[],  # default config of traces per subplot
        mean_traces=[],

        default_std_trace=eu.AttrDict(
            legendgroup='<mean_trace_legendgroup>',  # subplot_idx, trace_idx, mean_trace_legendgroup
            hoverinfo='none',
            showlegend=False,
        ),
        default_subplot_std_traces=[],  # default config of traces per subplot
        std_traces=[],

        default_element_trace=eu.AttrDict(  # overall default
            legendgroup=None,
            # subplot_idx, trace_idx, elem_idx, subelem_idx, mean_trace_legendgroup, std_trace_legendgroup
        ),
        default_subplot_element_traces=[],  # default per subplot
        default_data_element_traces=[],  # default per data item
        element_traces=[],  # individual items

        # label configurations

        labels=[],  # holds all labels in a specific structure

        default_mean_label='<trace_idx>',
        mean_labels=[],

        default_element_label='<mean_label> - <subelem_idx>',
        # possible replacements: <mean_label>, <subelem_idx>, <elem_idx>, <trace_idx>
        element_labels=[],

        default_colors=plotly.colors.DEFAULT_PLOTLY_COLORS,
    )
    config = eu.combine_dicts(kwargs, config, default_config)

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

    if config.plotly_format.lower() == 'webgl':
        plotly_scatter_plotter = plotly.graph_objs.Scattergl
    elif config.plotly_format.lower() == 'svg':
        plotly_scatter_plotter = plotly.graph_objs.Scatter
    else:
        raise ValueError('Unknown config {!r} for plotly_format! Allowed values: \'webgl\', \'svg\'.')

    # make figure with subplots
    fig = plotly.subplots.make_subplots(**config.subplots)

    mean_traces = []
    elem_traces = []

    elem_idx = 0

    # interate over subplots
    for subplot_idx, subplot_data in enumerate(data):

        subplot_mean_traces = []
        subplot_elem_traces = []

        # iterate over traces
        for trace_idx, cur_data in enumerate(subplot_data):

            # do not plot data, if it does not exits
            if cur_data is not None:

                # in case the data is only 1 point, add an extra dimension
                if np.ndim(cur_data) == 1:
                    cur_data = np.array([cur_data]).transpose()

                # create a moving average over the data if requested
                if config.moving_average is not None and config.moving_average.n != 1:
                    cur_data = eu.misc.moving_average(
                        cur_data,
                        config.moving_average.n,
                        config.moving_average.mode)

                # define standard x_values
                x_values = list(range(cur_data.shape[1]))

                # filter the data if requested
                if config.data_filter.every_nth_step is not None:

                    if isinstance(config.data_filter.every_nth_step, dict):
                        step = config.data_filter.every_nth_step.step
                        is_include_final_step = config.data_filter.every_nth_step.include_final_step
                    else:
                        step = config.data_filter.every_nth_step
                        is_include_final_step = False

                    # detect if the final step was not in the selection
                    if is_include_final_step and cur_data.shape[1] % step == 0:
                        inds = np.zeros(cur_data.shape[1], dtype=bool)
                        inds[::step] = True
                        inds[-1] = True

                        cur_data = cur_data[:, inds]
                        x_values = x_values[::step] + [x_values[-1]]
                    else:
                        cur_data = cur_data[:, ::step]
                        x_values = x_values[::step]

                mean_data = np.nanmean(cur_data, axis=0)

                if config.error_type == 'std':
                    std_data = np.nanstd(cur_data, axis=0)
                elif config.error_type == 'sem':
                    std_data = np.nanstd(cur_data, axis=0, ddof=1) / np.sqrt(np.shape(cur_data)[0])
                else:
                    raise ValueError('Unknown error_type!')

                info_text = ['{} ± {}'.format(mean_data[idx], std_data[idx]) for idx in range(len(mean_data))]

                # define label of the trace
                if config.labels:
                    mean_label = config.labels[subplot_idx][1][trace_idx][0]
                else:
                    mean_label = config.default_mean_label
                    if len(config.mean_labels) > trace_idx:
                        mean_label = config.mean_labels[trace_idx]
                mean_label = eu.misc.replace_str_from_dict(str(mean_label), {'<trace_idx>': trace_idx})

                mean_trace_params = dict(
                    x=x_values,
                    y=mean_data,
                    line=dict(color=config.default_colors[trace_idx % len(config.default_colors)]),
                    name=mean_label,
                    text=info_text,
                )

                mean_trace_config = eu.combine_dicts(config.default_mean_trace, config.default_trace)
                if len(config.default_subplot_mean_traces) > subplot_idx:
                    mean_trace_config = eu.combine_dicts(config.default_subplot_mean_traces[subplot_idx], mean_trace_config)
                if len(config.mean_traces) > trace_idx:
                    mean_trace_config = eu.combine_dicts(config.mean_traces[trace_idx], mean_trace_config)

                mean_trace_params = eu.combine_dicts(mean_trace_config, mean_trace_params)

                # handle legendgroup
                mean_trace_legendgroup = mean_trace_params.legendgroup
                if isinstance(mean_trace_legendgroup, str):
                    mean_trace_legendgroup = eu.misc.replace_str_from_dict(mean_trace_legendgroup,
                                                                           {'<trace_idx>': trace_idx,
                                                                            '<subplot_idx>': subplot_idx})
                mean_trace_params.legendgroup = mean_trace_legendgroup

                cur_mean_trace = plotly_scatter_plotter(**mean_trace_params)
                subplot_mean_traces.append(cur_mean_trace)

                # handle trace for std values

                if config.std.style.lower() == 'shaded':

                    fill_color = config.default_colors[trace_idx % len(config.default_colors)]
                    fill_color = fill_color.replace('rgb', 'rgba')
                    fill_color = fill_color.replace(')', ', 0.2)')

                    std_trace_params = dict(
                        x=x_values + x_values[::-1],
                        y=np.hstack((mean_data + std_data, mean_data[::-1] - std_data[::-1])),
                        fill='tozerox',
                        line=dict(color='rgba(255,255,255,0)'),
                        fillcolor=fill_color,
                    )

                elif config.std.style.lower() == 'errorbar':

                    std_trace_params = dict(
                        x=x_values[::config.std.steps],
                        y=mean_data[::config.std.steps],
                        error_y=dict(type='data', array=std_data, visible=True),
                        mode='markers',
                        line=dict(color=config.default_colors[trace_idx % len(config.default_colors)]),
                        marker=dict(size=0, opacity=0),
                    )

                else:
                    raise ValueError(
                        'Unknown config.std.style ({!r})! Options: \'shaded\', \'errorbar\''.format(config.std.type))

                std_trace_config = eu.combine_dicts(config.default_std_trace, config.default_trace)
                if len(config.default_subplot_std_traces) > subplot_idx:
                    std_trace_config = eu.combine_dicts(config.default_subplot_std_traces[subplot_idx], std_trace_config)
                if len(config.std_traces) > trace_idx:
                    std_trace_config = eu.combine_dicts(config.std_traces[trace_idx], std_trace_config)
                std_trace_params = eu.combine_dicts(std_trace_config, std_trace_params)

                # handle legendgroup
                std_trace_legendgroup = std_trace_params.legendgroup
                if isinstance(std_trace_legendgroup, str):
                    std_trace_legendgroup = eu.misc.replace_str_from_dict(std_trace_legendgroup,
                                                                          {'<trace_idx>': trace_idx,
                                                                           '<subplot_idx>': subplot_idx,
                                                                           '<mean_trace_legendgroup>': mean_trace_legendgroup})
                std_trace_params.legendgroup = std_trace_legendgroup

                cur_std_trace = plotly_scatter_plotter(**std_trace_params)
                subplot_mean_traces.append(cur_std_trace)

                # traces for each data element
                n_elems = cur_data.shape[0]
                color_coeff_step = 1 / n_elems
                cur_color_coeff = 0 + color_coeff_step
                for cur_elem_idx in range(n_elems):

                    if config.labels and len(config.labels[subplot_idx][1][trace_idx][1]) > cur_elem_idx:
                        element_label = config.labels[subplot_idx][1][trace_idx][1][cur_elem_idx]
                    else:
                        element_label = config.default_element_label
                    if len(config.element_labels) > trace_idx:
                        element_label = config.element_labels[trace_idx]
                    element_label = eu.misc.replace_str_from_dict(str(element_label),
                                                                  {'<trace_idx>': trace_idx,
                                                                   '<subelem_idx>': cur_elem_idx,
                                                                   '<elem_idx>': elem_idx,
                                                                   '<mean_label>': mean_label})

                    color = eu.gui.misc.transform_color_str_to_tuple(
                        config.default_colors[trace_idx % len(config.default_colors)])
                    color = (color[0],
                             int(color[1] * cur_color_coeff),
                             int(color[2] * cur_color_coeff),
                             int(color[3] * cur_color_coeff))
                    color = eu.gui.misc.transform_color_tuple_to_str(color)
                    cur_color_coeff += color_coeff_step

                    element_trace_params = dict(
                        x=x_values,
                        y=cur_data[cur_elem_idx, :],
                        line=dict(color=color),
                        name=element_label,
                        visible=True,
                    )

                    element_trace_config = eu.combine_dicts(config.default_element_trace, config.default_trace)
                    if len(config.default_subplot_element_traces) > subplot_idx:
                        element_trace_config = eu.combine_dicts(config.default_subplot_element_traces[subplot_idx],
                                                                element_trace_config)
                    if len(config.default_data_element_traces) > cur_elem_idx:
                        element_trace_config = eu.combine_dicts(config.default_data_element_traces[cur_elem_idx],
                                                                element_trace_config)
                    if len(config.element_traces) > elem_idx:
                        element_trace_config = eu.combine_dicts(config.element_traces[elem_idx], element_trace_config)

                    element_trace_params = eu.combine_dicts(element_trace_config, element_trace_params)

                    # handle legendgroup
                    element_trace_legendgroup = element_trace_params.legendgroup
                    if isinstance(element_trace_legendgroup, str):
                        element_trace_legendgroup = eu.misc.replace_str_from_dict(
                            element_trace_legendgroup,
                            {'<subelem_idx>': cur_elem_idx,
                             '<elem_idx>': elem_idx,
                             '<trace_idx>': trace_idx,
                             '<subplot_idx>': subplot_idx,
                             '<mean_trace_legendgroup>': mean_trace_legendgroup,
                             '<std_trace_legendgroup>': std_trace_legendgroup})
                    element_trace_params.legendgroup = element_trace_legendgroup

                    cur_elem_trace = plotly_scatter_plotter(**element_trace_params)
                    subplot_elem_traces.append(cur_elem_trace)

                    elem_idx += 1

        mean_traces.append(subplot_mean_traces)
        elem_traces.append(subplot_elem_traces)

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

    update_menus_visible_meanstd = []
    update_menus_visible_mean = []
    update_menus_visible_elements = []

    for subplot_idx in range(len(mean_traces)):
        update_menus_visible_meanstd.extend(
            [True, True] * int(len(mean_traces[subplot_idx]) / 2) + [False] * int(len(elem_traces[subplot_idx])))
        update_menus_visible_mean.extend(
            [True, False] * int(len(mean_traces[subplot_idx]) / 2) + [False] * int(len(elem_traces[subplot_idx])))

        element_default_visibility = [elem_trace['visible'] for elem_trace in elem_traces[subplot_idx]]
        update_menus_visible_elements.extend(
            [False, False] * int(len(mean_traces[subplot_idx]) / 2) + element_default_visibility)

    if layout.updatemenus:

        layout.updatemenus[0]['buttons'][0]['args'][0]['visible'] = update_menus_visible_meanstd
        layout.updatemenus[0]['buttons'][1]['args'][0]['visible'] = update_menus_visible_mean
        layout.updatemenus[0]['buttons'][2]['args'][0]['visible'] = update_menus_visible_elements

        if config.init_mode == 'mean_std':
            config.layout.updatemenus[0]['active'] = 0
        elif config.init_mode == 'mean':
            config.layout.updatemenus[0]['active'] = 1
        elif config.init_mode == 'elements':
            config.layout.updatemenus[0]['active'] = 2
        else:
            raise ValueError(
                'Value {!r} for \'config.init_mode\' is not supported! Only \'mean_std\',\'mean\',\'elements\'.'.format(
                    config.init_mode))

    if config.init_mode == 'mean_std':
        trace_visibility = update_menus_visible_meanstd
    elif config.init_mode == 'mean':
        trace_visibility = update_menus_visible_mean
    elif config.init_mode == 'elements':
        trace_visibility = update_menus_visible_elements
    else:
        raise ValueError(
            'Value {!r} for \'config.init_mode\' is not supported! Only \'mean_std\',\'mean\',\'elements\'.'.format(
                config.init_mode))

    cur_row = 1
    cur_col = 1
    for subplot_idx in range(n_subplots):

        n_traces = len(mean_traces[subplot_idx]) + len(elem_traces[subplot_idx])

        fig.add_traces(mean_traces[subplot_idx] + elem_traces[subplot_idx],
                       rows=[cur_row] * n_traces,
                       cols=[cur_col] * n_traces)

        if cur_col < config.subplots.cols:
            cur_col += 1
        else:
            cur_col = 1
            cur_row += 1

    for trace_idx in range(len(fig['data'])):
        fig['data'][trace_idx]['visible'] = trace_visibility[trace_idx]

    fig['layout'].update(layout)

    return fig
