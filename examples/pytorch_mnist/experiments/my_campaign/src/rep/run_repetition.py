#!/usr/bin/env python

# this allows to run processes in parallel on different cores without slowing down the processing
# because each of them wants to use all cores
import torch
torch.set_num_threads(1)

# read the config for this repetition from the config.py file
from config import config

# run the traning with the associated configuration for this repetition
import my_dl_lib
my_dl_lib.run_training(config=config)
