import random
import numpy as np
import exputils as eu
#import torch

def test_seed():

    # set seed directly
    eu.misc.seed(2)
    val_random = random.randint(0,10000)
    val_numpy = np.random.randint(10000)
    #val_torch = torch.randint(0,10000, (1, ))

    eu.misc.seed(2)
    assert val_random == random.randint(0,10000)
    assert val_numpy == np.random.randint(10000)
    #assert val_torch == torch.randint(0,10000, (1, ))

    # set seed via configuration dict
    config = dict(seed=3)
    eu.misc.seed(config)
    val_random = random.randint(0,10000)
    val_numpy = np.random.randint(10000)
    #val_torch = torch.randint(0,10000, (1, ))

    eu.misc.seed(config)
    assert val_random == random.randint(0,10000)
    assert val_numpy == np.random.randint(10000)
    #assert val_torch == torch.randint(0,10000, (1, ))