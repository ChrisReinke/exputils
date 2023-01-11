##
## This file is part of the exputils package.
##
## Copyright: INRIA
## Year: 2022, 2023
## Contact: chris.reinke@inria.fr
##
## exputils is provided under GPL-3.0-or-later
##
from exputils.gui.jupyter.experiment_data_loader_widget import ExperimentDataLoaderWidget
from exputils.gui.jupyter.multi_selection_widget import MultiSelectionWidget
from exputils.gui.jupyter.experiment_ids_selection_widget import ExperimentIDsSelectionWidget
from exputils.gui.jupyter.repetition_ids_selection_widget import RepetitionIDsSelectionWidget
from exputils.gui.jupyter.experiment_data_selection_widget import ExperimentDataSelectionWidget
from exputils.gui.jupyter.experiment_data_plot_selection_widget import ExperimentDataPlotSelectionWidget
from exputils.gui.jupyter.text_selection_accordion_widget import TextSelectionAccordionWidget
from exputils.gui.jupyter.base_widget import BaseWidget

from exputils.gui.jupyter.plotly_meanstd_scatter import plotly_meanstd_scatter
from exputils.gui.jupyter.plotly_meanstd_bar import plotly_meanstd_bar
from exputils.gui.jupyter.plotly_box import plotly_box
from exputils.gui.jupyter.tabulate_meanstd import tabulate_meanstd
from exputils.gui.jupyter.tabulate_pairwise import tabulate_pairwise

from exputils.gui.jupyter.misc import create_new_cell
from exputils.gui.jupyter.misc import save_config
from exputils.gui.jupyter.misc import load_config
from exputils.gui.jupyter.misc import add_children_to_widget
from exputils.gui.jupyter.misc import remove_children_from_widget
from exputils.gui.jupyter.misc import set_children_of_widget
from exputils.gui.jupyter.misc import generate_random_state_backup_name

from exputils.gui.jupyter.ipynbname import get_notebook_name
from exputils.gui.jupyter.ipynbname import get_notebook_path

DEFAULT_CONFIG_DIRECTORY = '.ipython_config'

# TODO: Refactor - create plotly plots as objects
# TODO: Feature - create table widget that shows statistical significant difference measures for same data that is given to bar or box plots