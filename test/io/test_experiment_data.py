import numpy as np
import exputils as eu


def test_get_data():

    experiment_data = {
        'exp0': {'sub_dict_1': {'values': np.array([[10, 11, 12, 13], [20, 21, 22, 23]]),
                                'no_rep_stat': np.array([10, 20, 30]),
                                'scalar_stat': 1.0},
                 'sub_dict_2': {'values': np.array([[30, 31, 32, 33], [40, 41, 42, 43]]),
                                'no_rep_stat': np.array([110, 120, 130]),
                                'scalar_stat': 2.0}},
        'exp1': {'sub_dict_1': {'values': np.array([[110, 111, 112, 113], [120, 121, 122, 123]]),
                                'no_rep_stat': np.array([210, 220, 230]),
                                'scalar_stat': 3.0},
                 'sub_dict_2': {'values': np.array([[130, 131, 132, 133], [140, 141, 142, 143]]),
                                'no_rep_stat': np.array([30, 320, 330]),
                                'scalar_stat': 4.0}}}

    experiment_descriptions = {
        'exp0': {'id': 'exp0', 'name': 'Experiment 0', 'is_load_data': True, 'directory': 'path\to\exp0',
                 'short_name': 'e0', 'description': 'descr0'},
        'exp1': {'id': 'exp1', 'name': 'Experiment 1', 'is_load_data': True, 'directory': 'path\to\exp1',
                 'short_name': 'e1', 'description': 'descr1'}}

    # single experiment
    data, _ = eu.io.get_experiment_data(experiment_data,
                                        datasources='sub_dict_1.values',
                                        experiment_ids='exp0')
    target_data = [[experiment_data['exp0']['sub_dict_1']['values']]]
    eu.misc.list_equal(data, target_data)


    # several experiments
    data, _ = eu.io.get_experiment_data(experiment_data,
                                        datasources='sub_dict_1.values',
                                        experiment_ids=['exp0', 'exp1'])
    target_data = [[experiment_data['exp0']['sub_dict_1']['values'],
                    experiment_data['exp1']['sub_dict_1']['values']]]
    eu.misc.list_equal(data, target_data)


    # all experiments
    data, _ = eu.io.get_experiment_data(experiment_data,
                                        datasources='sub_dict_1.values',
                                        experiment_ids='all')
    target_data = [[experiment_data['exp0']['sub_dict_1']['values'],
                    experiment_data['exp1']['sub_dict_1']['values']]]
    eu.misc.list_equal(data, target_data)


    # several data sources
    data, _ = eu.io.get_experiment_data(experiment_data,
                                        datasources=['sub_dict_1.values', 'sub_dict_2.values'],
                                        experiment_ids='all')
    target_data = [[experiment_data['exp0']['sub_dict_1']['values'],
                    experiment_data['exp1']['sub_dict_1']['values']],
                   [experiment_data['exp0']['sub_dict_2']['values'],
                    experiment_data['exp1']['sub_dict_2']['values']]
                   ]
    eu.misc.list_equal(data, target_data)


    # sub indexes
    data, _ = eu.io.get_experiment_data(experiment_data,
                                        datasources=['sub_dict_1.values', 'sub_dict_2.values[:,-1]'],
                                        experiment_ids='all',
                                        repetition_ids='all')
    target_data = [[experiment_data['exp0']['sub_dict_1']['values'],
                    experiment_data['exp1']['sub_dict_1']['values']],
                   [experiment_data['exp0']['sub_dict_2']['values'][:, -1],
                    experiment_data['exp1']['sub_dict_2']['values'][:, -1]]
                   ]
    assert eu.misc.list_equal(data, target_data)

    # sub indexes for numpy
    data, _ = eu.io.get_experiment_data(experiment_data,
                                        datasources=['sub_dict_1.values', 'sub_dict_2.values[:,[2,3]]'],
                                        experiment_ids='all',
                                        repetition_ids='all')
    target_data = [[experiment_data['exp0']['sub_dict_1']['values'],
                    experiment_data['exp1']['sub_dict_1']['values']],
                   [experiment_data['exp0']['sub_dict_2']['values'][:, [2,3]],
                    experiment_data['exp1']['sub_dict_2']['values'][:, [2,3]]]
                   ]
    assert eu.misc.list_equal(data, target_data)

    # filter repetitions
    data, _ = eu.io.get_experiment_data(experiment_data,
                                        datasources='sub_dict_1.values',
                                        experiment_ids='all',
                                        repetition_ids=[1])
    target_data = [[experiment_data['exp0']['sub_dict_1']['values'][[1]],
                    experiment_data['exp1']['sub_dict_1']['values'][[1]]]]
    assert eu.misc.list_equal(data, target_data)

    data, _ = eu.io.get_experiment_data(experiment_data,
                                        datasources='sub_dict_1.values',
                                        experiment_ids='all',
                                        repetition_ids=[1, 0])
    target_data = [[experiment_data['exp0']['sub_dict_1']['values'][[1, 0]],
                    experiment_data['exp1']['sub_dict_1']['values'][[1, 0 ]]]]
    assert eu.misc.list_equal(data, target_data)

    data, _ = eu.io.get_experiment_data(experiment_data,
                                        datasources='sub_dict_1.values',
                                        experiment_ids='exp0',
                                        repetition_ids=[1, 0])
    target_data = [[experiment_data['exp0']['sub_dict_1']['values'][[1, 0]]]]
    assert eu.misc.list_equal(data, target_data)

    data, _ = eu.io.get_experiment_data(experiment_data,
                                        datasources='sub_dict_1.values[:, -1]',
                                        experiment_ids='exp0',
                                        repetition_ids=[1])
    target_data = [[experiment_data['exp0']['sub_dict_1']['values'][[1],-1]]]
    assert eu.misc.list_equal(data, target_data)


    ##################################
    # EXPERIMENT DESCRIPTION
    data, labels = eu.io.get_experiment_data(experiment_data,
                                             experiment_descriptions=experiment_descriptions,
                                             datasources='sub_dict_1.values',
                                             experiment_ids='exp0')
    target_data = [[experiment_data['exp0']['sub_dict_1']['values']]]
    eu.misc.list_equal(data, target_data)

    target_labels = [('sub_dict_1.values', ['Experiment 0'])]
    eu.misc.list_equal(labels, target_labels)


    data, labels = eu.io.get_experiment_data(experiment_data,
                                             experiment_descriptions=experiment_descriptions,
                                             datasources=['sub_dict_1.values', 'sub_dict_2.values'])
    target_data = [[experiment_data['exp0']['sub_dict_1']['values'],
                    experiment_data['exp1']['sub_dict_1']['values']],
                   [experiment_data['exp0']['sub_dict_2']['values'],
                    experiment_data['exp1']['sub_dict_2']['values']]]

    eu.misc.list_equal(data, target_data)

    target_labels = [('sub_dict_1.values', ['Experiment 0', 'Experiment 1']),
                     ('sub_dict_2.values', ['Experiment 0', 'Experiment 1'])]
    eu.misc.list_equal(labels, target_labels)


    ######################################
    # NON REPETITION DATA

    # several experiments
    data, _ = eu.io.get_experiment_data(experiment_data,
                                        datasources='sub_dict_1.no_rep_stat',
                                        experiment_ids=['exp0', 'exp1'],
                                        repetition_ids='none')
    target_data = [[experiment_data['exp0']['sub_dict_1']['no_rep_stat'],
                    experiment_data['exp1']['sub_dict_1']['no_rep_stat']]]
    eu.misc.list_equal(data, target_data)

    data, _ = eu.io.get_experiment_data(experiment_data,
                                        datasources='sub_dict_1.scalar_stat',
                                        experiment_ids=['exp0', 'exp1'],
                                        repetition_ids='none')
    target_data = [[experiment_data['exp0']['sub_dict_1']['scalar_stat'],
                    experiment_data['exp1']['sub_dict_1']['scalar_stat']]]
    eu.misc.list_equal(data, target_data)
