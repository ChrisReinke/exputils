import exputils

if __name__ == '__main__':

    # define the statistics that should be computed
    statistics = [('value', exputils.stat.collect_1D_values),
                  ('step', exputils.stat.collect_counters),
                  ]

    # compute the statistics
    exputils.stat.calc_statistics_over_repetitions(statistics,
                                                   recalculate_statistics=True,
                                                   verbose=True)


