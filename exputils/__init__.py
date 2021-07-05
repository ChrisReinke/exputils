import exputils.data
import exputils.gui
import exputils.io
import exputils.manage
import exputils.misc

from exputils.misc.attrdict import AttrDict
from exputils.misc.attrdict import AutoAttrDict
from exputils.misc.attrdict import DefaultAttrDict
from exputils.misc.attrdict import DefaultFactoryAttrDict
from exputils.misc.attrdict import combine_dicts

__version__ = '0.2.12'

DEFAULT_ODS_CONFIGURATION_FILE = 'experiment_configurations.ods'
DEFAULT_EXPERIMENTS_DIRECTORY = 'experiments'
EXPERIMENT_DIRECTORY_TEMPLATE = 'experiment_{:06d}'
REPETITION_DIRECTORY_TEMPLATE = 'repetition_{:06d}'
DEFAULT_DATA_DIRECTORY = 'data' # name of the data directory under the experiments and repetition folders

REPETITION_DATA_KEY = 'repetition_data' # key name  for repetition data in the experiment_data dictionary

# TODO: add command scripts to the project here (see transfer_rl project)
# TODO: add commands script to execute repetitions that stores the status file automatically, so that no run_experiment.sh is necessary
# TODO: write command script to view progress of running experiment
# TODO: allow pull_data and push_code commands to operate only on the current experiment directory
