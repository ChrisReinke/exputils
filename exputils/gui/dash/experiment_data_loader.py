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
import pandas as pd
import os
import uuid
from dash import Dash, html, Input, Output, State, callback_context, no_update, callback
import dash_ag_grid as dag


# TODO: Feature - allow to filter datasources that should be loaded
# TODO: Feature - progress bar during data loading

class ExperimentDataLoader(html.Div):
    """
    Dash component for loading experiment data which can then be used for analysis and visualization.

    The component allows to select which experiments and datasources are loaded.
    It provides basically a GUI for the [load_experiment_data][exputils.data.load_experiment_data] function.
    It is also possible to define callback functions that allow to compute statistics of the
    loaded data or alter the data.
    After the user loaded the data through the application it is available via its `experiment_data` property.

    Functionality:

    - _Update Descriptions_: Load the descriptions of new experiments.
    This can be used to update the table after more experiments have been performed.
    - _Reset Descriptions_: Resets the descriptions of experiments in the table to their default if they had been changed by the user.
    - _Up Button_: Moves the selected experiments up in the order.
    - _Down Button_: Moves the selected experiments down in the order.
    - _Sort by Experiment ID_: Resorts the experiments according to their ID.
    - _Load Data_: Loads the data of all selected experiments. It is then available via the `experiment_data` property.
    - _Empty Data_: Empties the loaded data to free memory.
    """

    class Ids:
        """Return ids of internal components."""
        
        @staticmethod
        def experiment_grid(component_id: str):
            return f"{component_id}-experiment-grid"
        
        @staticmethod 
        def update_descriptions_btn(component_id: str):
            return f"{component_id}-update-descriptions-btn"
            
        @staticmethod
        def reset_descriptions_btn(component_id: str):
            return f"{component_id}-reset-descriptions-btn"
            
        @staticmethod
        def move_up_btn(component_id: str):
            return f"{component_id}-move-up-btn"
            
        @staticmethod
        def move_down_btn(component_id: str):
            return f"{component_id}-move-down-btn"
            
        @staticmethod
        def sort_by_id_btn(component_id: str):
            return f"{component_id}-sort-by-id-btn"
            
        @staticmethod
        def load_data_btn(component_id: str):
            return f"{component_id}-load-data-btn"
            
        @staticmethod
        def empty_data_btn(component_id: str):
            return f"{component_id}-empty-data-btn"
            
        @staticmethod
        def output_status(component_id: str):
            return f"{component_id}-output-status"

    @staticmethod
    def default_config():
        """Generates the default configuration for the component.

        Returns:
            dict: A dictionary containing default configurations for various components.
        """
        dc = eu.AttrDict()

        dc.load_experiment_descriptions_function = eu.AttrDict(
            func=eu.data.load_experiment_descriptions
        )
        dc.load_experiment_data_function = eu.AttrDict(
            func=eu.data.load_experiment_data
        )
        dc.experiments_directory = os.path.join('..', eu.DEFAULT_EXPERIMENTS_DIRECTORY)

        dc.info_area = eu.AttrDict()
        dc.info_area.is_visible = True
        dc.info_area.style = {
            'padding': '5px', 
            'border': '1px solid #ddd', 
            'borderRadius': '5px',
            'backgroundColor': '#f9f9f9', 
            'minHeight': '30px'
        }

        return dc

    def __init__(self, component_id=None, config=None, load_experiment_descriptions_function=None, load_experiment_data_function=None, **kwargs):
        # Allow developers to pass in their own `component_id`
        if component_id is None:
            component_id = str(uuid.uuid4())
        
        self.component_id = component_id
        self.config = eu.combine_dicts(kwargs, config, self.default_config())
        
        # Override config functions if provided directly
        if load_experiment_descriptions_function is not None:
            self.config.load_experiment_descriptions_function = eu.AttrDict(func=load_experiment_descriptions_function)
        if load_experiment_data_function is not None:
            self.config.load_experiment_data_function = eu.AttrDict(func=load_experiment_data_function)
        
        self.experiment_descriptions = None
        self.experiment_data = None

        # list with registered event handlers for the data collected event
        self._on_experiment_data_loaded_event_handlers = []
        self._on_experiment_descriptions_updated_event_handlers = []

        # Initialize experiment descriptions
        self.update_experiment_descriptions()
        
        # Create initial dataframe for the grid
        df = self._create_dataframe()
        
        # Define column definitions for AG Grid
        columnDefs = [
            {'field': 'order', 'headerName': 'Order', 'width': 80, 'editable': False},
            {'field': 'id', 'headerName': 'Experiment ID', 'width': 120, 'editable': False},
            {'field': 'is_load_data', 'headerName': 'Load Data', 'width': 100, 'editable': True},
            {'field': 'name', 'headerName': 'Name', 'width': 200, 'editable': True},
            {'field': 'short_name', 'headerName': 'Short Name', 'width': 120, 'editable': True},
            {'field': 'description', 'headerName': 'Description', 'width': 300, 'editable': True},
            {'field': 'directory', 'headerName': 'Directory', 'width': 200, 'editable': False}
        ]

        # Create AG Grid component
        grid = dag.AgGrid(
            id=self.Ids.experiment_grid(component_id),
            rowData=df.to_dict("records"),
            columnDefs=columnDefs,
            dashGridOptions={
                "animateRows": False, 
                "rowSelection": "multiple",
            },
            style={"height": "400px", "width": "100%"}
        )

        # Define the layout
        gui_elements = [
            # Top button row
            html.Div([
                html.Button('Update Descriptions', id=self.Ids.update_descriptions_btn(component_id), n_clicks=0, 
                           style={'width': '75%', 'marginRight': '5px'},
                           title='Update for the selected experiment and repetition.'),
                html.Button('Reset Descriptions', id=self.Ids.reset_descriptions_btn(component_id), n_clicks=0,
                           style={'width': '25%'},
                           title='Reset all experiment descriptions.')
            ], style={'display': 'flex', 'marginBottom': '10px', 'width': '100%'}),
            
            # Grid
            html.Div([grid], style={'marginBottom': '10px'}),
            
            # Move buttons row
            html.Div([
                html.Button('↓', id=self.Ids.move_down_btn(component_id), n_clicks=0, 
                           style={'width': '25%', 'marginRight': '5px'},
                           title='Moves the selected experiments down in the order.'),
                html.Button('↑', id=self.Ids.move_up_btn(component_id), n_clicks=0,
                           style={'width': '25%', 'marginRight': '5px'},
                           title='Moves the selected experiments up in the order.'),
                html.Button('Sort by Experiment ID', id=self.Ids.sort_by_id_btn(component_id), n_clicks=0,
                           style={'width': '50%'},
                           title='Resorts the experiments according to their ID.')
            ], style={'display': 'flex', 'marginBottom': '10px', 'width': '100%'}),
            
            # Data buttons row
            html.Div([
                html.Button('Load Data', id=self.Ids.load_data_btn(component_id), n_clicks=0,
                           style={'width': '75%', 'marginRight': '5px'},
                           title='Load experimental data.'),
                html.Button('Empty Data', id=self.Ids.empty_data_btn(component_id), n_clicks=0,
                           style={'width': '25%'},
                           title='Empties the loaded experimental data to free memory.')
            ], style={'display': 'flex', 'marginBottom': '10px', 'width': '100%'}),
            
            # Output/Status div
            html.Div(id=self.Ids.output_status(component_id), children="", 
                    hidden=not self.config.info_area.is_visible, 
                    style=self.config.info_area.style)
        ]

        # Call parent constructor
        super().__init__(gui_elements, style={'padding': '20px', 'maxWidth': '1200px', 'margin': '0 auto'}, **kwargs)

        # Setup callbacks
        self._setup_callbacks()

    def _setup_callbacks(self):
        """Setup all Dash callbacks for this component"""
        
        # Main callback for grid updates and button actions
        @callback(
            [Output(self.Ids.experiment_grid(self.component_id), "rowData"),
             Output(self.Ids.output_status(self.component_id), "children"),
             Output(self.Ids.experiment_grid(self.component_id), "selectedRows")],
            [Input(self.Ids.move_up_btn(self.component_id), "n_clicks"),
             Input(self.Ids.move_down_btn(self.component_id), "n_clicks"),
             Input(self.Ids.sort_by_id_btn(self.component_id), "n_clicks"),
             Input(self.Ids.update_descriptions_btn(self.component_id), "n_clicks"),
             Input(self.Ids.reset_descriptions_btn(self.component_id), "n_clicks"),
             Input(self.Ids.load_data_btn(self.component_id), "n_clicks"),
             Input(self.Ids.empty_data_btn(self.component_id), "n_clicks")],
            [State(self.Ids.experiment_grid(self.component_id), "selectedRows"),
             State(self.Ids.experiment_grid(self.component_id), "rowData")]
        )
        def handle_button_clicks(move_up_clicks, move_down_clicks, sort_clicks, 
                                update_clicks, reset_clicks, load_clicks, empty_clicks,
                                selected_rows, current_data):
            
            if not callback_context.triggered:
                return current_data, "", []
            
            # Get which button was clicked
            button_id = callback_context.triggered[0]['prop_id'].split('.')[0]
            
            try:
                if button_id == self.Ids.move_up_btn(self.component_id):
                    result = self._handle_move_up(selected_rows, current_data)
                    return result[0], result[1], result[2] if len(result) > 2 else []
                elif button_id == self.Ids.move_down_btn(self.component_id):
                    result = self._handle_move_down(selected_rows, current_data)
                    return result[0], result[1], result[2] if len(result) > 2 else []
                elif button_id == self.Ids.sort_by_id_btn(self.component_id):
                    result = self._handle_sort_by_id(current_data)
                    return result[0], result[1], []
                elif button_id == self.Ids.update_descriptions_btn(self.component_id):
                    result = self._handle_update_descriptions(is_reset=False)
                    return result[0], result[1], []
                elif button_id == self.Ids.reset_descriptions_btn(self.component_id):
                    result = self._handle_update_descriptions(is_reset=True)
                    return result[0], result[1], []
                elif button_id == self.Ids.load_data_btn(self.component_id):
                    result = self._handle_load_data(current_data)
                    return result[0], result[1], []
                elif button_id == self.Ids.empty_data_btn(self.component_id):
                    result = self._handle_empty_data(current_data)
                    return result[0], result[1], []
                else:
                    return current_data, "", []
                    
            except Exception as e:
                return current_data, f"❌ Error: {str(e)}", []

        # Callback for cell edits
        @callback(
            Output(self.Ids.output_status(self.component_id), "children", allow_duplicate=True),
            Input(self.Ids.experiment_grid(self.component_id), "cellValueChanged"),
            prevent_initial_call=True
        )
        def handle_cell_edit(cell_data):
            if cell_data:
                try:
                    # Update experiment descriptions based on cell edit
                    self._update_experiment_description_from_cell_edit(cell_data)
                    return f"✅ Updated {cell_data[0]['colId']} for experiment {cell_data[0]['rowId']}"
                except Exception as e:
                    return f"❌ Error updating cell: {type(e).__name__} - {str(e)}"
            return no_update

    def _create_dataframe(self):
        """Create dataframe from experiment descriptions"""
        if not self.experiment_descriptions:
            return pd.DataFrame()
            
        df = pd.DataFrame()
        # Direct mapping since column names match experiment description field names
        for field_name in ['id', 'order', 'is_load_data', 'short_name', 'name', 'description', 'directory']:
            df[field_name] = [descr[field_name] for descr in self.experiment_descriptions.values()]
        
        return df

    def _handle_move_up(self, selected_rows, current_data):
        """Handle move up button click"""
        if not selected_rows:
            return current_data, "❌ No rows selected.", []
        
        # Logic for moving rows up - adapted from dash_test.py
        # Create a copy to avoid mutating original
        updated_rows = current_data.copy()
        
        # Get the experiment_ids of selected rows for identification
        selected_exp_ids = {row["id"] for row in selected_rows}
        
        # Sort all rows by their current order to work with the sequence
        all_rows_sorted = sorted(updated_rows, key=lambda x: x["order"])
        
        # Create a list to track which rows are selected at each position
        selected_positions = []
        for i, row in enumerate(all_rows_sorted):
            if row["id"] in selected_exp_ids:
                selected_positions.append(i)
        
        # Filter out positions that can actually move up (position > 0)
        movable_positions = [pos for pos in selected_positions if pos > 0]
        
        if not movable_positions:
            return current_data, "❌ Cannot move up: no selected rows can move higher.", selected_rows
        
        # Create the new arrangement
        new_arrangement = all_rows_sorted.copy()
        
        # For each movable position, swap with the position above it
        for pos in sorted(movable_positions):
            # Swap the selected row at position 'pos' with the row at position 'pos-1'
            new_arrangement[pos], new_arrangement[pos-1] = new_arrangement[pos-1], new_arrangement[pos]
        
        # Update the order field to match the new positions
        for i, row in enumerate(new_arrangement):
            row["order"] = i
            # Update experiment descriptions
            exp_id = row["id"]
            if exp_id in self.experiment_descriptions:
                self.experiment_descriptions[exp_id]['order'] = i
        
        # Create summary message
        moved_count = len(movable_positions)
        total_selected = len(selected_positions)
        unmoved_count = total_selected - moved_count
        
        message = f"✅ Moved {moved_count} selected row(s) up by 1 position."
        if unmoved_count > 0:
            message += f" {unmoved_count} selected row(s) stayed at position 0."
        
        # Find the new selection (rows with the same experiment IDs)
        new_selection = [row for row in new_arrangement if row["id"] in selected_exp_ids]
        
        self._call_experiment_descriptions_updated_event()
        return new_arrangement, message, new_selection

    def _handle_move_down(self, selected_rows, current_data):
        """Handle move down button click"""
        if not selected_rows:
            return current_data, "❌ No rows selected.", []
        
        # Logic for moving rows down - adapted from dash_test.py
        # Create a copy to avoid mutating original
        updated_rows = current_data.copy()
        
        # Get the experiment_ids of selected rows for identification
        selected_exp_ids = {row["id"] for row in selected_rows}
        
        # Sort all rows by their current order to work with the sequence
        all_rows_sorted = sorted(updated_rows, key=lambda x: x["order"])
        max_order = len(all_rows_sorted) - 1
        
        # Create a list to track which rows are selected at each position
        selected_positions = []
        for i, row in enumerate(all_rows_sorted):
            if row["id"] in selected_exp_ids:
                selected_positions.append(i)
        
        # Filter out positions that can actually move down (position < max_order)
        movable_positions = [pos for pos in selected_positions if pos < max_order]
        
        if not movable_positions:
            return current_data, "❌ Cannot move down: no selected rows can move lower.", selected_rows
        
        # Create the new arrangement
        new_arrangement = all_rows_sorted.copy()
        
        # For each movable position, swap with the position below it
        # Process in reverse order to avoid conflicts
        for pos in sorted(movable_positions, reverse=True):
            # Swap the selected row at position 'pos' with the row at position 'pos+1'
            new_arrangement[pos], new_arrangement[pos+1] = new_arrangement[pos+1], new_arrangement[pos]
        
        # Update the order field to match the new positions
        for i, row in enumerate(new_arrangement):
            row["order"] = i
            # Update experiment descriptions
            exp_id = row["id"]
            if exp_id in self.experiment_descriptions:
                self.experiment_descriptions[exp_id]['order'] = i
        
        # Create summary message
        moved_count = len(movable_positions)
        total_selected = len(selected_positions)
        unmoved_count = total_selected - moved_count
        
        message = f"✅ Moved {moved_count} selected row(s) down by 1 position."
        if unmoved_count > 0:
            message += f" {unmoved_count} selected row(s) stayed at bottom position."
        
        # Find the new selection (rows with the same experiment IDs)
        new_selection = [row for row in new_arrangement if row["id"] in selected_exp_ids]
        
        self._call_experiment_descriptions_updated_event()
        return new_arrangement, message, new_selection

    def _handle_sort_by_id(self, current_data):
        """Handle sort by ID button click"""
        try:
            # Sort experiments according to ids
            sorted_existing_experiment_ids = sorted(list(self.experiment_descriptions.keys()))
            
            # Update the order of the experiments according to the sorted list
            for order, exp_id in enumerate(sorted_existing_experiment_ids):
                self.experiment_descriptions[exp_id]['order'] = order
            
            # Create new dataframe
            new_data = self._create_dataframe().to_dict("records")
            
            self._call_experiment_descriptions_updated_event()
            return new_data, "✅ Sorted experiments by ID."
            
        except Exception as e:
            return current_data, f"❌ Error sorting: {str(e)}"

    def _handle_update_descriptions(self, is_reset=False):
        """Handle update/reset descriptions button click"""
        try:
            self.update_experiment_descriptions(is_reset=is_reset)
            new_data = self._create_dataframe().to_dict("records")
            action = "Reset" if is_reset else "Updated"
            return new_data, f"✅ {action} experiment descriptions."
        except Exception as e:
            return no_update, f"❌ Error updating descriptions: {str(e)}"

    def _handle_load_data(self, current_data):
        """Handle load data button click"""
        try:
            self.load_data()
            return current_data, "✅ Data successfully loaded."
        except Exception as e:
            return current_data, f"❌ Error loading data: {str(e)}"

    def _handle_empty_data(self, current_data):
        """Handle empty data button click"""
        try:
            self.empty_data()
            return current_data, "✅ Data emptied to free memory."
        except Exception as e:
            return current_data, f"❌ Error emptying data: {str(e)}"

    def _update_experiment_description_from_cell_edit(self, cell_data):
        """Update experiment descriptions when a cell is edited"""
        for cell in cell_data:
            exp_id = cell['data']['id']
           
            # Direct assignment since column names match experiment description field names
            if exp_id in self.experiment_descriptions:
                col_id = cell['colId']
                self.experiment_descriptions[exp_id][col_id] = cell['value']
        
        self._call_experiment_descriptions_updated_event()

    def on_experiment_descriptions_updated(self, handler):
        """Register an event handler for when experiment descriptions are updated"""
        self._on_experiment_descriptions_updated_event_handlers.append(handler)

    def _call_experiment_descriptions_updated_event(self):
        """Call all registered experiment descriptions updated event handlers"""
        for handler in self._on_experiment_descriptions_updated_event_handlers:
            handler(eu.AttrDict(
                name='experiment_descriptions_updated',
                new=self.experiment_descriptions,
                owner=self,
                type='change'))

    def on_experiment_data_loaded(self, handler):
        """Register an event handler for when experiment data is loaded"""
        self._on_experiment_data_loaded_event_handlers.append(handler)

    def _call_experiment_data_loaded_event(self):
        """Call all registered experiment data loaded event handlers"""
        for handler in self._on_experiment_data_loaded_event_handlers:
            handler(eu.AttrDict(
                name='data_loaded',
                new=self.experiment_data,
                owner=self,
                type='change'))

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

            # remove non-existing elements from existing descriptions
            deleted_experiments = set(self.experiment_descriptions.keys()).difference(set(new_exp_descr.keys()))
            for deleted_exp in deleted_experiments:
                del self.experiment_descriptions[deleted_exp]

            # keep current order and add new experiments at the end of the list
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
                self.experiment_descriptions[exp_id]['order'] = order

            # do not keep the repetition ids from existing ones, but use the ones from the new descriptions
            # otherwise, if new repetitions are added, they will not be used
            for new_descr in new_exp_descr.values():
                self.experiment_descriptions[new_descr['id']]['repetition_ids'] = new_descr['repetition_ids']

        self._call_experiment_descriptions_updated_event()

    def empty_data(self):
        """Delete experiment_data to free memory"""
        if self.experiment_data:
            keys = list(self.experiment_data.keys())
            for key in keys:
                del self.experiment_data[key]

    def load_data(self):
        """Loads the experiment data.
        
        Can be called directly after initialization to preload the data without needing user input.
        """
        
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


class ExperimentDataLoaderWidget:
    """
    Jupyter widget wrapper for the ExperimentDataLoaderComponent that can be displayed inline in Jupyter notebooks.
    
    This class creates a Dash app containing the ExperimentDataLoaderComponent and provides a simple interface
    for use in Jupyter notebooks with support for inline display.
    
    Example:
        ```python
        import exputils as eu
        
        exp_data_loader = eu.gui.dash.ExperimentDataLoaderWidget(
            load_experiment_descriptions_function=dummy_load_descriptions,
            load_experiment_data_function=dummy_load_data
        )
        
        # register events
        exp_data_loader.on_experiment_data_loaded(on_experiment_data_loaded_handler)
        exp_data_loader.on_experiment_descriptions_updated(on_experiment_descriptions_updated_handler)
        
        display(exp_data_loader)
        ```
    """

    def default_config():
        """Generates the default configuration for the widget.

        Returns:
            dict: A dictionary containing default configurations for various components.
        """
        return ExperimentDataLoader.default_config()
    
    def __init__(self, config=None, load_experiment_descriptions_function=None, load_experiment_data_function=None, **kwargs):
        # Create the Dash app
        self.app = Dash(__name__, **kwargs)
        
        # Create the component
        self.component = ExperimentDataLoader(
            config=config,
            load_experiment_descriptions_function=load_experiment_descriptions_function,
            load_experiment_data_function=load_experiment_data_function
        )
        
        # Set the app layout to contain the component
        self.app.layout = html.Div([self.component])
        
        # Proxy important attributes and methods
        self.experiment_descriptions = self.component.experiment_descriptions
        self.experiment_data = self.component.experiment_data
    
    @property
    def experiment_descriptions(self):
        """Get experiment descriptions from the component"""
        return self.component.experiment_descriptions
    
    @experiment_descriptions.setter
    def experiment_descriptions(self, value):
        """Set experiment descriptions on the component"""
        self.component.experiment_descriptions = value
    
    @property
    def experiment_data(self):
        """Get experiment data from the component"""
        return self.component.experiment_data
    
    @experiment_data.setter
    def experiment_data(self, value):
        """Set experiment data on the component"""
        self.component.experiment_data = value
    
    def on_experiment_descriptions_updated(self, handler):
        """Register an event handler for when experiment descriptions are updated"""
        self.component.on_experiment_descriptions_updated(handler)
    
    def on_experiment_data_loaded(self, handler):
        """Register an event handler for when experiment data is loaded"""
        self.component.on_experiment_data_loaded(handler)
    
    def update_experiment_descriptions(self, is_reset=False):
        """Updates the experiment descriptions by adding new experiments and removing old experiments."""
        self.component.update_experiment_descriptions(is_reset=is_reset)
    
    def load_data(self):
        """Loads the experiment data."""
        self.component.load_data()
    
    def empty_data(self):
        """Delete experiment_data to free memory"""
        self.component.empty_data()
    
    def _repr_html_(self):
        """
        Jupyter notebook display representation.
        This method is called when the widget is displayed in a Jupyter notebook.
        """

        import socket

        # Check if port is already in use
        def is_port_in_use(port):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                return s.connect_ex(('localhost', port)) == 0

        port = 8050
        while is_port_in_use(port):
            port += 1

        self.app.run(mode='inline', port=port)
