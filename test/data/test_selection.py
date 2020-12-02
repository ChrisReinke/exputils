import numpy as np
import exputils as eu


def create_test_data():

    experiment_data = {
        'exp0': {'repetition_data': [{'rep_values': np.array([45,46,47]),
                                      'rep_values_1': np.array([62,53]),
                                      'rep_values_2': np.array([56]),
                                      'rep_values_3': 456},
                                     {'rep_values': np.array([78,79,80]),
                                      'rep_values_1': np.array([75,15,56]),
                                      'rep_values_2': np.array([35]),
                                      'rep_values_3': 753}],
                 'sub_dict_1': {'values': np.array([[10, 11, 12, 13], [20, 21, 22, 23]]),
                                'no_rep_stat': np.array([10, 20, 30]),
                                'scalar_stat': 1.0},
                 'sub_dict_2': {'values': np.array([[30, 31, 32, 33], [40, 41, 42, 43]]),
                                'no_rep_stat': np.array([110, 120, 130]),
                                'scalar_stat': 2.0}},
        'exp1': {'repetition_data': [{'rep_values': np.array([87,88,89]),
                                      'rep_values_1': np.array([62,53,45]),
                                      'rep_values_2': np.array([65]),
                                      'rep_values_3': 657},
                                     {'rep_values': np.array([56,57,58]),
                                      'rep_values_1': np.array([86]),
                                      'rep_values_2': np.array([76]),
                                      'rep_values_3': 754}],
                 'sub_dict_1': {'values': np.array([[110, 111, 112, 113], [120, 121, 122, 123]]),
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

    return experiment_data, experiment_descriptions


def test_datasource_experimentid_repetitionid_filters():

    experiment_data, experiment_descriptions = create_test_data()

    #################################
    # Test the different filters

    # single experiment
    data, _ = eu.data.select_experiment_data(experiment_data,
                                        datasources='sub_dict_1.values',
                                        experiment_ids='exp0')
    target_data = [[experiment_data['exp0']['sub_dict_1']['values']]]
    eu.misc.list_equal(data, target_data)


    # several experiments
    data, _ = eu.data.select_experiment_data(experiment_data,
                                        datasources='sub_dict_1.values',
                                        experiment_ids=['exp0', 'exp1'])
    target_data = [[experiment_data['exp0']['sub_dict_1']['values'],
                    experiment_data['exp1']['sub_dict_1']['values']]]
    eu.misc.list_equal(data, target_data)


    # all experiments
    data, _ = eu.data.select_experiment_data(experiment_data,
                                        datasources='sub_dict_1.values',
                                        experiment_ids='all')
    target_data = [[experiment_data['exp0']['sub_dict_1']['values'],
                    experiment_data['exp1']['sub_dict_1']['values']]]
    eu.misc.list_equal(data, target_data)


    # several data sources
    data, _ = eu.data.select_experiment_data(experiment_data,
                                        datasources=['sub_dict_1.values', 'sub_dict_2.values'],
                                        experiment_ids='all')
    target_data = [[experiment_data['exp0']['sub_dict_1']['values'],
                    experiment_data['exp1']['sub_dict_1']['values']],
                   [experiment_data['exp0']['sub_dict_2']['values'],
                    experiment_data['exp1']['sub_dict_2']['values']]
                   ]
    eu.misc.list_equal(data, target_data)


    # sub indexes
    data, _ = eu.data.select_experiment_data(experiment_data,
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
    data, _ = eu.data.select_experiment_data(experiment_data,
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
    data, _ = eu.data.select_experiment_data(experiment_data,
                                        datasources='sub_dict_1.values',
                                        experiment_ids='all',
                                        repetition_ids=[1])
    target_data = [[experiment_data['exp0']['sub_dict_1']['values'][[1]],
                    experiment_data['exp1']['sub_dict_1']['values'][[1]]]]
    assert eu.misc.list_equal(data, target_data)

    data, _ = eu.data.select_experiment_data(experiment_data,
                                        datasources='sub_dict_1.values',
                                        experiment_ids='all',
                                        repetition_ids=[1, 0])
    target_data = [[experiment_data['exp0']['sub_dict_1']['values'][[1, 0]],
                    experiment_data['exp1']['sub_dict_1']['values'][[1, 0 ]]]]
    assert eu.misc.list_equal(data, target_data)

    data, _ = eu.data.select_experiment_data(experiment_data,
                                        datasources='sub_dict_1.values',
                                        experiment_ids='exp0',
                                        repetition_ids=[1, 0])
    target_data = [[experiment_data['exp0']['sub_dict_1']['values'][[1, 0]]]]
    assert eu.misc.list_equal(data, target_data)

    data, _ = eu.data.select_experiment_data(experiment_data,
                                        datasources='sub_dict_1.values[:, -1]',
                                        experiment_ids='exp0',
                                        repetition_ids=[1])
    target_data = [[experiment_data['exp0']['sub_dict_1']['values'][[1],-1]]]
    assert eu.misc.list_equal(data, target_data)


    ##################################
    # EXPERIMENT DESCRIPTION
    data, labels = eu.data.select_experiment_data(experiment_data,
                                             experiment_descriptions=experiment_descriptions,
                                             datasources='sub_dict_1.values',
                                             experiment_ids='exp0')
    target_data = [[experiment_data['exp0']['sub_dict_1']['values']]]
    eu.misc.list_equal(data, target_data)

    target_labels = [('sub_dict_1.values', [('Experiment 0', ['e0 - 0', 'e0 - 1'])])]
    assert eu.misc.list_equal(labels, target_labels)

    # only specific repetitions
    data, labels = eu.data.select_experiment_data(experiment_data,
                                             experiment_descriptions=experiment_descriptions,
                                             datasources='sub_dict_1.values',
                                             experiment_ids='exp0',
                                             repetition_ids=[1])
    target_data = [[experiment_data['exp0']['sub_dict_1']['values'][1]]]
    eu.misc.list_equal(data, target_data)

    target_labels = [('sub_dict_1.values', [('Experiment 0', ['e0 - 1'])])]
    assert eu.misc.list_equal(labels, target_labels)

    # several datasources and experiments
    data, labels = eu.data.select_experiment_data(experiment_data,
                                             experiment_descriptions=experiment_descriptions,
                                             datasources=['sub_dict_1.values', 'sub_dict_2.values'])
    target_data = [[experiment_data['exp0']['sub_dict_1']['values'],
                    experiment_data['exp1']['sub_dict_1']['values']],
                   [experiment_data['exp0']['sub_dict_2']['values'],
                    experiment_data['exp1']['sub_dict_2']['values']]]

    eu.misc.list_equal(data, target_data)

    target_labels = [('sub_dict_1.values', [('Experiment 0', ['e0 - 0', 'e0 - 1']), ('Experiment 1', ['e1 - 0', 'e1 - 1'])]),
                     ('sub_dict_2.values', [('Experiment 0', ['e0 - 0', 'e0 - 1']), ('Experiment 1', ['e1 - 0', 'e1 - 1'])])]
    assert eu.misc.list_equal(labels, target_labels)

    # non-repetition data
    data, labels = eu.data.select_experiment_data(experiment_data,
                                             experiment_descriptions=experiment_descriptions,
                                             datasources='sub_dict_1.no_rep_stat',
                                             experiment_ids='exp0',
                                             repetition_ids=['none'])
    target_data = [[experiment_data['exp0']['sub_dict_1']['no_rep_stat']]]
    eu.misc.list_equal(data, target_data)

    target_labels = [('sub_dict_1.no_rep_stat', ['Experiment 0'])]
    assert eu.misc.list_equal(labels, target_labels)




def test_different_datatypes():

    experiment_data, experiment_descriptions = create_test_data()

    ######################################
    # EXPERIMENT DATA

    # several experiments
    data, _ = eu.data.select_experiment_data(experiment_data,
                                        datasources='sub_dict_1.no_rep_stat',
                                        experiment_ids=['exp0', 'exp1'],
                                        repetition_ids='none')
    target_data = [[experiment_data['exp0']['sub_dict_1']['no_rep_stat'],
                    experiment_data['exp1']['sub_dict_1']['no_rep_stat']]]
    assert eu.misc.list_equal(data, target_data)

    data, _ = eu.data.select_experiment_data(experiment_data,
                                        datasources='sub_dict_1.scalar_stat',
                                        experiment_ids=['exp0', 'exp1'],
                                        repetition_ids='none')
    target_data = [[experiment_data['exp0']['sub_dict_1']['scalar_stat'],
                    experiment_data['exp1']['sub_dict_1']['scalar_stat']]]
    assert eu.misc.list_equal(data, target_data)


    ######################################
    # REPETITION DATA

    # all repetitions
    data, _ = eu.data.select_experiment_data(experiment_data,
                                        datasources='rep_values',
                                        experiment_ids='all')

    target_data = [[np.array([experiment_data['exp0']['repetition_data'][0]['rep_values'],
                                  experiment_data['exp0']['repetition_data'][1]['rep_values']]),
                    np.array([experiment_data['exp1']['repetition_data'][0]['rep_values'],
                               experiment_data['exp1']['repetition_data'][1]['rep_values']])]]

    assert eu.misc.list_equal(data, target_data)

    # selected repetitions
    data, _ = eu.data.select_experiment_data(experiment_data,
                                        datasources='rep_values',
                                        experiment_ids='all',
                                        repetition_ids=[1])

    target_data = [[np.array([experiment_data['exp0']['repetition_data'][1]['rep_values']]),
                    np.array([experiment_data['exp1']['repetition_data'][1]['rep_values']])]]

    assert eu.misc.list_equal(data, target_data)

    # repetition data of different size
    data, _ = eu.data.select_experiment_data(experiment_data,
                                        datasources='rep_values_1',
                                        experiment_ids='all',
                                        repetition_ids='all')

    # exp 1
    target_array1 = np.full((2,3), np.nan)
    target_array1[0,:2] = np.array([experiment_data['exp0']['repetition_data'][0]['rep_values_1']])
    target_array1[1,:3] = np.array([experiment_data['exp0']['repetition_data'][1]['rep_values_1']])

    # exp 2
    target_array2 = np.full((2,3), np.nan)
    target_array2[0,:3] = np.array([experiment_data['exp1']['repetition_data'][0]['rep_values_1']])
    target_array2[1,:1] = np.array([experiment_data['exp1']['repetition_data'][1]['rep_values_1']])

    target_data = [[target_array1,
                    target_array2]]

    assert eu.misc.list_equal(data, target_data)


    # repetition data of size 1
    data, _ = eu.data.select_experiment_data(experiment_data,
                                        datasources='rep_values_2',
                                        experiment_ids='all',
                                        repetition_ids='all')

    target_data = [[np.array([experiment_data['exp0']['repetition_data'][0]['rep_values_2'][0],
                              experiment_data['exp0']['repetition_data'][1]['rep_values_2'][0]]),
                    np.array([experiment_data['exp1']['repetition_data'][0]['rep_values_2'][0],
                              experiment_data['exp1']['repetition_data'][1]['rep_values_2'][0]])]]

    assert eu.misc.list_equal(data, target_data)


    # repetition data of type scalar
    data, _ = eu.data.select_experiment_data(experiment_data,
                                        datasources='rep_values_3',
                                        experiment_ids='all',
                                        repetition_ids='all')

    target_data = [[np.array([experiment_data['exp0']['repetition_data'][0]['rep_values_3'],
                              experiment_data['exp0']['repetition_data'][1]['rep_values_3']]),
                    np.array([experiment_data['exp1']['repetition_data'][0]['rep_values_3'],
                              experiment_data['exp1']['repetition_data'][1]['rep_values_3']])]]

    assert eu.misc.list_equal(data, target_data)

    ######################################
    # EXPERIMENT - REPETITION DATA

    # these cases are tested in the test_datasource_experimentid_repetitionid_filters() function





def test_data_filter():

    pass

