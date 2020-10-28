import numpy as np
import os
import experiment_config


def run(**config):

    # set random seed
    np.random.seed(config['seed'])

    # do random walk
    values = np.empty(config['n_steps'])

    val = config['init_value']
    for step in range(config['n_steps']):
        values[step] = val
        direction = -1.0 if np.random.randint(2) == 0 else 1.0
        val += config['force'] + direction * np.random.standard_gamma(config['shape'])

    # save the values
    if not os.path.isdir(config['results_directory']):
        os.makedirs(config['results_directory'])
    np.save(os.path.join(config['results_directory'], 'values.npy'), values)

if __name__ == '__main__':

    config = experiment_config.get_config()

    run(**config)
