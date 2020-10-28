import exputils
import os
import glob
import numpy as np


def calc_value_stats(data):

    n_reps = np.max(list(data.keys())) + 1
    n_steps = data[n_reps-1]['values'].shape[0]

    values = np.full((n_reps, n_steps), np.nan)
    for rep_id, rep_data in data.items():
        values[rep_id, :] = rep_data['values']

    stats = dict()
    stats['data'] = values
    stats['means'] = np.nanmean(values, axis=0)
    stats['stds'] = np.nanstd(values, axis=0)

    return stats


def load_data(repetition_directories):

    data = dict()

    for repetition_directory in sorted(repetition_directories):

        # get id of the repetition from its foldername
        numbers_in_string = [int(s) for s in os.path.basename(repetition_directory).split('_') if s.isdigit()]
        repetition_id = numbers_in_string[0]

        data[repetition_id] = dict()

        # load all npy files in the given directory
        npy_file_list = [f for f in glob.glob(os.path.join(repetition_directory, 'results', '*.npy'))]

        for npy_file in npy_file_list:
            data_name = os.path.splitext(os.path.basename(npy_file))[0]
            data[repetition_id][data_name] = np.load(npy_file)

    return data


if __name__ == '__main__':

    experiments = '.'

    statistics = [('values', calc_value_stats),
                  ]

    exputils.calc_statistics_over_repetitions(statistics, load_data, experiments, recalculate_statistics=True, verbose=True)


