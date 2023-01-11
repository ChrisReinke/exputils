##
## This file is part of the exputils package.
##
## Copyright: INRIA
## Year: 2022, 2023
## Contact: chris.reinke@inria.fr
##
## exputils is provided under GPL-3.0-or-later
##
import os
import exputils as eu
import exputils.data.logging as log
import numpy as np


def create_test_data(target_directory_path, experiment_id = '000000'):

    # make experiment folders and repetition folders
    experiment_path = os.path.join(target_directory_path, 'experiment_' + experiment_id)
    rep_00_path = os.path.join(experiment_path, 'repetition_000000')
    rep_01_path = os.path.join(experiment_path, 'repetition_000001')

    os.makedirs(experiment_path, exist_ok=True)
    os.makedirs(rep_00_path, exist_ok=True)
    os.makedirs(rep_01_path, exist_ok=True)

    ########################
    # make experiment data
    log.clear()
    log.set_directory(os.path.join(experiment_path, eu.DEFAULT_DATA_DIRECTORY))
    for i in range(100):
        log.add_value('exp_data_01', np.random.rand())
        log.add_value('exp_data_02', np.random.rand())
    log.set_config(numpy_log_mode='npy')
    log.save()

    log.clear()
    log.set_directory(os.path.join(experiment_path, eu.DEFAULT_DATA_DIRECTORY))
    for i in range(100):
        log.add_value('exp_data_03', np.random.rand())
        log.add_value('exp_data_04', np.random.rand())
    log.set_config(numpy_log_mode='npz')
    log.save()

    # add a single object, a dill file per repetition
    log.clear()
    log.set_directory(os.path.join(experiment_path, eu.DEFAULT_DATA_DIRECTORY))
    log.add_single_object('single_object', dict(info='exp'))
    log.save()

    ########################
    # make repetition 0 data
    log.clear()
    log.set_directory(os.path.join(rep_00_path, eu.DEFAULT_DATA_DIRECTORY))
    for i in range(100):
        log.add_value('rep_data_01', np.random.rand())
        log.add_value('rep_data_02', np.random.rand())
    log.set_config(numpy_log_mode='npy')
    log.save()

    log.clear()
    log.set_directory(os.path.join(rep_00_path, eu.DEFAULT_DATA_DIRECTORY))
    for i in range(100):
        log.add_value('rep_data_03', np.random.rand())
        log.add_value('rep_data_04', np.random.rand())
    log.set_config(numpy_log_mode='npz')
    log.save()

    # add a single object, a dill file per repetition
    log.clear()
    log.set_directory(os.path.join(rep_00_path, eu.DEFAULT_DATA_DIRECTORY))
    log.add_single_object('single_object',dict(info='rep_00'))
    log.save()

    ########################
    # make repetition 1 data
    log.clear()
    log.set_directory(os.path.join(rep_01_path, eu.DEFAULT_DATA_DIRECTORY))
    for i in range(100):
        log.add_value('rep_data_01', np.random.rand())
        log.add_value('rep_data_02', np.random.rand())
    log.set_config(numpy_log_mode='npy')
    log.save()

    log.clear()
    log.set_directory(os.path.join(rep_01_path, eu.DEFAULT_DATA_DIRECTORY))
    for i in range(100):
        log.add_value('rep_data_03', np.random.rand())
        log.add_value('rep_data_04', np.random.rand())
    log.set_config(numpy_log_mode='npz')
    log.save()

    # add a single object, a dill file per repetition
    log.clear()
    log.set_directory(os.path.join(rep_01_path, eu.DEFAULT_DATA_DIRECTORY))
    log.add_single_object('single_object', dict(info='rep_01'))
    log.save()

    ########################
    # add a configuration python module for each repetition
    f = open(os.path.join(rep_00_path, 'config.py'), 'w')
    f.write('config = \'rep_0_config\'')
    f.close()

    f = open(os.path.join(rep_01_path, 'config.py'), 'w')
    f.write('config = \'rep_1_config\'')
    f.close()




def test_loading(tmpdir):

    create_test_data(tmpdir.strpath)

    # direct loading
    data, exp_descr = eu.data.loading.load_experiment_data(experiments_directory=tmpdir.strpath)

    assert '000000' in data
    assert 'exp_data_01' in data['000000']
    assert 'exp_data_02' in data['000000']

    assert 0 in data['000000'].repetition_data
    assert 'rep_data_01' in data['000000'].repetition_data[0]
    assert 'rep_data_02' in data['000000'].repetition_data[0]

    assert 1 in data['000000'].repetition_data
    assert 'rep_data_01' in data['000000'].repetition_data[1]
    assert 'rep_data_02' in data['000000'].repetition_data[1]

    # loading from experiment descriptions
    exp_descr = eu.data.loading.load_experiment_descriptions(experiments_directory=tmpdir.strpath)
    data, exp_descr = eu.data.loading.load_experiment_data(experiment_descriptions=exp_descr)

    assert '000000' in data
    assert 'exp_data_01' in data['000000']
    assert 'exp_data_02' in data['000000']

    assert 0 in data['000000'].repetition_data
    assert 'rep_data_01' in data['000000'].repetition_data[0]
    assert 'rep_data_02' in data['000000'].repetition_data[0]

    assert 1 in data['000000'].repetition_data
    assert 'rep_data_01' in data['000000'].repetition_data[1]
    assert 'rep_data_02' in data['000000'].repetition_data[1]

    # TODO: test experiment descriptions


def test_loading_single_experiment(tmpdir):

    create_test_data(tmpdir.strpath, '000000')
    create_test_data(tmpdir.strpath, '000001')

    #####################################
    # load all
    data, exp_descr = eu.data.loading.load_experiment_data(
        experiments_directory=tmpdir.strpath,
        #allowed_experiments_id_list=[]
    )

    assert '000000' in data
    assert 'exp_data_01' in data['000000']
    assert 'exp_data_02' in data['000000']

    assert 0 in data['000000'].repetition_data
    assert 'rep_data_01' in data['000000'].repetition_data[0]
    assert 'rep_data_02' in data['000000'].repetition_data[0]

    assert 1 in data['000000'].repetition_data
    assert 'rep_data_01' in data['000000'].repetition_data[1]
    assert 'rep_data_02' in data['000000'].repetition_data[1]


    assert '000001' in data
    assert 'exp_data_01' in data['000001']
    assert 'exp_data_02' in data['000001']

    assert 0 in data['000001'].repetition_data
    assert 'rep_data_01' in data['000001'].repetition_data[0]
    assert 'rep_data_02' in data['000001'].repetition_data[0]

    assert 1 in data['000001'].repetition_data
    assert 'rep_data_01' in data['000001'].repetition_data[1]
    assert 'rep_data_02' in data['000001'].repetition_data[1]

    #####################################
    # only load exp 000001
    data, exp_descr = eu.data.loading.load_experiment_data(
        experiments_directory=tmpdir.strpath,
        allowed_experiments_id_list=['000001']
    )

    assert '000000' not in data

    assert '000001' in data
    assert 'exp_data_01' in data['000001']
    assert 'exp_data_02' in data['000001']

    assert 0 in data['000001'].repetition_data
    assert 'rep_data_01' in data['000001'].repetition_data[0]
    assert 'rep_data_02' in data['000001'].repetition_data[0]

    assert 1 in data['000001'].repetition_data
    assert 'rep_data_01' in data['000001'].repetition_data[1]
    assert 'rep_data_02' in data['000001'].repetition_data[1]


    #####################################
    # do not load exp 000001
    data, exp_descr = eu.data.loading.load_experiment_data(
        experiments_directory=tmpdir.strpath,
        denied_experiments_id_list=['000001']
    )

    assert '000000' in data
    assert 'exp_data_01' in data['000000']
    assert 'exp_data_02' in data['000000']

    assert 0 in data['000000'].repetition_data
    assert 'rep_data_01' in data['000000'].repetition_data[0]
    assert 'rep_data_02' in data['000000'].repetition_data[0]

    assert 1 in data['000000'].repetition_data
    assert 'rep_data_01' in data['000000'].repetition_data[1]
    assert 'rep_data_02' in data['000000'].repetition_data[1]


    assert '000001' not in data


def test_loading_pre_allowed_data_filter(tmpdir):
    create_test_data(tmpdir.strpath)

    data, exp_descr = eu.data.loading.load_experiment_data(
        experiments_directory=tmpdir.strpath,
        pre_allowed_data_filter = ['exp_data_01', 'rep_data_01']
        )

    assert '000000' in data
    assert 'exp_data_01' in data['000000']
    assert 'exp_data_02' not in data['000000']

    assert 0 in data['000000'].repetition_data
    assert 'rep_data_01' in data['000000'].repetition_data[0]
    assert 'rep_data_02' not in data['000000'].repetition_data[0]

    assert 1 in data['000000'].repetition_data
    assert 'rep_data_01' in data['000000'].repetition_data[1]
    assert 'rep_data_02' not in data['000000'].repetition_data[1]


def test_loading_pre_denied_data_filter(tmpdir):
    create_test_data(tmpdir.strpath)

    data, exp_descr = eu.data.loading.load_experiment_data(
        experiments_directory=tmpdir.strpath,
        pre_denied_data_filter = ['exp_data_02', 'rep_data_02']
        )

    assert '000000' in data
    assert 'exp_data_01' in data['000000']
    assert 'exp_data_02' not in data['000000']

    assert 0 in data['000000'].repetition_data
    assert 'rep_data_01' in data['000000'].repetition_data[0]
    assert 'rep_data_02' not in data['000000'].repetition_data[0]

    assert 1 in data['000000'].repetition_data
    assert 'rep_data_01' in data['000000'].repetition_data[1]
    assert 'rep_data_02' not in data['000000'].repetition_data[1]


def test_loading_post_allowed_data_filter(tmpdir):
    create_test_data(tmpdir.strpath)

    data, exp_descr = eu.data.loading.load_experiment_data(
        experiments_directory=tmpdir.strpath,
        post_allowed_data_filter = ['exp_data_01', 'rep_data_01']
        )

    assert '000000' in data
    assert 'exp_data_01' in data['000000']
    assert 'exp_data_02' not in data['000000']

    assert 0 in data['000000'].repetition_data
    assert 'rep_data_01' in data['000000'].repetition_data[0]
    assert 'rep_data_02' not in data['000000'].repetition_data[0]

    assert 1 in data['000000'].repetition_data
    assert 'rep_data_01' in data['000000'].repetition_data[1]
    assert 'rep_data_02' not in data['000000'].repetition_data[1]


def test_loading_post_denied_data_filter(tmpdir):
    create_test_data(tmpdir.strpath)

    data, exp_descr = eu.data.loading.load_experiment_data(
        experiments_directory=tmpdir.strpath,
        post_denied_data_filter = ['exp_data_02', 'rep_data_02']
        )

    assert '000000' in data
    assert 'exp_data_01' in data['000000']
    assert 'exp_data_02' not in data['000000']

    assert 0 in data['000000'].repetition_data
    assert 'rep_data_01' in data['000000'].repetition_data[0]
    assert 'rep_data_02' not in data['000000'].repetition_data[0]

    assert 1 in data['000000'].repetition_data
    assert 'rep_data_01' in data['000000'].repetition_data[1]
    assert 'rep_data_02' not in data['000000'].repetition_data[1]


def test_loading_on_experiment_data_loaded(tmpdir):
    create_test_data(tmpdir.strpath)

    def on_experiment_data_loaded(experiment_id, data):
        assert experiment_id == '000000'
        data.mean_exp_data_01 = np.mean(data.exp_data_01)

    # by itself
    data, exp_descr = eu.data.loading.load_experiment_data(
        experiments_directory=tmpdir.strpath,
        on_experiment_data_loaded=[on_experiment_data_loaded]
        )

    assert '000000' in data
    assert 'exp_data_01' in data['000000']
    assert 'exp_data_02' in data['000000']
    assert 'mean_exp_data_01' in data['000000']
    assert data['000000'].mean_exp_data_01 == np.mean(data['000000'].exp_data_01)

    assert 0 in data['000000'].repetition_data
    assert 'rep_data_01' in data['000000'].repetition_data[0]
    assert 'rep_data_02' in data['000000'].repetition_data[0]

    assert 1 in data['000000'].repetition_data
    assert 'rep_data_01' in data['000000'].repetition_data[1]
    assert 'rep_data_02' in data['000000'].repetition_data[1]

    # combine with pre and post data filter
    data, exp_descr = eu.data.loading.load_experiment_data(
        experiments_directory=tmpdir.strpath,
        on_experiment_data_loaded=[on_experiment_data_loaded],
        pre_allowed_data_filter=['exp_data_01'],
        post_denied_data_filter=['exp_data_01'],
        )

    assert '000000' in data
    assert 'exp_data_01' not in data['000000']
    assert 'exp_data_02' not in data['000000']
    assert 'mean_exp_data_01' in data['000000']

    assert 0 in data['000000'].repetition_data
    assert 'rep_data_01' not in data['000000'].repetition_data[0]
    assert 'rep_data_02' not in data['000000'].repetition_data[0]

    assert 1 in data['000000'].repetition_data
    assert 'rep_data_01' not in data['000000'].repetition_data[1]
    assert 'rep_data_02' not in data['000000'].repetition_data[1]


def test_loading_on_repetition_data_loaded(tmpdir):
    create_test_data(tmpdir.strpath)

    def on_repetition_data_loaded(experiment_id, repetition_id, data):
        assert experiment_id == '000000'
        assert repetition_id == 0 or repetition_id == 1
        data.mean_rep_data_01 = np.mean(data.rep_data_01)

    # by itself
    data, exp_descr = eu.data.loading.load_experiment_data(
        experiments_directory=tmpdir.strpath,
        on_repetition_data_loaded=[on_repetition_data_loaded]
        )

    assert '000000' in data
    assert 'exp_data_01' in data['000000']
    assert 'exp_data_02' in data['000000']

    assert 0 in data['000000'].repetition_data
    assert 'rep_data_01' in data['000000'].repetition_data[0]
    assert 'rep_data_02' in data['000000'].repetition_data[0]
    assert 'mean_rep_data_01' in data['000000'].repetition_data[0]
    assert data['000000'].repetition_data[0].mean_rep_data_01 == np.mean(data['000000'].repetition_data[0].rep_data_01)

    assert 1 in data['000000'].repetition_data
    assert 'rep_data_01' in data['000000'].repetition_data[1]
    assert 'rep_data_02' in data['000000'].repetition_data[1]
    assert 'mean_rep_data_01' in data['000000'].repetition_data[1]
    assert data['000000'].repetition_data[1].mean_rep_data_01 == np.mean(data['000000'].repetition_data[1].rep_data_01)

    # combine with pre and post data filter
    data, exp_descr = eu.data.loading.load_experiment_data(
        experiments_directory=tmpdir.strpath,
        on_repetition_data_loaded=[on_repetition_data_loaded],
        pre_allowed_data_filter=['rep_data_01'],
        post_denied_data_filter=['rep_data_01'],
        )

    assert '000000' in data
    assert 'exp_data_01' not in data['000000']
    assert 'exp_data_02' not in data['000000']

    assert 0 in data['000000'].repetition_data
    assert 'rep_data_01' not in data['000000'].repetition_data[0]
    assert 'rep_data_02' not in data['000000'].repetition_data[0]
    assert 'mean_rep_data_01' in data['000000'].repetition_data[0]

    assert 1 in data['000000'].repetition_data
    assert 'rep_data_01' not in data['000000'].repetition_data[1]
    assert 'rep_data_02' not in data['000000'].repetition_data[1]
    assert 'mean_rep_data_01' in data['000000'].repetition_data[1]


def test_loading_python_module(tmpdir):
    create_test_data(tmpdir.strpath)

    config_module = eu.data.loading.load_experiment_python_module(
        experiment_id=0,
        repetition_id=0,
        module_path='config.py',
        experiments_directory=tmpdir.strpath)

    assert config_module.config == 'rep_0_config'

    config_module = eu.data.loading.load_experiment_python_module(
        experiment_id=0,
        repetition_id=1,
        module_path='config.py',
        experiments_directory=tmpdir.strpath)

    assert config_module.config == 'rep_1_config'


def test_loading_single_object(tmpdir):
    create_test_data(tmpdir.strpath)

    obj = eu.data.loading.load_experiment_data_single_object(
        'single_object',
        experiment_id=0,
        repetition_id=0,
        experiments_directory=tmpdir.strpath)
    assert obj['info'] == 'rep_00'

    obj = eu.data.loading.load_experiment_data_single_object(
        'single_object',
        experiment_id=0,
        repetition_id=1,
        experiments_directory=tmpdir.strpath)
    assert obj['info'] == 'rep_01'

    obj = eu.data.loading.load_experiment_data_single_object(
        'single_object',
        experiment_id=0,
        experiments_directory=tmpdir.strpath)
    assert obj['info'] == 'exp'
