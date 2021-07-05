import os
import exputils as eu
import exputils.data.logging as log
import numpy as np


def create_test_data(target_directory_path):

    # make experiment folders and repetition folders
    experiment_path = os.path.join(target_directory_path, 'experiment_000000')
    rep_00_path = os.path.join(experiment_path, 'repetition_000000')
    rep_01_path = os.path.join(experiment_path, 'repetition_000001')

    os.makedirs(experiment_path, exist_ok=True)
    os.makedirs(rep_00_path, exist_ok=True)
    os.makedirs(rep_01_path, exist_ok=True)

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
