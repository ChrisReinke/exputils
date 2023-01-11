##
## This file is part of the exputils package.
##
## Copyright: INRIA
## Year: 2022, 2023
## Contact: chris.reinke@inria.fr
##
## exputils is provided under GPL-3.0-or-later
##
from exputils.gui.jupyter.multi_selection_widget import MultiSelectionWidget
import exputils as eu
import numpy as np

class RepetitionIDsSelectionWidget(MultiSelectionWidget):
    """
    MultiSelectionWidget to select experiment ids in a experiment_data dict.
    """

    @staticmethod
    def default_config():
        dc = eu.gui.jupyter.MultiSelectionWidget.default_config()

        # if true, returns 'all' for selected_experiment_ids property if all repetitions
        # are selected instead of a list of all repetition ids
        dc.is_return_all_string = True

        # defines if an extra choice called none is given
        dc.is_select_non_choice = True

        return dc

    def __init__(self, experiment_data, experiment_descriptions=None, config=None, **kwargs):
        self.config = eu.combine_dicts(kwargs, config, self.default_config())

        # get experiment ids
        self.repetition_ids = []

        # choice strings that are displayed to the user, can include ids, name, short_name, ...
        all_repetition_ids = []

        # only extract ids automatically, if an experiment description is given
        if experiment_descriptions is not None:
            for exp_descr in experiment_descriptions.values():
                if 'repetition_ids' in exp_descr:
                    all_repetition_ids += exp_descr['repetition_ids']

        repetition_ids = np.unique(all_repetition_ids).tolist()

        super().__init__(choices=repetition_ids, **self.config)


    @property
    def selected_repetition_ids(self):

        if self.config.is_return_all_string and self.config.is_select_all_choice and self.select_all_checkbox.value == True:
            return 'all'
        else:
            return self.selected_choices


    @selected_repetition_ids.setter
    def selected_repetition_ids(self, selected_repetition_ids):
        self.selected_choices = selected_repetition_ids