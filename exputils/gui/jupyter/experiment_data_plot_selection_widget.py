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
import ipywidgets
from exputils.gui.jupyter.experiment_data_selection_widget import ExperimentDataSelectionWidget
import IPython


DEFAULT_PLOTLY_MEANSTD_SCATTER_CONFIG = """layout = dict(
    xaxis = dict(
        title = '', 
        range = [None, None]),
    yaxis = dict(
        title = '', 
        range = [None, None]),
),
moving_average = dict(
    n = 1
),
data_filter = dict(
    every_nth_step = dict(
        step = 1,
        include_final_step = False
    ),
),        
default_group_label = 'rep <group_idx>'"""

DEFAULT_PLOTLY_BOX_CONFIG = """layout = dict(
    xaxis = dict(
        title = '', 
        range = [None, None] 
        ),
    yaxis = dict(
        title = '', 
        range = [None, None] 
        )
    )"""

DEFAULT_PLOTLY_MEANSTD_BAR_CONFIG = """layout = dict(
    xaxis = dict(
        title = '', 
        range = [None, None] 
        ),
    yaxis = dict(
        title = '', 
        range = [None, None] 
        )
    ),
    default_group_label = 'rep <group_idx>'"""

DEFAULT_TABULATE_MEANSTD_CONFIG = """primary_content_function = np.nanmean,
secondary_content_function = np.nanstd,
flip_rows_and_cols = False,
tabulate=eu.AttrDict(
            tablefmt='html', #
            numalign='right',
        ),
cell_format = '{:.3f} ({:.3f})',
top_left_cell_content = ''"""

DEFAULT_TABULATE_PAIRWISE_CONFIG = """pairwise_function = eu.misc.mannwhitneyu_pvalue,
pairwise_mode = 'upper_triangle', # which pairs are compared? 'full', 'full_not_identity', 'upper_triangle', 'upper_triangle_not_identity', 'lower_triangle', 'lower_triangle_not_identity'
tabulate=eu.AttrDict(
            tablefmt='html', # 'html' or 'latex'
            numalign='right',
        ),
cell_format = '{}',
top_left_cell_content = 'p-value',
labels=[]"""

CODE_TEMPLATE_MULTILINE = """# Plotting of <datasources> 
import exputils as eu
<import_statements>

plot_config = <plot_function_config>

selection_widget = eu.gui.jupyter.ExperimentDataPlotSelectionWidget(
    experiment_data_loader,
    datasources=<datasources>,
    experiment_ids='all',
    repetition_ids='all',
    output_format=<output_format>,
    data_filter=<data_filter>,
    plot_function=<plot_function>,
    plot_function_config=plot_config,
    state_backup_name=<state_backup_name>,
    state_backup_variable_filter=['experiment_ids', 'repetition_ids'],  # only save these variables as backup
    is_datasources_selection=False,
    is_output_format_selection=False,
    is_data_filter_selection=False,
    is_plot_function_selection=False,
    is_plot_function_config_editor=False,
    is_code_producer=False) 
display(selection_widget)
selection_widget.plot_data()"""

CODE_TEMPLATE_SINGLELINE = """# Plotting of <datasources> 
import exputils as eu
<import_statements>

plot_config = <plot_function_config>

selection_widget = eu.gui.jupyter.ExperimentDataPlotSelectionWidget(experiment_data_loader, datasources=<datasources>, experiment_ids='all', repetition_ids='all', output_format=<output_format>, data_filter=<data_filter>, plot_function=<plot_function>, plot_function_config=plot_config, state_backup_name=<state_backup_name>, state_backup_variable_filter=['experiment_ids', 'repetition_ids'], is_datasources_selection=False, is_output_format_selection=False, is_data_filter_selection=False, is_plot_function_selection=False, is_plot_function_config_editor=False, is_code_producer=False)
display(selection_widget)
selection_widget.plot_data()"""

def config_obj_to_dict(config_obj):
    '''
    Transforms a potential configuration (either dict or string) to configuration dictionary.
    If it is a string, it tries to execute the <string> as python code with 'dict(<string>)'.
    If this fails, then the returned object the Exception.
    '''
    if config_obj is None:
        config = None
    elif isinstance(config_obj, dict):
        config = config_obj
    else:
        try:
            _locals = {}
            exec('import numpy as np;import exputils as eu;tmp_dict = dict({})'.format(config_obj), {}, _locals)
            config = _locals['tmp_dict']
        except Exception as err:
            config = err
    return config


class ExperimentDataPlotSelectionWidget(ExperimentDataSelectionWidget):

    @staticmethod
    def default_config():
        dc = ExperimentDataSelectionWidget.default_config()

        # do not show the get data button, this widget will create its own plotting button
        dc.is_get_experiment_data_button = False

        # dictionary with possible plotting function
        dc.plot_functions = {'plotly_meanstd_scatter': eu.gui.jupyter.plotly_meanstd_scatter,
                             'plotly_box': eu.gui.jupyter.plotly_box,
                             'plotly_meanstd_bar': eu.gui.jupyter.plotly_meanstd_bar,
                             'tabulate_meanstd': eu.gui.jupyter.tabulate_meanstd,
                             'tabulate_pairwise': eu.gui.jupyter.tabulate_pairwise,

        }

        # dictionary with plot_function_configs for each
        dc.plot_function_configs = {'plotly_meanstd_scatter': DEFAULT_PLOTLY_MEANSTD_SCATTER_CONFIG,
                                    'plotly_box': DEFAULT_PLOTLY_BOX_CONFIG,
                                    'plotly_meanstd_bar': DEFAULT_PLOTLY_MEANSTD_BAR_CONFIG,
                                    'tabulate_meanstd': DEFAULT_TABULATE_MEANSTD_CONFIG,
                                    'tabulate_pairwise': DEFAULT_TABULATE_PAIRWISE_CONFIG,
        }

        dc.is_plot_function_selection = True
        dc.plot_function = list(dc.plot_functions.keys())[0]
        dc.plot_function_selection = eu.AttrDict(
            hbox=eu.AttrDict(  # ipywidgets.HBox parameters
                layout=eu.AttrDict(
                    width='100%')),
            label=eu.AttrDict(  # ipywidgets.Label parameters
                value='Plot Function:',
                layout=eu.AttrDict(min_width='100px')),
            dropdown=eu.AttrDict(  # ipywidgets.Text parameters
                description='',
                layout=eu.AttrDict(width='100%')))

        dc.is_plot_function_config_editor = True
        dc.plot_function_config = None
        dc.plot_function_config_editor = eu.AttrDict(
            title = 'Plot Configuration',
            accordion=eu.AttrDict(  # ipywidgets.HBox parameters
                selected_index=None,  # collapse accordion at init
                layout=eu.AttrDict(
                    width='100%')),
            textarea=eu.AttrDict(  # ipywidgets.Label parameters
                placeholder='Provide the configuration of the plot function in form of a python dictionary ...',
                layout=eu.AttrDict(
                    min_width='100%'))) # TODO: start with a larger height at the beginning

        dc.is_plot_button = True
        dc.plot_button = eu.AttrDict(
            description='Plot Data',
            tooltip='Plots the data according to the selection.',
            layout=eu.AttrDict(width='100%', height='95%'))

        dc.code_producer.code_templates = [dict(name='Multi Line', code_template=CODE_TEMPLATE_MULTILINE),
                                           dict(name='Single Line', code_template=CODE_TEMPLATE_SINGLELINE)]

        dc.figure_output = eu.AttrDict()  # ipywidgets.Output parameters

        return dc


    def __init__(self, experiment_data, experiment_descriptions=None, config=None, **kwargs):

        super().__init__(experiment_data,
                         experiment_descriptions=experiment_descriptions,
                         config=config,
                         **kwargs)

        # add a figure output below the selection
        self.figure_output = None

        #########################
        # handle config input if not a state backup was loaded
        if not hasattr(self, '_plot_function_key') and not hasattr(self, '_plot_function') and not hasattr(self, '_plot_function_configs'):

            # use first plot function in plot_fuctions dictionary if non is provided
            if self.config.plot_function == '' or self.config.plot_function is None:
                plot_function = list(self.config.plot_functions.keys())[0]
            else:
                plot_function = self.config.plot_function

            if isinstance(plot_function, str):
                # config.plot_function is a key for the config.plot_functions dictionary

                if self.config.plot_function not in self.config.plot_functions:
                    raise ValueError('If config.plot_function is a string then it must be a key for the config.plot_functions dictionary!')

                self._plot_function_key = plot_function
                self._plot_function = self.config.plot_functions[self._plot_function_key]

            elif callable(plot_function):
                # if the config.plotfunction is a function handle
                self._plot_function_key = 'NONE'
                self._plot_function = plot_function

            else:
                raise TypeError('Unsupported type for config.plot_fuction! Only strings or function handles are valid.')

            # handle self._plot_function_configs
            self._plot_function_configs = self.config.plot_function_configs.copy()
            plot_function_config = self.config.plot_function_config
            if plot_function_config == '' or plot_function_config is None:
                # if no config.plot_function_config is given, then use the one from the config.plot_function_configs dictionary
                # create a new entry in _plot_function_configs if non exists for this plot_function_key
                if self._plot_function_key not in self._plot_function_configs:
                    self._plot_function_configs[self._plot_function_key] = None
            else:
                # if a config is given, then override the _plot_functions_config with it
                self._plot_function_configs[self._plot_function_key] = config_obj_to_dict(plot_function_config)

            # if the config is invalid and the user can not change it anymore, then raise an exception
            if not self.config.is_plot_function_config_editor \
                    and isinstance(self._plot_function_configs[self._plot_function_key], BaseException):
                raise self._plot_function_config[self._plot_function_key]

            if self._plot_function_key == 'NONE' and self.config.is_plot_function_selection:
                raise ValueError('If plot_function_selection is active, then the config.plot_function must be a key for the config.plot_functions dictionary!')

        ########################
        # add gui components
        selection_children = []

        # only allow selection of a plot function if the defined intial plot_function is not a function handle
        if self.config.is_plot_function_selection and callable(self.config.plot_function):
            self.config.is_plot_function_selection = False

        # selection of plot function
        if self.config.is_plot_function_selection:

            self.plot_function_selection_label_widget = ipywidgets.Label(**self.config.plot_function_selection.label)

            self.plot_function_selection_dropdown_widget = ipywidgets.Dropdown(
                options=list(self.config.plot_functions.keys()),
                value=self._plot_function_key,
                **self.config.plot_function_selection.dropdown)

            self.plot_function_selection_hbox_widget = ipywidgets.HBox(
                [self.plot_function_selection_label_widget, self.plot_function_selection_dropdown_widget],
                **self.config.plot_function_selection.hbox)

            selection_children.append(self.plot_function_selection_hbox_widget)

            # register event to know when a new plot function was selected
            self.plot_function_selection_dropdown_widget.observe(
                self._on_plot_function_selection_dropdown_widget_value_change,
                names='value')

        if self.config.is_plot_function_config_editor:

            self.plot_function_config_editor_textarea = ipywidgets.Textarea(
                value=self._plot_function_configs[self._plot_function_key],
                **self.config.plot_function_config_editor.textarea)

            self.plot_function_config_editor_accordion = ipywidgets.Accordion(
                children=[self.plot_function_config_editor_textarea],
                **self.config.plot_function_config_editor.accordion)
            self.plot_function_config_editor_accordion.set_title(0, self.config.plot_function_config_editor.title)

            selection_children.append(self.plot_function_config_editor_accordion)

            # register event to know when a new config was edited
            self.plot_function_config_editor_textarea.observe(
                self._on_plot_function_config_editor_value_change,
                names='value')

        # add selection items befor the box for the buttons
        eu.gui.jupyter.add_children_to_widget(self, selection_children, idx=-1)

        # add plotting button
        if self.config.is_plot_button:
            self.plot_button = ipywidgets.Button(**self.config.plot_button)
            self.plot_button.on_click(self._plot_button_on_click_handler)

            # append button to start of button box
            eu.gui.jupyter.add_children_to_widget(self.activity_hbox, self.plot_button, idx=0)


    def _on_plot_function_selection_dropdown_widget_value_change(self, event_descr):
        self._plot_function_key = event_descr['new']
        self._plot_function = self.config.plot_functions[self._plot_function_key]
        self.plot_function_config = self._plot_function_configs.get(self._plot_function_key, None)


    def _on_plot_function_config_editor_value_change(self, event_descr):
        self._plot_function_configs[self._plot_function_key] = event_descr['new']


    @property
    def plot_function(self):
        return self._plot_function


    @plot_function.setter
    def plot_function(self, plot_function):

        if isinstance(plot_function, str):
            # config.plot_function is a key for the config.plot_functions dictionary

            if plot_function not in self.config.plot_functions:
                raise ValueError(
                    'If plot_function is a string then it must be a key for the config.plot_functions dictionary!')

            self._plot_function_key = plot_function
            self._plot_function = self.config.plot_functions[self._plot_function_key]

            # also the config.plot_function_configs dict will be used
            self.plot_function_config = self._plot_function_configs[self._plot_function_key]

        elif callable(plot_function):
            # if the config.plotfunction is a function handle

            # try to find function in configured functions
            plot_function_key = 'NONE'
            for func_str, func in self.config.plot_functions.items():
                if func == plot_function:
                    plot_function_key = func_str
                    break

            self._plot_function_key = plot_function_key
            self._plot_function = plot_function
            if self._plot_function_key not in self._plot_function_configs:
                self._plot_function_configs[self._plot_function_key] = None

    @property
    def plot_function_config(self):
        return config_obj_to_dict(self._plot_function_configs[self._plot_function_key])


    @plot_function_config.setter
    def plot_function_config(self, plot_function_config):

        if self.config.is_plot_function_config_editor:

            if not isinstance(plot_function_config, str):
                raise ValueError('If the plot_function_config_editor is activated, then the given plot_function_config must be a string!')

            # was the gui element already created?
            if hasattr(self, 'plot_function_config_editor_textarea'):
                self.plot_function_config_editor_textarea.value = plot_function_config

        self._plot_function_configs[self._plot_function_key] = plot_function_config


    def _plot_button_on_click_handler(self, _):
        self.plot_data()


    @property
    def selection(self):
        '''AttrDict (dict) with the selected experiment data options.'''
        selection = super().selection
        selection.plot_function = self.plot_function
        selection.plot_function_config = self.plot_function_config
        return selection


    @selection.setter
    def selection(self, selection):
        super(self.__class__, self.__class__).selection.fset(self, selection)
        if 'plot_function' in selection: self.plot_function = selection.plot_function
        if 'plot_function_config' in selection: self.plot_function_config = selection.plot_function_config


    def get_widget_state(self):
        state = super().get_widget_state()

        if self._plot_function_key == 'NONE':
            state.plot_function = self.plot_function
        else:
            state.plot_function = self._plot_function_key
        state._plot_function_configs = self._plot_function_configs
        return state


    def set_widget_state(self, state):

        if '_plot_function_configs' in state:
            self._plot_function_configs = state._plot_function_configs  # set all gui configs

        if 'plot_function' in state:
            self.plot_function = state.plot_function

        if '_plot_function_configs' in state:
            self.plot_function_config = self._plot_function_configs[self._plot_function_key]  # update the view

        return super().set_widget_state(state)


    def plot_data(self):

        # display the figure
        # must be created here so that the display is created below the selection gui
        if self.figure_output is None:
            self.figure_output = ipywidgets.Output(**self.config.figure_output)
            IPython.display.display(self.figure_output)
        else:
            self.figure_output.clear_output(wait=True)

        with self.figure_output:
            print('Plotting ...')

            # load experimental data before plotting
            self.select_experiment_data()

            plot_config = self.plot_function_config
            if isinstance(plot_config, BaseException):
                raise plot_config
            else:
                display_obiect = self.plot_function(
                    self.selected_data,
                    labels=self.selected_data_labels,
                    config=plot_config)

                self.figure_output.clear_output(wait=True)
                IPython.display.display(display_obiect)


    def get_code_producer_variables(self):

        variables = super().get_code_producer_variables()

        plot_function_handle = self.plot_function
        variables.plot_function = plot_function_handle.__name__

        if plot_function_handle.__module__ == '__main__' or plot_function_handle.__module__ == 'builtins':
            # no extra imports
            variables.import_statements = '\n'
        else:
            variables.import_statements = 'from {} import {}'.format(plot_function_handle.__module__, variables.plot_function)

        # plot configuration as a dictionary
        if self.config.is_plot_function_config_editor:
            plot_function_config_str = 'eu.AttrDict(\n{})'.format(self.plot_function_config_editor_textarea.value)
        else:
            plot_function_config_dict = self.plot_function_config
            plot_function_config_str = 'eu.' + str(eu.AttrDict(plot_function_config_dict))

        variables.plot_function_config = plot_function_config_str

        return variables