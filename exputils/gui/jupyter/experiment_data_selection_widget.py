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
import warnings
from exputils.gui.jupyter.base_widget import BaseWidget
from exputils.gui.jupyter.experiment_ids_selection_widget import ExperimentIDsSelectionWidget
from exputils.gui.jupyter.repetition_ids_selection_widget import RepetitionIDsSelectionWidget
from exputils.gui.jupyter.code_producer_widget import CodeProducerWidget

# TODO: Bug - giving several datasources seems not not work, as they are combined to a single string
# TODO: Feature - add selection of label_templates for data sources, experiments, and repetitions
# TODO: Feature - add data source selection helper
# TODO: Feature - allow that changes of names in the experiment_data_loader are directly taken as updates here
# TODO: Refactor - put the output widget into this class and allow to print errors and warnings to it if data is loaded
# TODO: Feature - add on_selection_changed event
# TODO: Refactor - keep for each selection attribute (e.g. datasources) an internal variable (self._datasources) which
#       is updated if the selection changes. This allows to not overrider the config in the case of default values.

CODE_TEMPLATE_MULTILINE = """selection_widget = ExperimentDataSelectionWidget(
    experiment_data, 
    experiment_descriptions,
    datasources=<datasources>,
    experiment_ids=<experiment_ids>,
    repetition_ids=<repetition_ids>,
    output_format=<output_format>,
    data_filter=<data_filter>,
    state_backup_name=<state_backup_name>,
    state_backup_variable_filter=['experiment_ids', 'repetition_ids'],
    is_datasources_selection=False,
    is_output_format_selection=False,
    is_data_filter_selection=False,
    is_code_producer=False) 
display(selection_widget)"""

CODE_TEMPLATE_SINGLELINE = """selection_widget = ExperimentDataSelectionWidget(experiment_data, experiment_descriptions, datasources=<datasources>, experiment_ids=<experiment_ids>, repetition_ids=<repetition_ids>, output_format=<output_format>, data_filter=<data_filter>, state_backup_name=<state_backup_name>, is_datasources_selection=False, is_output_format_selection=False, is_data_filter_selection=False, is_code_producer=False)
display(selection_widget)"""


class ExperimentDataSelectionWidget(BaseWidget, ipywidgets.VBox):

    @staticmethod
    def default_config():
        dc = BaseWidget.default_config()

        dc.is_datasources_selection = True
        dc.datasources = ''
        dc.datasources_selection = eu.AttrDict(
            hbox=eu.AttrDict(layout=eu.AttrDict(width='100%')),  # ipywidgets.HBox parameters
            label=eu.AttrDict(  # ipywidgets.Label parameters
                value='Data Sources:',
                layout=eu.AttrDict(min_width='100px')),
            text=eu.AttrDict(  # ipywidgets.Text parameters
                placeholder='Provide a comma seperated list of data sources ...',
                description='',
                layout=eu.AttrDict(width='100%')))

        dc.is_experiment_ids_selection = True
        dc.experiment_ids = 'all'
        dc.experiment_ids_selection = eu.AttrDict(
            hbox=eu.AttrDict(layout=eu.AttrDict(width='100%')),  # ipywidgets.HBox parameters
            label=eu.AttrDict(  # ipywidgets.Label parameters
                value='Experiments:',
                layout=eu.AttrDict(min_width='100px')),
            multiselect=eu.AttrDict(  # exputils.gui.jupyter.ExperimentIDsSelectionWidget parameters
                main_vbox=eu.AttrDict(
                    layout=eu.AttrDict(width='100%'))))

        dc.is_repetition_ids_selection = True
        dc.repetition_ids = 'all'
        dc.repetition_ids_selection = eu.AttrDict(
            hbox=eu.AttrDict(layout=eu.AttrDict(width='100%')),  # ipywidgets.HBox parameters
            label=eu.AttrDict(  # ipywidgets.Label parameters
                value='Repetitions:',
                layout=eu.AttrDict(min_width='100px')),
            multiselect=eu.AttrDict(  # exputils.gui.jupyter.MultiSelectionWidget parameters
                main_vbox=eu.AttrDict(
                    layout=eu.AttrDict(width='100%'))))

        dc.is_output_format_selection = False
        dc.output_format = 'S,E,D'
        dc.output_format_selection = eu.AttrDict(
            hbox=eu.AttrDict(layout=eu.AttrDict(width='100%')),  # ipywidgets.HBox parameters
            label=eu.AttrDict(  # ipywidgets.Label parameters
                value='Output Format:',
                layout=eu.AttrDict(min_width='100px')),
            text=eu.AttrDict(  # ipywidgets.Text parameters
                placeholder='Provide output format description string ...',
                description='',
                layout=eu.AttrDict(width='100%')))

        dc.is_data_filter_selection = False
        dc.data_filter = ''
        dc.data_filter_selection = eu.AttrDict(
            hbox=eu.AttrDict(layout=eu.AttrDict(width='100%')),  # ipywidgets.HBox parameters
            label=eu.AttrDict(  # ipywidgets.Label parameters
                value='Filter:',
                layout=eu.AttrDict(min_width='100px')),
            text=eu.AttrDict(  # ipywidgets.Text parameters
                placeholder='Provide optional filter ...',
                description='',
                layout=eu.AttrDict(width='100%')))
        dc.main_vbox = eu.AttrDict()

        # Box that contains the elements that do activities
        dc.activity_hbox = eu.AttrDict(
            layout=eu.AttrDict(width='100%', height='100%')
        )

        dc.is_get_experiment_data_button = True
        dc.get_experiment_data_button = eu.AttrDict(
            description='Get Data',
            tooltip='Collects the exoerimental data according to the given selection.',
            layout=eu.AttrDict(width='100%', height='95%'))

        dc.is_code_producer = True
        dc.code_producer = eu.AttrDict(
            code_templates=[dict(name='Multi Line', code_template=CODE_TEMPLATE_MULTILINE),
                            dict(name='Single Line', code_template=CODE_TEMPLATE_SINGLELINE)],
            main_box=eu.AttrDict(layout=eu.AttrDict(width='25%', height='99%')))

        # config for collecting the data
        dc.select_experiment_data_func = eu.data.select_experiment_data  # function to get the data

        return dc


    def __init__(self, experiment_data_object, experiment_descriptions=None, config=None, **kwargs):

        # constructor of BaseWidget
        super().__init__(config=config, **kwargs)
        # constructor of VBox
        super(BaseWidget, self).__init__(
            **self.config.main_vbox)

        # handle input of either data loader widget or data itsel
        if isinstance(experiment_data_object, eu.gui.jupyter.ExperimentDataLoaderWidget):
            if experiment_descriptions is not None:
                warnings.warn('If an ExperimentDataLoaderWidget is provided, then the experiment_descriptions parameter will be ignored.')

            self._experiment_data = experiment_data_object.experiment_data
            self._experiment_descriptions = experiment_data_object.experiment_descriptions

            # register event at widget, if it loads new data
            experiment_data_object.on_experiment_data_loaded(self._on_new_experiment_data_handler)
        else:
            self._experiment_data = experiment_data_object
            self._experiment_descriptions = experiment_descriptions

        self._selected_data = None
        self._selected_data_labels = None

        # self._on_selection_changed_event_handlers = []
        self._on_data_collected_event_handlers = []

        child_widgets = []

        if self.config.is_datasources_selection:
            self.datasources_selection_label_widget = ipywidgets.Label(**self.config.datasources_selection.label)
            self.datasources_selection_text_widget = ipywidgets.Text(
                value='',
                **self.config.datasources_selection.text)
            self.datasources_selection_hbox_widget = ipywidgets.HBox(
                [self.datasources_selection_label_widget, self.datasources_selection_text_widget],
                **self.config.datasources_selection.hbox)
            child_widgets.append(self.datasources_selection_hbox_widget)

        if self.config.is_experiment_ids_selection:
            self.experiment_ids_selection_label_widget = ipywidgets.Label(**self.config.experiment_ids_selection.label)
            self.experiment_ids_selection_multiselect_widget = ExperimentIDsSelectionWidget(
                self.experiment_data,
                experiment_descriptions=self.experiment_descriptions,
                **self.config.experiment_ids_selection.multiselect)
            self.experiment_ids_selection_hbox_widget = ipywidgets.HBox(
                [self.experiment_ids_selection_label_widget, self.experiment_ids_selection_multiselect_widget],
                **self.config.experiment_ids_selection.hbox)
            child_widgets.append(self.experiment_ids_selection_hbox_widget)

        if self.config.is_repetition_ids_selection:
            self.repetition_ids_selection_label_widget = ipywidgets.Label(**self.config.repetition_ids_selection.label)
            self.repetition_ids_selection_multiselect_widget = RepetitionIDsSelectionWidget(
                self.experiment_data,
                experiment_descriptions=self.experiment_descriptions,
                **self.config.repetition_ids_selection.multiselect)
            self.repetition_ids_selection_hbox_widget = ipywidgets.HBox(
                [self.repetition_ids_selection_label_widget, self.repetition_ids_selection_multiselect_widget],
                **self.config.repetition_ids_selection.hbox)
            child_widgets.append(self.repetition_ids_selection_hbox_widget)

        if self.config.is_output_format_selection:
            self.output_format_selection_label_widget = ipywidgets.Label(**self.config.output_format_selection.label)
            self.output_format_selection_text_widget = ipywidgets.Text(
                value='',
                **self.config.output_format_selection.text)
            self.output_format_selection_hbox_widget = ipywidgets.HBox(
                [self.output_format_selection_label_widget, self.output_format_selection_text_widget],
                **self.config.output_format_selection.hbox)
            child_widgets.append(self.output_format_selection_hbox_widget)

        if self.config.is_data_filter_selection:
            self.data_filter_selection_label_widget = ipywidgets.Label(**self.config.data_filter_selection.label)
            self.data_filter_selection_text_widget = ipywidgets.Text(
                value='',
                **self.config.data_filter_selection.text)
            self.data_filter_selection_hbox_widget = ipywidgets.HBox(
                [self.data_filter_selection_label_widget, self.data_filter_selection_text_widget],
                **self.config.data_filter_selection.hbox)
            child_widgets.append(self.data_filter_selection_hbox_widget)

        activity_box_child_widgets = []
        if self.config.is_get_experiment_data_button:
            self.get_experiment_data_button = ipywidgets.Button(**self.config.get_experiment_data_button)
            self.get_experiment_data_button.on_click(self._get_experiment_data_button_on_click_handler)
            activity_box_child_widgets.append(self.get_experiment_data_button)

        if self.config.is_code_producer:
            self.code_producer_widget = CodeProducerWidget(
                code_variables=self.get_code_producer_variables,
                **self.config.code_producer)
            activity_box_child_widgets.append(self.code_producer_widget)

        self.activity_hbox = ipywidgets.HBox(
            children=activity_box_child_widgets,
            **self.config.activity_hbox)
        child_widgets.append(self.activity_hbox)

        eu.gui.jupyter.add_children_to_widget(self, child_widgets)

        # set initial selection from config
        self.datasources = self.config.datasources
        self.experiment_ids = self.config.experiment_ids
        self.repetition_ids = self.config.repetition_ids
        self.output_format = self.config.output_format
        self.data_filter = self.config.data_filter

        # load previously backuped selection if exists
        self.load_state_backup()


    @property
    def experiment_data(self):
        return self._experiment_data


    @property
    def experiment_descriptions(self):
        return self._experiment_descriptions


    def set_experiment_data(self, experiment_data, experiment_descriptions=None):
        self._experiment_data = experiment_data
        self._experiment_descriptions = experiment_descriptions
        self._update_selections_to_new_experiment_data()


    @property
    def selected_data(self):
        return self._selected_data


    @property
    def selected_data_labels(self):
        return self._selected_data_labels


    @property
    def datasources(self):
        if not self.config.is_datasources_selection:
            return eu.misc.str_to_list(self.config.datasources)
        else:
            return eu.misc.str_to_list(self.datasources_selection_text_widget.value)


    @datasources.setter
    def datasources(self, datasources):

        if isinstance(datasources, str):
            datasources = eu.misc.str_to_list(datasources)

        if not self.config.is_datasources_selection:
            self.config.datasources = datasources
        else:
            self.datasources_selection_text_widget.value = ', '.join(datasources)


    @property
    def experiment_ids(self):
        if not self.config.is_experiment_ids_selection:
            return self.config.experiment_ids
        else:
            return self.experiment_ids_selection_multiselect_widget.selected_experiment_ids


    @experiment_ids.setter
    def experiment_ids(self, experiment_ids):
        if not self.config.is_experiment_ids_selection:
            self.config.experiment_ids = experiment_ids
        else:
            self.experiment_ids_selection_multiselect_widget.selected_experiment_ids = experiment_ids


    @property
    def repetition_ids(self):
        if not self.config.is_repetition_ids_selection:
            return self.config.repetition_ids
        else:
            rep_ids = self.repetition_ids_selection_multiselect_widget.selected_repetition_ids
            if not rep_ids:
                rep_ids = 'none'
            return rep_ids


    @repetition_ids.setter
    def repetition_ids(self, repetition_ids):
        if not self.config.is_repetition_ids_selection:
            self.config.repetition_ids = repetition_ids
        else:
            self.repetition_ids_selection_multiselect_widget.selected_repetition_ids = repetition_ids


    @property
    def output_format(self):

        if not self.config.is_output_format_selection:
            output_format = self.config.output_format
        else:
            output_format = self.output_format_selection_text_widget.value

        if isinstance(output_format, str):
            output_format = tuple(output_format.split(','))

        # transform string to tuple: 'S,E,D' --> ('S','E','D')
        return output_format


    @output_format.setter
    def output_format(self, output_format):

        if isinstance(output_format, str):
            output_format = tuple(output_format.replace(' ', '').split(','))
        elif isinstance(output_format, list):
            output_format = tuple(output_format)

        if not self.config.is_output_format_selection:
            self.config.output_format = output_format
        else:
            self.output_format_selection_text_widget.value = ', '.join(output_format)


    @property
    def data_filter(self):

        if not self.config.is_data_filter_selection:
            return self.config.data_filter
        else:
            return self.data_filter_text_widget.value


    @data_filter.setter
    def data_filter(self, data_filter):

        if not self.config.is_data_filter_selection:
            self.config.data_filter = data_filter
        else:
            self.data_filter_text_widget.value = data_filter


    @property
    def selection(self):
        '''AttrDict (dict) with the selected experiment data options.'''
        return eu.AttrDict(
            datasources=self.datasources,
            experiment_ids=self.experiment_ids,
            repetition_ids=self.repetition_ids,
            output_format=self.output_format,
            data_filter=self.data_filter)


    @selection.setter
    def selection(self, selection):
        selection = eu.AttrDict(selection)
        if 'datasources' in selection: self.datasources = selection.datasources
        if 'experiment_ids' in selection: self.experiment_ids = selection.experiment_ids
        if 'repetition_ids' in selection: self.repetition_ids = selection.repetition_ids
        if 'output_format' in selection: self.output_format = selection.output_format
        if 'data_filter' in selection: self.data_filter = selection.data_filter


    def on_data_collected(self, handler):
        '''
        Register an event handler for the case new data was collected.
        The handler receives a dict with information about the event.
        '''
        self._on_data_collected_event_handlers.append(handler)


    def _call_data_collected_event(self):
        descr = {'name': 'data_collected',
                 'owner': self,
                 'type': 'change'}

        for handler in self._on_data_collected_event_handlers:
            handler(descr)


    def select_experiment_data(self):

        data = self.config.select_experiment_data_func(
            self.experiment_data,
            self.datasources,
            experiment_ids=self.experiment_ids,
            repetition_ids=self.repetition_ids,
            output_format=self.output_format,
            experiment_descriptions=self.experiment_descriptions)

        # some get data functions provide labels, some not
        if isinstance(data, tuple):
            self._selected_data = data[0]
            self._selected_data_labels = data[1]
        else:
            self._selected_data = data
            self._selected_data_labels = None

        self._call_data_collected_event()

        self.backup_state()

        return self.selected_data, self.selected_data_labels


    def _get_experiment_data_button_on_click_handler(self, _):
        self.select_experiment_data()


    def _code_production_button_on_click_handler(self, _):
        eu.gui.jupyter.create_new_cell(r"print('hello world')")


    def get_widget_state(self):
        state = super().get_widget_state()
        state.datasources = self.datasources
        state.experiment_ids = self.experiment_ids
        state.repetition_ids = self.repetition_ids
        state.output_format = self.output_format
        state.data_filter = self.data_filter
        return state


    def set_widget_state(self, state):
        if 'datasources' in state: self.datasources = state.datasources
        if 'experiment_ids' in state: self.experiment_ids = state.experiment_ids
        if 'repetition_ids' in state: self.repetition_ids = state.repetition_ids
        if 'output_format' in state: self.output_format = state.output_format
        if 'data_filter' in state: self.data_filter = state.data_filter
        return super().set_widget_state(state)


    def get_code_producer_variables(self):

        self.backup_state()

        if isinstance(self.experiment_ids, list):
            experiment_ids = str(self.experiment_ids)
        else:
            experiment_ids = r"'{}'".format(self.experiment_ids)

        if isinstance(self.repetition_ids, list):
            repetition_ids = str(self.repetition_ids)
        else:
            repetition_ids = r"'{}'".format(self.repetition_ids)

        return eu.AttrDict(
            datasources=str(self.datasources),
            experiment_ids=experiment_ids,
            repetition_ids=repetition_ids,
            output_format=self.output_format,
            data_filter=r"'{}'".format(self.data_filter),
            state_backup_name=r"'{}'".format(eu.gui.jupyter.misc.generate_random_state_backup_name()))


    def _on_new_experiment_data_handler(self, event_descr):
        '''
        Called if the experiment data loader widget loaded new experiment data.
        Updates the experiment_data of the selection widget.
        '''
        self.set_experiment_data(
            event_descr['owner'].experiment_data,
            event_descr['owner'].experiment_descriptions)


    def _update_selections_to_new_experiment_data(self):

        # create new experiment_id_selection
        if self.config.is_experiment_ids_selection:
            self.experiment_ids_selection_multiselect_widget = ExperimentIDsSelectionWidget(
                self.experiment_data,
                experiment_descriptions=self.experiment_descriptions,
                **self.config.experiment_ids_selection.multiselect)
            eu.gui.jupyter.set_children_of_widget(
                self.experiment_ids_selection_hbox_widget,
                1,
                self.experiment_ids_selection_multiselect_widget)

        # create new repetition_id_selection
        if self.config.is_repetition_ids_selection:
            self.repetition_ids_selection_multiselect_widget = RepetitionIDsSelectionWidget(
                self.experiment_data,
                experiment_descriptions=self.experiment_descriptions,
                **self.config.repetition_ids_selection.multiselect)
            eu.gui.jupyter.set_children_of_widget(
                self.repetition_ids_selection_hbox_widget,
                1,
                self.repetition_ids_selection_multiselect_widget)