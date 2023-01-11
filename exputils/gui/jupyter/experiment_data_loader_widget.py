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
import pandas as pd
import qgrid
import os
from exputils.gui.jupyter.base_widget import BaseWidget
import IPython
import warnings

# TODO: Feature - allow to filter datasources that should be loaded
# TODO: Feature - progress bar during data loading
# TODO: Bugfix - If the order of the items is changed rapidely (buttons quicly pressed) then sometimes a wrong item gets selected afterwards
#                It is unclear what causes this issue.

class ExperimentDataLoaderWidget(BaseWidget, ipywidgets.VBox):

    @staticmethod
    def default_config():
        dc = BaseWidget.default_config()

        dc.load_experiment_descriptions_function = eu.AttrDict(
            func=eu.data.load_experiment_descriptions
        )
        dc.load_experiment_data_function = eu.AttrDict(
            func=eu.data.load_experiment_data
        )
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

        dc.move_buttons_box = eu.AttrDict(
            layout=eu.AttrDict(
                width='100%',
                display='flex',
                flex_flow='row',
                align_items='stretch'))

        dc.move_up_button = eu.AttrDict(
            layout=eu.AttrDict(
                width = '25%',
                height = 'auto'),
            description = u'\u02C5', # 'down',
            disabled = False,
            button_style = '',  # 'success', 'info', 'warning', 'danger' or ''
            tooltip = 'Moves the selected experiments up in the order.  (Only works if data is not filtered.)')

        dc.move_down_button = eu.AttrDict(
            layout=eu.AttrDict(
                width = '25%',
                height = 'auto'),
            description = u'\u02C4', #'up',
            disabled = False,
            button_style = '',  # 'success', 'info', 'warning', 'danger' or ''
            tooltip = 'Moves the selected experiments down in the order.  (Only works if data is not filtered.)')

        dc.sort_by_id_button = eu.AttrDict(
            layout=eu.AttrDict(
                width='50%',
                height='auto'),
            description='Sort by Experiment ID',  # 'up',
            disabled=False,
            button_style='',  # 'success', 'info', 'warning', 'danger' or ''
            tooltip='Resorts the experiments according to their ID.')

        dc.data_buttons_box = eu.AttrDict(
            layout=eu.AttrDict(
                width='100%',
                display='flex',
                flex_flow='row',
                align_items='stretch'))

        dc.load_data_button = eu.AttrDict(
            layout=eu.AttrDict(
                width = '75%',
                height = 'auto'),
            description = 'Load Data',
            disabled = False,
            button_style = '',  # 'success', 'info', 'warning', 'danger' or ''
            tooltip = 'Load experimental data.')

        dc.empty_data_button = eu.AttrDict(
            layout=eu.AttrDict(
                width = '25%',
                height = 'auto'),
            description = 'Empty Data',
            disabled = False,
            button_style = '',  # 'success', 'info', 'warning', 'danger' or ''
            tooltip = 'Empties the loaded experimental data to free memory.')


        # naming of columns in the dataframe (key: name in experiment_description dict, value: name in dataframe)
        dc.dataframe_column_names = {'id': 'experiment id',
                                     'order': 'order',
                                     'is_load_data': 'load data',
                                     'short_name': 'short name',
                                     'name': 'name',
                                     'description': 'description',
                                     'directory': 'directory'}

        dc.qgrid_widget = eu.AttrDict(
            show_toolbar = True,
            grid_options = {'autoEdit': True,
                            'sortable': False},
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

        self.move_up_btn = ipywidgets.Button(**self.config.move_up_button)
        self.move_down_btn = ipywidgets.Button(**self.config.move_down_button)
        self.sort_by_id_button = ipywidgets.Button(**self.config.sort_by_id_button)
        self.move_buttons_box = ipywidgets.Box(
            children=[self.move_down_btn, self.move_up_btn, self.sort_by_id_button],
            **self.config.move_buttons_box)

        self.load_data_btn = ipywidgets.Button(**self.config.load_data_button)
        self.empty_data_btn = ipywidgets.Button(**self.config.empty_data_button)
        self.data_buttons_box = ipywidgets.Box(
            children=[self.load_data_btn, self.empty_data_btn],
            **self.config.data_buttons_box)

        eu.gui.jupyter.add_children_to_widget(
            self,
            [self.top_button_box, self.qgrid_widget, self.move_buttons_box, self.data_buttons_box])

        # create an output widget
        self._output_widget = None

        self._update_qgrid()

        # register events
        self.load_descr_btn.on_click(self._handle_load_descr_button_on_click)
        self.reset_descr_btn.on_click(self._handle_reset_descr_button_on_click)
        self.load_data_btn.on_click(self._handle_load_data_button_on_click)
        self.empty_data_btn.on_click(self._handle_empty_data_button_on_click)
        self.move_up_btn.on_click(self._handle_move_up_button_on_click)
        self.move_down_btn.on_click(self._handle_move_down_button_on_click)
        self.sort_by_id_button.on_click(self._handle_sort_by_id_button_on_click)

        self._handle_qgrid_cell_edited_is_active = True

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


    def _handle_empty_data_button_on_click(self, btn):
        # errors are plotted in output widget and it will be cleaned after next button press
        with self._prepare_output_widget():
            # empty data and save widget state
            self.empty_data()
            self.backup_state()
            print('Emptied data.')


    def _handle_move_up_button_on_click(self, btn):
        # errors are plotted in output widget and it will be cleaned after next button press
        with self._prepare_output_widget():
            try:
                self.move_up_btn.disabled = True
                self.move_down_btn.disabled = True

                self.move_experiments_up()
            finally:
                self.move_up_btn.disabled = False
                self.move_down_btn.disabled = False

    def _handle_move_down_button_on_click(self, btn):
        # errors are plotted in output widget and it will be cleaned after next button press
        with self._prepare_output_widget():
            try:
                self.move_up_btn.disabled = True
                self.move_down_btn.disabled = True

                self.move_experiments_down()
            finally:
                self.move_up_btn.disabled = False
                self.move_down_btn.disabled = False

    def _handle_sort_by_id_button_on_click(self, btn):
        # errors are plotted in output widget and it will be cleaned after next button press
        with self._prepare_output_widget():
            self.resort_experiments_by_id()

    def _handle_qgrid_cell_edited(self, event, widget):
        with self._prepare_output_widget():

            if self._handle_qgrid_cell_edited_is_active:

                # update the experiment_description
                if event['name'] == 'cell_edited':

                    for expdescr_prop_name, df_col_name in self.config.dataframe_column_names.items():
                        if df_col_name == event['column']:
                            self.experiment_descriptions[event['index']][expdescr_prop_name] = event['new']
                            break

                    self.backup_state()

                    self._call_experiment_descriptions_updated_event()


    def _handle_qgrid_filter_changed(self, event, widget):
        with self._prepare_output_widget():

            # identify if a filter is active or not
            is_filter_active = len(self.qgrid_widget.df) != len(self.qgrid_widget.get_changed_df())

            if is_filter_active:
                # do not allow to change order
                self.move_up_btn.disabled = True
                self.move_down_btn.disabled = True

            else:
                # allow to change order
                self.move_up_btn.disabled = False
                self.move_down_btn.disabled = False

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

        self.qgrid_widget.on('filter_changed', self._handle_qgrid_filter_changed)

        self.sort_grid_by_order()


    def sort_grid_by_order(self):
        # hack to resort the experiments in the grid according to the order field
        content = dict(
            type='change_sort',
            sort_field=self.config.dataframe_column_names['order'],
            sort_ascending=True)
        self.qgrid_widget._handle_qgrid_msg_helper(content)


    def on_experiment_descriptions_updated(self, handler):
        """
        Register an event handler for the case that the experiment descriptions was changed.
        Please note, that this does not mean that the data was loaded according to the new experiment descriptions.
        Use the on_experiment_data_loaded for this purpose.
        The handler receives a dict with information about the event.
        """
        self._on_experiment_descriptions_updated_event_handlers.append(handler)


    def _call_experiment_descriptions_updated_event(self):
        for handler in self._on_experiment_descriptions_updated_event_handlers:
            handler(eu.AttrDict(
                name='experiment_descriptions_updated',
                new=self.experiment_descriptions,
                owner=self,
                type='change'))


    def on_experiment_data_loaded(self, handler):
        """
        Register an event handler for the case new data was loaded.
        The handler receives a dict with information about the event.
        """
        self._on_experiment_data_loaded_event_handlers.append(handler)


    def _call_experiment_data_loaded_event(self):
        for handler in self._on_experiment_data_loaded_event_handlers:
            handler(eu.AttrDict(
                name='data_loaded',
                new=self.experiment_data,
                owner=self,
                type='change'))


    def move_experiments_up(self, selected_items=None, is_select_changed_items=True):

        try:
            self._handle_qgrid_cell_edited_is_active = False

            if selected_items is None:
                selected_items = self.qgrid_widget.get_selected_df()

            if len(selected_items) > 0:

                order_col_name = self.config.dataframe_column_names['order']
                experiment_id_col_name = self.config.dataframe_column_names['id']

                # select according to the order
                selected_items = selected_items.sort_values(by=order_col_name)
                qgrid_df = self.qgrid_widget.get_changed_df()

                # make order the index to allow to seach by it
                all_items_sorted_by_order = qgrid_df.sort_values(by=order_col_name).reset_index().set_index(order_col_name)

                selected_idx = len(selected_items) - 1
                while selected_idx >= 0:

                    # identify current block of consequetively selected items
                    current_block_exp_ids = []

                    is_block = True
                    last_item_order = None
                    while is_block and selected_idx >= 0:
                        cur_item_order = selected_items.iloc[selected_idx][order_col_name]

                        if last_item_order is None or last_item_order - cur_item_order == 1:
                            current_block_exp_ids.append(selected_items.index[selected_idx])
                            selected_idx -= 1
                            last_item_order = cur_item_order
                        else:
                            is_block = False

                    order_of_highest_block_item = qgrid_df.loc[current_block_exp_ids[0]][order_col_name]

                    # only change orders if the block is not at the end of the list
                    if order_of_highest_block_item < len(qgrid_df) - 1:

                        # change the order of item below the block
                        exp_id_of_current_item_above_block = all_items_sorted_by_order.loc[order_of_highest_block_item + 1][experiment_id_col_name]

                        new_order = order_of_highest_block_item - len(current_block_exp_ids) + 1
                        self.qgrid_widget.edit_cell(
                            exp_id_of_current_item_above_block,
                            order_col_name,
                            new_order)
                        self.experiment_descriptions[exp_id_of_current_item_above_block]['order'] = new_order

                        # subtract 1 to all selected items in the block
                        for block_item_exp_id in current_block_exp_ids:
                            new_order = qgrid_df.loc[block_item_exp_id]['order'] + 1

                            self.qgrid_widget.edit_cell(
                                block_item_exp_id,
                                order_col_name,
                                new_order)
                            self.experiment_descriptions[block_item_exp_id]['order'] = new_order

                        #resort the experiments in the grid according to the order field
                        self.sort_grid_by_order()

                        # reslect the old elements
                        if is_select_changed_items:
                            self.qgrid_widget.change_selection(selected_items.index)

                        self.backup_state()

                        self._call_experiment_descriptions_updated_event()
        finally:
            self._handle_qgrid_cell_edited_is_active = True


    def move_experiments_down(self, selected_items=None, is_select_changed_items=True):

        try:
            self._handle_qgrid_cell_edited_is_active = False

            if selected_items is None:
                selected_items = self.qgrid_widget.get_selected_df()

            if len(selected_items) > 0:

                order_col_name = self.config.dataframe_column_names['order']
                experiment_id_col_name = self.config.dataframe_column_names['id']

                # select according to the order
                selected_items = selected_items.sort_values(by=order_col_name)
                qgrid_df = self.qgrid_widget.get_changed_df()

                # make order the index to allow to seach by it
                all_items_sorted_by_order = qgrid_df.sort_values(by=order_col_name).reset_index().set_index(order_col_name)

                selected_idx = 0
                while selected_idx < len(selected_items):

                    # identify current block of consequetively selected items
                    current_block_exp_ids = []

                    is_block = True
                    last_item_order = None
                    while is_block and selected_idx < len(selected_items):
                        cur_item_order = selected_items.iloc[selected_idx][order_col_name]

                        if last_item_order is None or cur_item_order - last_item_order == 1:
                            current_block_exp_ids.append(selected_items.index[selected_idx])
                            selected_idx += 1
                            last_item_order = cur_item_order
                        else:
                            is_block = False

                    order_of_lowest_block_item = qgrid_df.loc[current_block_exp_ids[0]][order_col_name]

                    # only change orders if the block is not at the end of the list
                    if order_of_lowest_block_item > 0:

                        # change the order of item below the block
                        exp_id_of_current_item_below_block = all_items_sorted_by_order.loc[order_of_lowest_block_item - 1][experiment_id_col_name]

                        new_order = order_of_lowest_block_item + len(current_block_exp_ids) - 1
                        self.qgrid_widget.edit_cell(
                            exp_id_of_current_item_below_block,
                            order_col_name,
                            new_order)
                        self.experiment_descriptions[exp_id_of_current_item_below_block]['order'] = new_order

                        # subtract 1 to all selected items in the block
                        for block_item_exp_id in current_block_exp_ids:
                            new_order = qgrid_df.loc[block_item_exp_id]['order'] - 1

                            self.qgrid_widget.edit_cell(
                                block_item_exp_id,
                                order_col_name,
                                new_order)
                            self.experiment_descriptions[block_item_exp_id]['order'] = new_order

                        # resort the experiments in the grid according to the order field
                        self.sort_grid_by_order()

                        # reselect the old elements
                        if is_select_changed_items:
                            self.qgrid_widget.change_selection(selected_items.index)

                        self.backup_state()

                        self._call_experiment_descriptions_updated_event()
        finally:
            self._handle_qgrid_cell_edited_is_active = True


    def resort_experiments_by_id(self):
        """
        Resets the order of the experiments according to their IDs.
        """
        try:
            # don't allow to change the qgrid during the operation
            self._handle_qgrid_cell_edited_is_active = False

            # sort experiments according to ids
            # get list of experiment ids
            sorted_existing_experiment_ids = sorted(list(self.experiment_descriptions.keys()))

            # update the order of the experiments according to the sorted list
            for order, exp_id in enumerate(sorted_existing_experiment_ids):
                self.experiment_descriptions[exp_id].order = order

            # update the gui according to the new order
            self._update_qgrid()

            # inform others the descriptions are changed
            self._call_experiment_descriptions_updated_event()

        finally:
            # qgrid can be changed again
            self._handle_qgrid_cell_edited_is_active = True


    def update_experiment_descriptions(self, is_reset=False):
        """Updates the experiment descriptions by adding new experiments and removing old experiments."""

        # load experiment descriptions
        new_exp_descr = eu.misc.call_function_from_config(
            self.config.load_experiment_descriptions_function,
            self.config.experiments_directory)

        if not self.experiment_descriptions or is_reset:
            self.experiment_descriptions = new_exp_descr
        else:
            # combine existing descriptions and new list

            # remove non-existing elements from exisiting descriptions
            deleted_experiments = set(self.experiment_descriptions.keys()).difference(set(new_exp_descr.keys()))
            for deleted_exp in deleted_experiments:
                del self.experiment_descriptions[deleted_exp]

            # kepp current order and add new experiments at the end of the list
            # get current order of experiment
            sorted_existing_experiment_ids = eu.data.get_ordered_experiment_ids_from_descriptions(self.experiment_descriptions)
            sorted_new_experiment_ids = eu.data.get_ordered_experiment_ids_from_descriptions(new_exp_descr)

            # remove existing experiment ids from the sorted list of new experiment ids
            for existing_exp_id in sorted_existing_experiment_ids:
                if existing_exp_id in sorted_new_experiment_ids:
                    sorted_new_experiment_ids.remove(existing_exp_id)

            # add new elements
            self.experiment_descriptions = eu.combine_dicts(self.experiment_descriptions, new_exp_descr)

            # update the order of the experiments according to the sorted lists
            for order, exp_id in enumerate(sorted_existing_experiment_ids + sorted_new_experiment_ids):
                self.experiment_descriptions[exp_id].order = order

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

    def empty_data(self):
        """Delete experiment_data to free memory."""
        if self.experiment_data:
            keys = list(self.experiment_data.keys())
            for key in keys:
                del self.experiment_data[key]

    def load_data(self):

        # delete old data to free memory
        self.empty_data()

        experiment_data = eu.misc.call_function_from_config(
            self.config.load_experiment_data_function,
            self.experiment_descriptions)

        # some data loader functions give as extra argument the experiment descriptions
        if isinstance(experiment_data, tuple):
            experiment_data = experiment_data[0]

        self.experiment_data = experiment_data

        self._call_experiment_data_loaded_event()
