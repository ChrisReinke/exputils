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
    eu.manage.start_experiments(directory=directory, parallel=True)

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
    assert n_open_scripts == 3


def test_get_number_of_scripts(tmpdir):

    dir_path = os.path.dirname(os.path.realpath(__file__))

    # change working directory to this path
    os.chdir(dir_path)

    # copy the scripts in the temporary folder
    directory = os.path.join(tmpdir.strpath, 'test_experimentstarter_01')
    shutil.copytree('./start_scripts', directory)

    # check
    n_scripts = eu.manage.get_number_of_scripts(directory=directory)
    assert n_scripts == 4
