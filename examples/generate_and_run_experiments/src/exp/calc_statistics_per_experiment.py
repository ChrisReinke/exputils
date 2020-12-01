import exputils as eu
import numpy as np

def calc_value_regret(statistic_name, data):
    '''Calculates the regret over all repetitions, i.e. value - max(value).'''

    # create numpy array that can hold all repetition data
    n_repetitions = np.max(list(data.keys())) + 1
    n_values = np.max([len(d['value']) for d in data.values()])
    rep_value = np.full((n_repetitions, n_values), np.nan)

    # collect values data
    for rep_id, rep_data in data.items():
        rep_value[rep_id, :] = rep_data['value']

    # calc regret
    return rep_value - np.nanmax(rep_value)


if __name__ == '__main__':

    # define the statistics that should be computed
    statistics = [('value_regret', calc_value_regret),
                  ]

    # compute the statistics
    eu.data.calc_statistics_over_repetitions(
        statistics,
        recalculate_statistics=True,
        verbose=True)