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


class BaseWidget:

    @staticmethod
    def default_config():

        dc = eu.AttrDict()

        dc.is_use_state_backup = True
        dc.state_backup_name = None
        
        dc.state_backup_variable_filter = None

        return dc


    def __init__(self, config=None, **kwargs):
        self.config = eu.combine_dicts(kwargs, config, self.default_config())


    @property
    def state_backup_name(self):
        state_backup_name = self.config.state_backup_name
        if state_backup_name is None:
            state_backup_name = type(self).__name__ + '_state_backup'
        return state_backup_name


    @state_backup_name.setter
    def state_backup_name(self, state_backup_name):
        self.config.backup_name = state_backup_name


    def get_widget_state(self):
        return eu.AttrDict()


    def set_widget_state(self, state):
        pass


    def backup_state(self):
        if self.config.is_use_state_backup:
            state_backup = self.get_widget_state()
            state_backup = self._filter_state(state_backup)
            eu.gui.jupyter.save_config(state_backup, self.state_backup_name)


    def load_state_backup(self):
        if self.config.is_use_state_backup:
            state_backup = eu.gui.jupyter.load_config(self.state_backup_name)
            if state_backup:
                state_backup = self._filter_state(state_backup)
                self.set_widget_state(state_backup)
                
                
    def _filter_state(self, state):
        
        if self.config.state_backup_variable_filter is None:
            filtered_state = state
        else:
            filtered_state = eu.AttrDict()
            
            state_backup_variable_filter = self.config.state_backup_variable_filter
            if not isinstance(state_backup_variable_filter, list):
                state_backup_variable_filter = [state_backup_variable_filter]

            for variable_name in state_backup_variable_filter:
                if variable_name in state:
                    filtered_state[variable_name] = state[variable_name]
            
        return filtered_state
            
