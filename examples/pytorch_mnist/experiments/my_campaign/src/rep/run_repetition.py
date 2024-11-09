#!/usr/bin/env python

import my_dl_lib
import torch

# read the config for this repetition from the config.py file
from config import config

# this allows to run processes in parallel on different cores without slowing down the processing
# because each of them wants to use all cores
torch.set_num_threads(1)

# run the traning with the associated configuration for this repetition
my_dl_lib.run_training(config=config)
