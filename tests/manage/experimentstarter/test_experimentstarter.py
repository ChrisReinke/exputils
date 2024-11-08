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
import shutil


def test_experimentstarter(tmpdir):

    dir_path = os.path.dirname(os.path.realpath(__file__))

    # change working directory to this path
    os.chdir(dir_path)


    ############################################################################
    ## test 01 - serial

    # copy the scripts in the temporary folder
    directory = os.path.join(tmpdir.strpath, 'test_experimentstarter_01')
    shutil.copytree('./start_scripts', directory)

    # run scripts
    eu.manage.start_experiments(directory=directory, parallel=False)

    # check if the required files have been generated
    assert os.path.isfile(os.path.join(directory, 'job04.txt'))
    assert os.path.isfile(os.path.join(directory, 'job01/job01.txt'))
    assert os.path.isfile(os.path.join(directory, 'job02/job02.txt'))
    assert not os.path.isfile(os.path.join(directory, 'job03/job03.txt'))

    ############################################################################
    ## test 02 - parallel

    # copy the scripts in the temporary folder
    directory = os.path.join(tmpdir.strpath, 'test_experimentstarter_02')
    shutil.copytree('./start_scripts', directory)

    # run scripts
    eu.manage.start_experiments(directory=directory, parallel=True, verbose=True)

    # check if the required files have been generated
    assert os.path.isfile(os.path.join(directory, 'job04.txt'))
    assert os.path.isfile(os.path.join(directory, 'job01/job01.txt'))
    assert os.path.isfile(os.path.join(directory, 'job02/job02.txt'))
    assert not os.path.isfile(os.path.join(directory, 'job03/job03.txt'))


    ############################################################################
    ## test 03 - is_chdir=True

    # copy the scripts in the temporary folder
    directory = os.path.join(tmpdir.strpath, 'test_experimentstarter_03')
    shutil.copytree('./start_scripts', directory)

    # run scripts
    eu.manage.start_experiments(directory=directory, parallel=True, is_chdir=True)

    # check if the required files have been generated
    assert os.path.isfile(os.path.join(directory, 'job04.txt'))
    assert os.path.isfile(os.path.join(directory, 'job01/job01.txt'))
    assert os.path.isfile(os.path.join(directory, 'job02/job02.txt'))
    assert not os.path.isfile(os.path.join(directory, 'job03/job03.txt'))


def test_get_number_of_scripts_to_execute(tmpdir):

    dir_path = os.path.dirname(os.path.realpath(__file__))

    # change working directory to this path
    os.chdir(dir_path)

    # copy the scripts in the temporary folder
    directory = os.path.join(tmpdir.strpath, 'test_experimentstarter_01')
    shutil.copytree('./start_scripts', directory)

    # check
    n_open_scripts = eu.manage.get_number_of_scripts_to_execute(directory=directory)
    assert n_open_scripts == 4


def test_get_number_of_scripts(tmpdir):

    dir_path = os.path.dirname(os.path.realpath(__file__))

    # change working directory to this path
    os.chdir(dir_path)

    # copy the scripts in the temporary folder
    directory = os.path.join(tmpdir.strpath, 'test_experimentstarter_01')
    shutil.copytree('./start_scripts', directory)

    # check
    n_scripts = eu.manage.get_number_of_scripts(directory=directory)
    assert n_scripts == 5


def test_is_to_start_status():

    assert eu.manage.experimentstarter._is_to_start_status('todo')
    assert eu.manage.experimentstarter._is_to_start_status('error')
    assert eu.manage.experimentstarter._is_to_start_status('none')
    assert eu.manage.experimentstarter._is_to_start_status(None)
    assert eu.manage.experimentstarter._is_to_start_status('unfinished')

    assert eu.manage.experimentstarter._is_to_start_status('running') == False
    assert eu.manage.experimentstarter._is_to_start_status('running 50%') == False
    assert eu.manage.experimentstarter._is_to_start_status('dwdw') == False


def test_status_file_writing_default_on(tmpdir):

    ####################################################################
    # Automatic writting of status file is on by default

    # job4 of the scripts is writing a message into the status file, check it

    dir_path = os.path.dirname(os.path.realpath(__file__))
    # change working directory to this path
    os.chdir(dir_path)

    # copy the scripts in the temporary folder
    directory = os.path.join(tmpdir.strpath, 'test_update_status_file')
    shutil.copytree('./start_scripts', directory)

    # run scripts
    eu.manage.start_experiments(directory=directory, parallel=False)

    # exists a status file?
    status_file_path = os.path.join(directory, 'job04/start.sh.status')

    assert os.path.isfile(status_file_path)

    # read file and see if the message was written
    n_todo_messages = 0
    n_running_messages = 0
    n_custom_messages = 0
    n_finished_messages = 0

    f = open(status_file_path, 'r')
    lines = f.readlines()
    for line in lines:
        if line == 'todo\n':
            n_todo_messages += 1
        if line == 'running\n':
            n_running_messages += 1
        if line == 'running hello\n':
            n_custom_messages += 1
        if line == 'finished\n':
            n_finished_messages += 1

    assert n_todo_messages == 1
    assert n_running_messages == 1
    assert n_custom_messages == 1
    assert n_finished_messages == 1


def test_status_file_writing_off(tmpdir):
    ####################################################################
    # Automatic writting of status file is on by default

    # job4 of the scripts is writing a message into the status file, check it

    dir_path = os.path.dirname(os.path.realpath(__file__))
    # change working directory to this path
    os.chdir(dir_path)

    # copy the scripts in the temporary folder
    directory = os.path.join(tmpdir.strpath, 'test_update_status_file')
    shutil.copytree('./start_scripts', directory)

    # run scripts
    eu.manage.start_experiments(directory=directory, parallel=False, write_status_files_automatically=False)

    # exists a status file?
    status_file_path = os.path.join(directory, 'job04/start.sh.status')

    assert os.path.isfile(status_file_path)

    # read file and see if the message was written
    n_todo_messages = 0
    n_running_messages = 0
    n_custom_messages = 0
    n_finished_messages = 0

    f = open(status_file_path, 'r')
    lines = f.readlines()
    for line in lines:
        if line == 'todo\n':
            n_todo_messages += 1
        if line == 'running\n':
            n_running_messages += 1
        if line == 'running hello\n':
            n_custom_messages += 1
        if line == 'finished\n':
            n_finished_messages += 1

    assert n_todo_messages == 0
    assert n_running_messages == 0
    assert n_custom_messages == 1
    assert n_finished_messages == 0
