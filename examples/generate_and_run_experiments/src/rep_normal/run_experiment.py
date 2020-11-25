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
        val += config['force'] + np.random.normal(0.0, config['sigma'])

    # save the values
    if not os.path.isdir(config['results_directory']):
        os.makedirs(config['results_directory'])
    np.save(os.path.join(config['results_directory'], 'values.npy'), values)

if __name__ == '__main__':

    config = experiment_config.get_config()

    run(**config)
