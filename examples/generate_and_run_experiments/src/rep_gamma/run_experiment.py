import numpy as np
from exputils.logging import log
import experiment_config


def run(**config):

    # set random seed
    np.random.seed(config['seed'])

    # do random walk
    val = config['init_value']

    log.add_value('step', 0)
    log.add_value('value', val)

    for step in range(config['n_steps']):
        direction = -1.0 if np.random.randint(2) == 0 else 1.0
        val += config['force'] + direction * np.random.standard_gamma(config['shape'])

        log.add_value('step', step + 1)
        log.add_value('value', val)

    # save log
    log.save()


if __name__ == '__main__':

    config = experiment_config.get_config()

    run(**config)