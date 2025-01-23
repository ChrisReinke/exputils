import os
import exputils as eu
import shutil

def test_get_number_of_scripts_to_execute(tmpdir):

    dir_path = os.path.dirname(os.path.realpath(__file__))

    # change working directory to this path
    os.chdir(dir_path)

    # copy the scripts in the temporary folder
    directory = os.path.join(tmpdir.strpath, 'test_get_number_of_scripts_to_execute')
    shutil.copytree('./start_scripts', directory)

    # check
    n_open_scripts = eu.manage.get_number_of_scripts_to_execute(start_scripts='*.sh', directory=directory)
    assert n_open_scripts == 4


def test_get_number_of_scripts(tmpdir):

    dir_path = os.path.dirname(os.path.realpath(__file__))

    # change working directory to this path
    os.chdir(dir_path)

    # copy the scripts in the temporary folder
    directory = os.path.join(tmpdir.strpath, 'test_get_number_of_scripts')
    shutil.copytree('./start_scripts', directory)

    # check
    n_scripts = eu.manage.get_number_of_scripts(start_scripts='*.sh', directory=directory)
    assert n_scripts == 5


def test_get_experiments_status_on_campaign(tmpdir):

    dir_path = os.path.dirname(os.path.realpath(__file__))

    # change working directory to this path
    os.chdir(dir_path)

    # copy the scripts in the temporary folder
    directory = os.path.join(tmpdir.strpath, 'test_get_experiments_status_on_campaign')
    shutil.copytree('./campaign', directory)

    # check
    status, statistics = eu.manage.get_experiments_status(directory=directory)

    assert len(status) == 5

    assert status[0].date == '2024/11/13'
    assert status[0].time == '09:53:53'
    assert status[0].status == 'todo'
    assert status[0].experiment_id == '000001'
    assert status[0].repetition_idx == 1
    assert status[0].script_path == os.path.join(
        directory,
        'experiments/experiment_000001/repetition_000001/run_repetition.py'
    )

    assert status[1].date == '2024/11/11'
    assert status[1].time == '09:53:54'
    assert status[1].status == 'running'
    assert status[1].experiment_id == '000002'
    assert status[1].repetition_idx == 0
    assert status[1].script_path == os.path.join(
        directory,
        'experiments/experiment_000002/repetition_000000/run_repetition.py'
    )

    assert status[2].date == '2024/11/10'
    assert status[2].time == '09:54:53'
    assert status[2].status == 'ongoing update'
    assert status[2].experiment_id == '000002'
    assert status[2].repetition_idx == 1
    assert status[2].script_path == os.path.join(
        directory,
        'experiments/experiment_000002/repetition_000001/run_repetition.py'
    )

    assert status[3].date == '2023/11/13'
    assert status[3].time == '10:53:53'
    assert status[3].status == 'finished'
    assert status[3].experiment_id == '000003'
    assert status[3].repetition_idx == 0
    assert status[3].script_path == os.path.join(
        directory,
        'experiments/experiment_000003/repetition_000000/run_repetition.py'
    )

    assert status[4].date == '2024/09/13'
    assert status[4].time == '11:53:53'
    assert status[4].status == 'error'
    assert status[4].experiment_id == '000003'
    assert status[4].repetition_idx == 1
    assert status[4].script_path == os.path.join(
        directory,
        'experiments/experiment_000003/repetition_000001/run_repetition.py'
    )

    assert statistics.total == 5
    assert statistics.todo == 1
    assert statistics.running == 2
    assert statistics.finished == 1
    assert statistics.error == 1


def test_get_experiments_status_on_open_format(tmpdir):

    dir_path = os.path.dirname(os.path.realpath(__file__))

    # change working directory to this path
    os.chdir(dir_path)

    # copy the scripts in the temporary folder
    directory = os.path.join(tmpdir.strpath, 'test_get_experiments_status_on_open_format')
    shutil.copytree('./start_scripts', directory)

    # check
    status, statistics = eu.manage.get_experiments_status(directory=directory)

    assert len(status) == 3

    # TODO: check the correct status of each file
    assert status[0].date == '2024/11/13'

    assert statistics.total == 3
    assert statistics.todo == 1
    assert statistics.running == 0
    assert statistics.finished == 1
    assert statistics.error == 1
