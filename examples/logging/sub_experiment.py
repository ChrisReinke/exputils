import exputils.data.logging as log
import numpy as np

def run_subexperiment():

    n_steps = 4

    for step in range(n_steps):
        log.add_value('step', step)
        log.add_value('random', np.random.rand())






