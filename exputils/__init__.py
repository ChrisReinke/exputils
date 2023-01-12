##
## This file is part of the exputils package.
##
## Copyright: INRIA
## Year: 2022, 2023
## Contact: chris.reinke@inria.fr
##
## exputils is provided under GPL-3.0-or-later
##
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

from exputils.misc import update_status

__version__ = '0.3.3'

DEFAULT_ODS_CONFIGURATION_FILE = 'experiment_configurations.ods'
DEFAULT_EXPERIMENTS_DIRECTORY = 'experiments'
EXPERIMENT_DIRECTORY_TEMPLATE = 'experiment_{:06d}'
REPETITION_DIRECTORY_TEMPLATE = 'repetition_{:06d}'
DEFAULT_DATA_DIRECTORY = 'data'  # name of the data directory under the experiments and repetition folders

REPETITION_DATA_KEY = 'repetition_data'  # key name  for repetition data in the experiment_data dictionary
