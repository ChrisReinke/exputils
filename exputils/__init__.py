import exputils.run
import exputils.misc
import exputils.logging
import exputils.io
import exputils.stat
import exputils.gui
from exputils.attrdict import AttrDict
from exputils.attrdict import AutoAttrDict
from exputils.attrdict import DefaultAttrDict
from exputils.attrdict import DefaultFactoryAttrDict
from exputils.attrdict import combine_dicts

__version__ = '0.2.0'

EXPERIMENT_DIRECTORY_TEMPLATE = 'experiment_{:06d}'
REPETITION_DIRECTORY_TEMPLATE = 'repetition_{:06d}'
DEFAULT_EXPERIMENTS_DIRECTORY = 'experiments'
DEFAULT_STATISTICS_DIRECTORY = 'statistics'
DEFAULT_LOGS_DIRECTORY = 'logs'
DEFAULT_ODS_CONFIGURATION_FILE = 'experiment_configurations.ods'