import exputils as eu
import ipywidgets
import pandas as pd
import qgrid
import os
from exputils.gui.jupyter.base_widget import BaseWidget
import IPython
import warnings

# TODO: Feature - ordering of experiments
# TODO: Feature - allow to filter datasources that should be loaded
# TODO: Feature - progress bar during data loading

class ExperimentDataLoaderWidget(BaseWidget, ipywidgets.VBox):

    @staticmethod
    def default_config():
        dc = BaseWidget.default_config()

        dc.load_experiment_descriptions_function = eu.data.load_experiment_descriptions
        dc.load_experiment_data_function = eu.data.load_experiment_data
        dc.experiments_directory = os.path.join('..', eu.DEFAULT_EXPERIMENTS_DIRECTORY)

        dc.main_box = eu.AttrDict(
            layout=eu.AttrDict(
                width='99%',
                display='flex',
                flex_flow='column',
                align_items='stretch'))

        dc.top_button_box = eu.AttrDict(
            layout=eu.AttrDict(
                width='100%',
                display='flex',
                flex_flow='row',
                align_items='stretch'))

        dc.load_descr_button = eu.AttrDict(
            layout=eu.AttrDict(
                width = '75%',
                height = 'auto'),
            description = 'Update Descriptions',
            disabled = False,
            button_style = '',  # 'success', 'info', 'warning', 'danger' or ''
            tooltip = 'Update for the selected experiment and repetition.')

        dc.reset_descr_button = eu.AttrDict(
            layout=eu.AttrDict(
                width = '25%',
                height = 'auto'),
            description = 'Reset Descriptions',
            disabled = False,
            button_style = '',  # 'success', 'info', 'warning', 'danger' or ''
            tooltip = 'Reset all experiment descriptions.')

        dc.load_data_button = eu.AttrDict(
            layout=eu.AttrDict(
                width = 'auto',
                height = 'auto'),
            description = 'Load Data',
            disabled = False,
            button_style = '',  # 'success', 'info', 'warning', 'danger' or ''
            tooltip = 'Load experimental data.')

        # naming of columns in the dataframe (key: name in experiment_description dict, value: name in dataframe)
        dc.dataframe_column_names = {'id': 'experiment id',
                                     'is_load_data': 'load data',
                                     'short_name': 'short name',
                                     'name': 'name',
                                     'description': 'description',
                                     'directory': 'directory'}

        dc.qgrid_widget = eu.AttrDict(
            show_toolbar = True,
            grid_options = {'autoEdit': True},
            column_options = {'editable': False},
            column_definitions = {
                'load data': {'editable': True},
                'short name': {'editable': True},
                'name': {'editable': True},
                'description': {'editable': True}})

        dc.output_widget = eu.AttrDict()

        return dc


    def __init__(self, config=None, **kwargs):
        # constructor of BaseWidget
        super().__init__(config=config, **kwargs)
        # constructor of GridspecLayout
        super(BaseWidget, self).__init__(
            **self.config.main_box)

        self.experiment_descriptions = None
        self.experiment_data = None

        # list with registered event handlers for the data collected event
        self._on_experiment_data_loaded_event_handlers = []
        self._on_experiment_descriptions_updated_event_handlers = []

        self.load_state_backup()

        self.update_experiment_descriptions()

        # create gui elements
        self.load_descr_btn = ipywidgets.Button(**self.config.load_descr_button)
        self.reset_descr_btn = ipywidgets.Button(**self.config.reset_descr_button)
        self.top_button_box = ipywidgets.Box(
            children=[self.load_descr_btn, self.reset_descr_btn],
            **self.config.top_button_box)
        self.qgrid_widget = ipywidgets.Box()  # initialize with dummy, will be overridden by update function
        self.load_data_btn = ipywidgets.Button(**self.config.load_data_button)
        eu.gui.jupyter.add_children_to_widget(
            self,
            [self.top_button_box, self.qgrid_widget, self.load_data_btn])

        # create an output widget
        self._output_widget = None

        self._update_qgrid()

        # register events
        self.load_descr_btn.on_click(self._handle_load_descr_button_on_click)
        self.reset_descr_btn.on_click(self._handle_reset_descr_button_on_click)
        self.load_data_btn.on_click(self._handle_load_data_button_on_click)

    def _prepare_output_widget(self):

        if self._output_widget is None:
            self._output_widget = ipywidgets.Output(**self.config.output_widget)
            IPython.display.display(self._output_widget)
        else:
            warnings.resetwarnings()
            self._output_widget.clear_output(wait=False)

        return self._output_widget


    def _handle_load_descr_button_on_click(self, btn):
        # errors are plotted in output widget and it will be cleaned after next button press
        with self._prepare_output_widget():
            self.update_experiment_descriptions(is_reset=False)
            self._update_qgrid()


    def _handle_reset_descr_button_on_click(self, btn):
        # errors are plotted in output widget and it will be cleaned after next button press
        with self._prepare_output_widget():
            self.update_experiment_descriptions(is_reset=True)
            self._update_qgrid()


    def _handle_load_data_button_on_click(self, btn):
        # errors are plotted in output widget and it will be cleaned after next button press
        with self._prepare_output_widget():
            # load data and save widget state
            print('Load data ...')
            self.load_data()
            self.backup_state()
            print('Data successfully loaded.')


    def _handle_qgrid_cell_edited(self, event, widget):

        # update the experiment_description
        if event['name'] == 'cell_edited':

            for expdescr_prop_name, df_col_name in self.config.dataframe_column_names.items():
                if df_col_name == event['column']:
                    self.experiment_descriptions[event['index']][expdescr_prop_name] = event['new']
                    break

            self.backup_state()

            self._call_experiment_descriptions_updated_event()


    def _update_qgrid(self):

        # convert experiment description to the dataframe
        df = pd.DataFrame()
        for exp_descr_field_name, df_column_name in self.config.dataframe_column_names.items():
            df[df_column_name] = [descr[exp_descr_field_name] for descr in self.experiment_descriptions.values()]

        df = df.set_index(self.config.dataframe_column_names['id'])

        # create a new qgrid widget with the dataframe
        for opt_name, opt_value in self.config.qgrid_widget.grid_options.items():
            qgrid.set_grid_option(opt_name, opt_value)

        self.qgrid_widget = qgrid.show_grid(df,
                                            column_options=self.config.qgrid_widget.column_options,
                                            column_definitions=self.config.qgrid_widget.column_definitions,
                                            show_toolbar=self.config.qgrid_widget.show_toolbar)

        eu.gui.jupyter.remove_children_from_widget(self, 1)
        eu.gui.jupyter.add_children_to_widget(self, self.qgrid_widget, idx=1)

        self.qgrid_widget.on('cell_edited', self._handle_qgrid_cell_edited)


    def on_experiment_descriptions_updated(self, handler):
        '''
        Register an event handler for the case that the experiment descriptions was changed.
        Please note, that this does not mean that the data was loaded according to the new experiment descriptions.
        Use the on_experiment_data_loaded for this purpose.
        The handler receives a dict with information about the event.
        '''
        self._on_experiment_descriptions_updated_event_handlers.append(handler)


    def _call_experiment_descriptions_updated_event(self):
        for handler in self._on_experiment_descriptions_updated_event_handlers:
            handler(eu.AttrDict(
                name='experiment_descriptions_updated',
                new=self.experiment_descriptions,
                owner=self,
                type='change'))


    def on_experiment_data_loaded(self, handler):
        '''
        Register an event handler for the case new data was loaded.
        The handler receives a dict with information about the event.
        '''
        self._on_experiment_data_loaded_event_handlers.append(handler)


    def _call_experiment_data_loaded_event(self):
        for handler in self._on_experiment_data_loaded_event_handlers:
            handler(eu.AttrDict(
                name='data_loaded',
                new=self.experiment_data,
                owner=self,
                type='change'))


    def update_experiment_descriptions(self, is_reset=False):
        '''Updates the experiment descriptions by adding new experiments and removing old experiments.'''

        # load experiment descriptions
        new_exp_descr = self.config.load_experiment_descriptions_function(self.config.experiments_directory)

        if not self.experiment_descriptions or is_reset:
            self.experiment_descriptions = new_exp_descr
        else:
            # combine existing descriptions and new list

            # remove non-existing elements from exisiting descriptions
            deleted_experiments = set(self.experiment_descriptions.keys()).difference(set(new_exp_descr.keys()))
            for deleted_exp in deleted_experiments:
                del self.experiment_descriptions[deleted_exp]

            # add new elements
            self.experiment_descriptions = eu.combine_dicts(self.experiment_descriptions, new_exp_descr)

            # do not keep the repetition ids from existing ones, but use the ones from the new discriptions
            # otherwise, if new repetitions are added, they will not be used
            for new_descr in new_exp_descr.values():
                self.experiment_descriptions[new_descr.id].repetition_ids = new_descr.repetition_ids

        self._call_experiment_descriptions_updated_event()


    def get_widget_state(self):
        state = super().get_widget_state()
        state.experiment_descriptions = self.experiment_descriptions
        return state


    def set_widget_state(self, state):
        if 'experiment_descriptions' in state: self.experiment_descriptions  = state.experiment_descriptions
        return super().set_widget_state(state)


    def load_data(self):

        experiment_data = self.config.load_experiment_data_function(self.experiment_descriptions)

        # some data loader functions give as extra argument the experiment descriptions
        if isinstance(experiment_data, tuple):
            experiment_data = experiment_data[0]

        self.experiment_data = experiment_data

        self._call_experiment_data_loaded_event()