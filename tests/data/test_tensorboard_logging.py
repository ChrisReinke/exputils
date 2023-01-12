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
import subprocess
import glob


def _create_no_tb_logging_test_code(path):
    f = open(path, 'a')
    f.writelines([
        'import exputils.data.logging as log', '\n',
        '', '\n',
        'if __name__ == \'__main__\':', '\n',
        '   log.add_value(\'val\', 100)', '\n',
        '   log.add_scalar(\'val2\', 100)', '\n',
        '   log.save()' '\n',
    ])
    f.close()


def _create_nonactive_tb_logging_test_code(path):
    f = open(path, 'a')
    f.writelines([
        'import exputils.data.logging as log', '\n',
        '', '\n',
        'if __name__ == \'__main__\':', '\n',
        '   log.create_tensorboard()', '\n',
        '   log.add_value(\'cata/val\', 100)', '\n',
        '   log.add_scalar(\'val2\', 100)', '\n',
        '   log.save()' '\n',
    ])
    f.close()


def _create_active_tb_logging_test_code(path):
    f = open(path, 'a')
    f.writelines([
        'import exputils.data.logging as log', '\n',
        '', '\n',
        'if __name__ == \'__main__\':', '\n',
        '   log.activate_tensorboard()', '\n',
        '   log.add_value(\'val\', 100)', '\n',
        '   log.add_scalar(\'cat/val\', 100)', '\n',
        '   log.save()' '\n',
    ])
    f.close()


def _create_extra_tb_logging_test_code(path):
    f = open(path, 'a')
    f.writelines([
        'import exputils.data.logging as log', '\n',
        '', '\n',
        'if __name__ == \'__main__\':', '\n',
        '   log.create_tensorboard()', '\n',
        '   log.tensorboard().add_scalar(\'val\', 25)', '\n',
        '   log.save()' '\n',
    ])
    f.close()


def test_tensorboard_logging(tmp_path):
    """
    Creates an experiments folder structure:
        experiments/experiment_000001
            /repetition_000000
            /repetition_000001
            /repetition_000002
            /repetition_000003

    Creates under each a python file that
        repetition_000000 - no logging to tb
        repetition_000001 - no active logging to tb
        repetition_000002 - active logging to tb
        repetition_000003 - extra logging to tb without logging to exputils log

    Checks if tb log gets created and filled if automatic logging is active.
    """

    experiments_dir = tmp_path / eu.DEFAULT_EXPERIMENTS_DIRECTORY
    experiments_dir.mkdir()

    experiment_dir = experiments_dir / eu.EXPERIMENT_DIRECTORY_TEMPLATE.format(1)
    experiment_dir.mkdir()

    ###############################
    # repetition without tb logging
    repetition_0_dir = experiment_dir / eu.REPETITION_DIRECTORY_TEMPLATE.format(0)
    repetition_0_dir.mkdir()
    _create_no_tb_logging_test_code(os.path.join(str(repetition_0_dir), 'write_log.py'))
    os.chdir(str(repetition_0_dir))
    subprocess.check_output(['python', 'write_log.py'])

    assert not os.path.exists(str(experiments_dir / 'tensorboard_logs'))

    ###############################
    # repetition with tb but without automatic logging
    repetition_1_dir = experiment_dir / eu.REPETITION_DIRECTORY_TEMPLATE.format(1)
    repetition_1_dir.mkdir()
    _create_nonactive_tb_logging_test_code(os.path.join(str(repetition_1_dir), 'write_log.py'))
    os.chdir(str(repetition_1_dir))
    subprocess.check_output(['python', 'write_log.py'])

    tensorboard_log_dir = experiments_dir / 'tensorboard_logs'
    tensorboard_log_repetition_1_dir = tensorboard_log_dir / 'exp_1' / 'rep_1'

    assert os.path.exists(str(tensorboard_log_dir))
    assert os.path.exists(str(tensorboard_log_repetition_1_dir))
    tblog_files = glob.glob(os.path.join(str(tensorboard_log_repetition_1_dir), '*/*.tblog'))
    assert len(tblog_files) == 1
    empty_tblog_file_size = os.path.getsize(tblog_files[0])

    ###############################
    # repetition with tb with automatic logging
    repetition_2_dir = experiment_dir / eu.REPETITION_DIRECTORY_TEMPLATE.format(2)
    repetition_2_dir.mkdir()
    _create_active_tb_logging_test_code(os.path.join(str(repetition_2_dir), 'write_log.py'))
    os.chdir(str(repetition_2_dir))
    subprocess.check_output(['python', 'write_log.py'])

    tensorboard_log_dir = experiments_dir / 'tensorboard_logs'
    tensorboard_log_repetition_2_dir = tensorboard_log_dir / 'exp_1' / 'rep_2'

    assert os.path.exists(str(tensorboard_log_repetition_2_dir))
    tblog_files = glob.glob(os.path.join(str(tensorboard_log_repetition_2_dir), '*/*.tblog'))
    assert len(tblog_files) == 1
    nonempty_tblog_file_size = os.path.getsize(tblog_files[0])

    assert nonempty_tblog_file_size > empty_tblog_file_size

    ###############################
    # repetition with extra tb
    repetition_3_dir = experiment_dir / eu.REPETITION_DIRECTORY_TEMPLATE.format(3)
    repetition_3_dir.mkdir()
    _create_extra_tb_logging_test_code(os.path.join(str(repetition_3_dir), 'write_log.py'))
    os.chdir(str(repetition_3_dir))
    subprocess.check_output(['python', 'write_log.py'])

    tensorboard_log_dir = experiments_dir / 'tensorboard_logs'
    tensorboard_log_repetition_3_dir = tensorboard_log_dir / 'exp_1' / 'rep_3'

    assert os.path.exists(str(tensorboard_log_repetition_3_dir))
    tblog_files = glob.glob(os.path.join(str(tensorboard_log_repetition_3_dir), '*/*.tblog'))
    assert len(tblog_files) == 1
    nonempty_tblog_file_size = os.path.getsize(tblog_files[0])

    assert nonempty_tblog_file_size > empty_tblog_file_size