##
## This file is part of the exputils package.
##
## Copyright: INRIA
## Year: 2022, 2023
## Contact: chris.reinke@inria.fr
##
## exputils is provided under GPL-3.0-or-later
##
import exputils as eu
import os


def test_generate_experiments(tmpdir):

    dir_path = os.path.dirname(os.path.realpath(__file__))

    # change working directory to this path
    os.chdir(dir_path)

    ################################################
    # test 1

    directory = os.path.join(tmpdir.strpath, 'test01')

    eu.manage.generate_experiment_files(
        os.path.join(dir_path, 'test_01.ods'),
        directory=directory,
        extra_files=[os.path.join(dir_path, 'extra_file_01'), os.path.join(dir_path, 'extra_file_02')]
    )

    # group folders
    assert os.path.isdir(os.path.join(directory, 'group_01'))
    assert os.path.isdir(os.path.join(directory, 'group_02'))

    # experiment folder folders
    assert os.path.isdir(os.path.join(directory, 'group_01', 'experiment_000001'))
    assert os.path.isdir(os.path.join(directory, 'group_01', 'experiment_000003'))
    assert os.path.isdir(os.path.join(directory, 'group_02', 'experiment_000010'))
    assert os.path.isdir(os.path.join(directory, 'group_02', 'experiment_000030'))

    # experiment files
    assert os.path.isfile(os.path.join(directory, 'group_01', 'experiment_000001', 'file_01'))
    assert os.path.isfile(os.path.join(directory, 'group_01', 'experiment_000001', 'exp_1_file_02'))
    assert os.path.isfile(os.path.join(directory, 'group_01', 'experiment_000001', 'extra_file_01'))
    assert os.path.isfile(os.path.join(directory, 'group_01', 'experiment_000001', 'extra_file_02'))

    assert os.path.isfile(os.path.join(directory, 'group_01', 'experiment_000003', 'file_01'))
    assert os.path.isfile(os.path.join(directory, 'group_01', 'experiment_000003', 'exp_3_file_02'))
    assert os.path.isfile(os.path.join(directory, 'group_01', 'experiment_000003', 'extra_file_01'))
    assert os.path.isfile(os.path.join(directory, 'group_01', 'experiment_000003', 'extra_file_02'))

    assert os.path.isfile(os.path.join(directory, 'group_02', 'experiment_000010', 'file_01'))
    assert os.path.isfile(os.path.join(directory, 'group_02', 'experiment_000010', 'exp_10_file_02'))
    assert os.path.isfile(os.path.join(directory, 'group_02', 'experiment_000010', 'extra_file_01'))
    assert os.path.isfile(os.path.join(directory, 'group_02', 'experiment_000010', 'extra_file_02'))

    assert os.path.isfile(os.path.join(directory, 'group_02', 'experiment_000030', 'file_01'))
    assert os.path.isfile(os.path.join(directory, 'group_02', 'experiment_000030', 'exp_30_file_02'))
    assert os.path.isfile(os.path.join(directory, 'group_02', 'experiment_000030', 'extra_file_01'))
    assert os.path.isfile(os.path.join(directory, 'group_02', 'experiment_000030', 'extra_file_02'))

    # file content
    with open(os.path.join(directory, 'group_01', 'experiment_000001', 'file_01'), 'r') as file:
        file_content = file.read()
    assert 'file 1:\n1\n0\n1\nguten\n' == file_content

    with open(os.path.join(directory, 'group_01', 'experiment_000001', 'exp_1_file_02'), 'r') as file:
        file_content = file.read()
    assert 'file 2:\n3\nvielen\n' == file_content

    with open(os.path.join(directory, 'group_01', 'experiment_000003', 'file_01'), 'r') as file:
        file_content = file.read()
    assert 'file 1:\n3\n0\n5\ntag\n' == file_content

    with open(os.path.join(directory, 'group_01', 'experiment_000003', 'exp_3_file_02'), 'r') as file:
        file_content = file.read()
    assert 'file 2:\n7\ndank\n' == file_content

    with open(os.path.join(directory, 'group_02', 'experiment_000010', 'file_01'), 'r') as file:
        file_content = file.read()
    assert 'file 1:\n10\n0\n10\nguten\n' == file_content

    with open(os.path.join(directory, 'group_02', 'experiment_000010', 'exp_10_file_02'), 'r') as file:
        file_content = file.read()
    assert 'file 2:\n30\nvielen\n' == file_content

    with open(os.path.join(directory, 'group_02', 'experiment_000030', 'file_01'), 'r') as file:
        file_content = file.read()
    assert 'file 1:\n30\n0\n50\ntag\n' == file_content

    with open(os.path.join(directory, 'group_02', 'experiment_000030', 'exp_30_file_02'), 'r') as file:
        file_content = file.read()
    assert 'file 2:\n70\ndank\n' == file_content

    ################################################
    # test 2 - different ods layout

    directory = os.path.join(tmpdir.strpath, 'test02')

    eu.manage.generate_experiment_files(os.path.join(dir_path, 'test_02.ods'), directory=directory, extra_files=os.path.join(dir_path, 'extra_file_01'))

    # group folders
    assert os.path.isdir(os.path.join(directory))

    # experiment folder folders
    assert os.path.isdir(os.path.join(directory, 'experiment_000001'))
    assert os.path.isdir(os.path.join(directory, 'experiment_000003'))

    # experiment files
    assert os.path.isfile(os.path.join(directory, 'experiment_000001', 'file_01'))
    assert os.path.isfile(os.path.join(directory, 'experiment_000001', 'exp_1_file_02'))
    assert os.path.isfile(os.path.join(directory, 'experiment_000001', 'extra_file_01'))


    assert os.path.isfile(os.path.join(directory, 'experiment_000003', 'file_01'))
    assert os.path.isfile(os.path.join(directory, 'experiment_000003', 'exp_3_file_02'))
    assert os.path.isfile(os.path.join(directory, 'experiment_000003', 'extra_file_01'))

    # file content
    with open(os.path.join(directory, 'experiment_000001', 'file_01'), 'r') as file:
        file_content = file.read()
    assert 'file 1:\n1\n0\n1\nguten\n' == file_content

    with open(os.path.join(directory, 'experiment_000001', 'exp_1_file_02'), 'r') as file:
        file_content = file.read()
    assert 'file 2:\n3\nvielen\n' == file_content

    with open(os.path.join(directory, 'experiment_000003', 'file_01'), 'r') as file:
        file_content = file.read()
    assert 'file 1:\n3\n0\n5\ntag\n' == file_content

    with open(os.path.join(directory, 'experiment_000003', 'exp_3_file_02'), 'r') as file:
        file_content = file.read()
    assert 'file 2:\n7\ndank\n' == file_content


    ################################################
    # test 3 - repetitions

    directory = os.path.join(tmpdir.strpath, 'test03')

    eu.manage.generate_experiment_files(os.path.join(dir_path, 'test_03.ods'), directory=directory, extra_files=[os.path.join(dir_path, 'extra_file_01'), os.path.join(dir_path, 'extra_file_02')])

    # group folders
    assert os.path.isdir(os.path.join(directory, 'group_01'))

    # experiment folder folders
    assert os.path.isdir(os.path.join(directory, 'group_01', 'experiment_000001'))
    assert os.path.isdir(os.path.join(directory, 'group_01', 'experiment_000003'))

    # repetition folders
    assert os.path.isdir(os.path.join(directory, 'group_01', 'experiment_000001', 'repetition_000000'))
    assert os.path.isdir(os.path.join(directory, 'group_01', 'experiment_000001', 'repetition_000001'))
    assert os.path.isdir(os.path.join(directory, 'group_01', 'experiment_000003', 'repetition_000000'))

    # experiment files
    assert os.path.isfile(os.path.join(directory, 'group_01', 'experiment_000001', 'repetition_000000', 'file_01'))
    assert os.path.isfile(os.path.join(directory, 'group_01', 'experiment_000001', 'repetition_000000', 'exp_1_file_02'))
    assert os.path.isfile(os.path.join(directory, 'group_01', 'experiment_000001', 'repetition_000000', 'extra_file_01'))
    assert os.path.isfile(os.path.join(directory, 'group_01', 'experiment_000001', 'repetition_000000', 'extra_file_02'))

    assert os.path.isfile(os.path.join(directory, 'group_01', 'experiment_000001', 'repetition_000001', 'file_01'))
    assert os.path.isfile(os.path.join(directory, 'group_01', 'experiment_000001', 'repetition_000001', 'exp_1_file_02'))
    assert os.path.isfile(os.path.join(directory, 'group_01', 'experiment_000001', 'repetition_000001', 'extra_file_01'))
    assert os.path.isfile(os.path.join(directory, 'group_01', 'experiment_000001', 'repetition_000001', 'extra_file_02'))

    assert os.path.isfile(os.path.join(directory, 'group_01', 'experiment_000003', 'repetition_000000', 'file_01'))
    assert os.path.isfile(os.path.join(directory, 'group_01', 'experiment_000003', 'repetition_000000', 'exp_3_file_02'))
    assert os.path.isfile(os.path.join(directory, 'group_01', 'experiment_000003', 'repetition_000000', 'extra_file_01'))
    assert os.path.isfile(os.path.join(directory, 'group_01', 'experiment_000003', 'repetition_000000', 'extra_file_02'))


    # file content
    with open(os.path.join(directory, 'group_01', 'experiment_000001', 'repetition_000000', 'file_01'), 'r') as file:
        file_content = file.read()
    assert 'file 1:\n1\n0\n1\nguten\n' == file_content

    with open(os.path.join(directory, 'group_01', 'experiment_000001', 'repetition_000000', 'exp_1_file_02'), 'r') as file:
        file_content = file.read()
    assert 'file 2:\n3\nvielen\n' == file_content

    with open(os.path.join(directory, 'group_01', 'experiment_000001', 'repetition_000001', 'file_01'), 'r') as file:
        file_content = file.read()
    assert 'file 1:\n1\n1\n1\nguten\n' == file_content

    with open(os.path.join(directory, 'group_01', 'experiment_000001', 'repetition_000001', 'exp_1_file_02'), 'r') as file:
        file_content = file.read()
    assert 'file 2:\n3\nvielen\n' == file_content

    with open(os.path.join(directory, 'group_01', 'experiment_000003', 'repetition_000000', 'file_01'), 'r') as file:
        file_content = file.read()
    assert 'file 1:\n3\n0\n5\ntag\n' == file_content

    with open(os.path.join(directory, 'group_01', 'experiment_000003', 'repetition_000000', 'exp_3_file_02'), 'r') as file:
        file_content = file.read()
    assert 'file 2:\n7\ndank\n' == file_content



    ################################################
    # test 4 - special character that have to be converted

    directory = os.path.join(tmpdir.strpath, 'test04')

    eu.manage.generate_experiment_files(os.path.join(dir_path, 'test_04.ods'), directory=directory, extra_files=[os.path.join(dir_path, 'extra_file_01'), os.path.join(dir_path, 'extra_file_02')])

    # file content
    with open(os.path.join(directory, 'group_01', 'experiment_000001', 'file_01'), 'r') as file:
        file_content = file.read()
    assert 'file 1:\n1\n0\n\'bla\'\n\'bla2\'\n' == file_content


    ################################################
    # test 5 - folder for source files and templates

    directory = os.path.join(tmpdir.strpath, 'test05')

    eu.manage.generate_experiment_files(os.path.join(dir_path, 'test_05.ods'), directory=directory, extra_files=[os.path.join(dir_path, 'extra_file_01'), os.path.join(dir_path, 'extra_file_02')])

    # files
    assert os.path.isfile(os.path.join(directory, 'group_01', 'experiment_000001', 'file_03'))
    assert os.path.isfile(os.path.join(directory, 'group_01', 'experiment_000001', 'file_04'))
    assert os.path.isfile(os.path.join(directory, 'group_01', 'experiment_000001', 'extra_file_01'))
    assert os.path.isfile(os.path.join(directory, 'group_01', 'experiment_000001', 'extra_file_02'))
    assert not os.path.isfile(os.path.join(directory, 'group_01', 'experiment_000001', 'file_04_template'))

    assert os.path.isfile(os.path.join(directory, 'group_01', 'experiment_000003', 'file_03'))
    assert os.path.isfile(os.path.join(directory, 'group_01', 'experiment_000003', 'file_04'))
    assert os.path.isfile(os.path.join(directory, 'group_01', 'experiment_000003', 'extra_file_01'))
    assert os.path.isfile(os.path.join(directory, 'group_01', 'experiment_000003', 'extra_file_02'))
    assert not os.path.isfile(os.path.join(directory, 'group_01', 'experiment_000003', 'file_04_template'))


    # files
    assert os.path.isfile(os.path.join(directory, 'group_02', 'experiment_000001', 'file_03'))
    assert os.path.isfile(os.path.join(directory, 'group_02', 'experiment_000001', 'file_04'))
    assert os.path.isfile(os.path.join(directory, 'group_02', 'experiment_000001', 'extra_file_01'))
    assert os.path.isfile(os.path.join(directory, 'group_02', 'experiment_000001', 'extra_file_02'))
    assert not os.path.isfile(os.path.join(directory, 'group_02', 'experiment_000001', 'file_04_template'))


    assert os.path.isfile(os.path.join(directory, 'group_02', 'experiment_000003', 'file_03'))
    assert os.path.isfile(os.path.join(directory, 'group_02', 'experiment_000003', 'file_04'))
    assert os.path.isfile(os.path.join(directory, 'group_02', 'experiment_000003', 'extra_file_01'))
    assert os.path.isfile(os.path.join(directory, 'group_02', 'experiment_000003', 'extra_file_02'))
    assert not os.path.isfile(os.path.join(directory, 'group_02', 'experiment_000003', 'file_04_template'))


    # file content
    with open(os.path.join(directory, 'group_01', 'experiment_000001', 'file_04'), 'r') as file:
        file_content = file.read()
    assert '\'bla\'\n' == file_content

    with open(os.path.join(directory, 'group_01', 'experiment_000003', 'file_04'), 'r') as file:
        file_content = file.read()
    assert '\'blubb\'\n' == file_content


    with open(os.path.join(directory, 'group_02', 'experiment_000001', 'file_04'), 'r') as file:
        file_content = file.read()
    assert '\'bla\'\n' == file_content

    with open(os.path.join(directory, 'group_02', 'experiment_000003', 'file_04'), 'r') as file:
        file_content = file.read()
    assert '\'blubb\'\n' == file_content



    ################################################
    # test 6 - source files for experiments and for repetitions

    directory = os.path.join(tmpdir.strpath, 'test06')

    eu.manage.generate_experiment_files(os.path.join(dir_path, 'test_06.ods'), directory=directory, extra_files=[os.path.join(dir_path, 'extra_file_01')], extra_experiment_files=[os.path.join(dir_path, 'extra_file_02')])

    # files

    # group 01
    # repetition files
    assert os.path.isfile(os.path.join(directory, 'group_01', 'experiment_000001', 'repetition_000000', 'file_03'))
    assert os.path.isfile(os.path.join(directory, 'group_01', 'experiment_000001', 'repetition_000000', 'file_04'))
    assert os.path.isfile(os.path.join(directory, 'group_01', 'experiment_000001', 'repetition_000000', 'extra_file_01'))

    assert os.path.isfile(os.path.join(directory, 'group_01', 'experiment_000001', 'repetition_000001', 'file_03'))
    assert os.path.isfile(os.path.join(directory, 'group_01', 'experiment_000001', 'repetition_000001', 'file_04'))
    assert os.path.isfile(os.path.join(directory, 'group_01', 'experiment_000001', 'repetition_000001', 'extra_file_01'))

    assert os.path.isfile(os.path.join(directory, 'group_01', 'experiment_000003', 'repetition_000000', 'file_03'))
    assert os.path.isfile(os.path.join(directory, 'group_01', 'experiment_000003', 'repetition_000000', 'file_04'))
    assert os.path.isfile(os.path.join(directory, 'group_01', 'experiment_000003', 'repetition_000000', 'extra_file_01'))

    # experiment files
    assert os.path.isfile(os.path.join(directory, 'group_01', 'experiment_000003', 'file_05'))
    assert os.path.isfile(os.path.join(directory, 'group_01', 'experiment_000003', 'file_06'))
    assert os.path.isfile(os.path.join(directory, 'group_01', 'experiment_000003', 'extra_file_02'))

    # group 02
    # repetition directories
    assert os.path.isdir(os.path.join(directory, 'group_02', 'experiment_000001', 'repetition_000000'))
    assert os.path.isdir(os.path.join(directory, 'group_02', 'experiment_000001', 'repetition_000001'))
    assert os.path.isdir(os.path.join(directory, 'group_02', 'experiment_000003', 'repetition_000000'))

    # experiment files
    assert os.path.isfile(os.path.join(directory, 'group_02', 'experiment_000003', 'file_05'))
    assert os.path.isfile(os.path.join(directory, 'group_02', 'experiment_000003', 'file_06'))
    assert os.path.isfile(os.path.join(directory, 'group_02', 'experiment_000003', 'extra_file_02'))


    # file content
    with open(os.path.join(directory, 'group_01', 'experiment_000001', 'repetition_000000', 'file_04'), 'r') as file:
        file_content = file.read()
    assert '\'bla\'\n' == file_content

    with open(os.path.join(directory, 'group_01', 'experiment_000001', 'repetition_000001', 'file_04'), 'r') as file:
        file_content = file.read()
    assert '\'bla\'\n' == file_content

    with open(os.path.join(directory, 'group_01', 'experiment_000001', 'file_05'), 'r') as file:
        file_content = file.read()
    assert '\'bla2\'\n' == file_content


    with open(os.path.join(directory, 'group_01', 'experiment_000003', 'repetition_000000', 'file_04'), 'r') as file:
        file_content = file.read()
    assert '\'blubb\'\n' == file_content

    with open(os.path.join(directory, 'group_01', 'experiment_000003', 'file_05'), 'r') as file:
        file_content = file.read()
    assert '\'blubb2\'\n' == file_content


    with open(os.path.join(directory, 'group_02', 'experiment_000001', 'file_05'), 'r') as file:
        file_content = file.read()
    assert '\'bla2\'\n' == file_content

    with open(os.path.join(directory, 'group_02', 'experiment_000003', 'file_05'), 'r') as file:
        file_content = file.read()
    assert '\'blubb2\'\n' == file_content


def test_generate_experiments_copy_operator_cp(tmpdir):
    # test the non default copy operator cp

    dir_path = os.path.dirname(os.path.realpath(__file__))

    # change working directory to this path
    os.chdir(dir_path)

    ################################################
    # test 1

    directory = os.path.join(tmpdir.strpath, 'test01')

    eu.manage.generate_experiment_files(
        os.path.join(dir_path, 'test_01.ods'),
        directory=directory,
        extra_files=[os.path.join(dir_path, 'extra_file_01'), os.path.join(dir_path, 'extra_file_02')],
        copy_operator='cp'
    )

    # group folders
    assert os.path.isdir(os.path.join(directory, 'group_01'))
    assert os.path.isdir(os.path.join(directory, 'group_02'))

    # experiment folder folders
    assert os.path.isdir(os.path.join(directory, 'group_01', 'experiment_000001'))
    assert os.path.isdir(os.path.join(directory, 'group_01', 'experiment_000003'))
    assert os.path.isdir(os.path.join(directory, 'group_02', 'experiment_000010'))
    assert os.path.isdir(os.path.join(directory, 'group_02', 'experiment_000030'))

    # experiment files
    assert os.path.isfile(os.path.join(directory, 'group_01', 'experiment_000001', 'file_01'))
    assert os.path.isfile(os.path.join(directory, 'group_01', 'experiment_000001', 'exp_1_file_02'))
    assert os.path.isfile(os.path.join(directory, 'group_01', 'experiment_000001', 'extra_file_01'))
    assert os.path.isfile(os.path.join(directory, 'group_01', 'experiment_000001', 'extra_file_02'))

    assert os.path.isfile(os.path.join(directory, 'group_01', 'experiment_000003', 'file_01'))
    assert os.path.isfile(os.path.join(directory, 'group_01', 'experiment_000003', 'exp_3_file_02'))
    assert os.path.isfile(os.path.join(directory, 'group_01', 'experiment_000003', 'extra_file_01'))
    assert os.path.isfile(os.path.join(directory, 'group_01', 'experiment_000003', 'extra_file_02'))

    assert os.path.isfile(os.path.join(directory, 'group_02', 'experiment_000010', 'file_01'))
    assert os.path.isfile(os.path.join(directory, 'group_02', 'experiment_000010', 'exp_10_file_02'))
    assert os.path.isfile(os.path.join(directory, 'group_02', 'experiment_000010', 'extra_file_01'))
    assert os.path.isfile(os.path.join(directory, 'group_02', 'experiment_000010', 'extra_file_02'))

    assert os.path.isfile(os.path.join(directory, 'group_02', 'experiment_000030', 'file_01'))
    assert os.path.isfile(os.path.join(directory, 'group_02', 'experiment_000030', 'exp_30_file_02'))
    assert os.path.isfile(os.path.join(directory, 'group_02', 'experiment_000030', 'extra_file_01'))
    assert os.path.isfile(os.path.join(directory, 'group_02', 'experiment_000030', 'extra_file_02'))

    # file content
    with open(os.path.join(directory, 'group_01', 'experiment_000001', 'file_01'), 'r') as file:
        file_content = file.read()
    assert 'file 1:\n1\n0\n1\nguten\n' == file_content

    with open(os.path.join(directory, 'group_01', 'experiment_000001', 'exp_1_file_02'), 'r') as file:
        file_content = file.read()
    assert 'file 2:\n3\nvielen\n' == file_content

    with open(os.path.join(directory, 'group_01', 'experiment_000003', 'file_01'), 'r') as file:
        file_content = file.read()
    assert 'file 1:\n3\n0\n5\ntag\n' == file_content

    with open(os.path.join(directory, 'group_01', 'experiment_000003', 'exp_3_file_02'), 'r') as file:
        file_content = file.read()
    assert 'file 2:\n7\ndank\n' == file_content

    with open(os.path.join(directory, 'group_02', 'experiment_000010', 'file_01'), 'r') as file:
        file_content = file.read()
    assert 'file 1:\n10\n0\n10\nguten\n' == file_content

    with open(os.path.join(directory, 'group_02', 'experiment_000010', 'exp_10_file_02'), 'r') as file:
        file_content = file.read()
    assert 'file 2:\n30\nvielen\n' == file_content

    with open(os.path.join(directory, 'group_02', 'experiment_000030', 'file_01'), 'r') as file:
        file_content = file.read()
    assert 'file 1:\n30\n0\n50\ntag\n' == file_content

    with open(os.path.join(directory, 'group_02', 'experiment_000030', 'exp_30_file_02'), 'r') as file:
        file_content = file.read()
    assert 'file 2:\n70\ndank\n' == file_content


def test_generate_experiments_default_values(tmpdir):
    # test the non default copy operator cp

    dir_path = os.path.dirname(os.path.realpath(__file__))

    # change working directory to this path
    os.chdir(dir_path)

    ################################################
    # test 1

    directory = os.path.join(tmpdir.strpath, 'test_default_values')

    eu.manage.generate_experiment_files(
        os.path.join(dir_path, 'test_default_values.ods'),
        directory=directory
    )

    # experiment folder folders
    assert os.path.isdir(os.path.join(directory, 'experiment_000001'))
    assert os.path.isdir(os.path.join(directory, 'experiment_000003'))

    # experiment files
    assert os.path.isfile(os.path.join(directory, 'experiment_000001', 'file_default_values'))
    assert os.path.isfile(os.path.join(directory, 'experiment_000003', 'file_default_values'))

    # file content
    with open(os.path.join(directory, 'experiment_000001', 'file_default_values'), 'r') as file:
        file_content = file.read()
    assert 'file default values:\n1\ndefault 2\n' == file_content

    with open(os.path.join(directory, 'experiment_000003', 'file_default_values'), 'r') as file:
        file_content = file.read()
    assert 'file default values:\n\'default 1\'\nhello\n' == file_content


def test_generate_experiments_remove_lines(tmpdir):
    # test the non default copy operator cp

    dir_path = os.path.dirname(os.path.realpath(__file__))

    # change working directory to this path
    os.chdir(dir_path)

    ################################################
    # test 1

    directory = os.path.join(tmpdir.strpath, 'test_remove_lines')

    eu.manage.generate_experiment_files(
        os.path.join(dir_path, 'test_remove_lines.ods'),
        directory=directory
    )

    # experiment folder folders
    assert os.path.isdir(os.path.join(directory, 'experiment_000001'))
    assert os.path.isdir(os.path.join(directory, 'experiment_000003'))

    # experiment files
    assert os.path.isfile(os.path.join(directory, 'experiment_000001', 'file_remove_lines'))
    assert os.path.isfile(os.path.join(directory, 'experiment_000003', 'file_remove_lines'))

    # file content
    with open(os.path.join(directory, 'experiment_000001', 'file_remove_lines'), 'r') as file:
        file_content = file.read()
    assert 'file remove lines:\n1\n' == file_content

    with open(os.path.join(directory, 'experiment_000003', 'file_remove_lines'), 'r') as file:
        file_content = file.read()
    assert 'file remove lines:\n3\n' == file_content

