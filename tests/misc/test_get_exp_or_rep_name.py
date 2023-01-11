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


def _check_get_experiment_name(path, experiment_name):

    if experiment_name is None:
        experiment_name = 'is None'
    else:
        experiment_name = '== \'' + experiment_name + '\''

    f = open(os.path.join(path,'check_experiment_name.py'), 'a')
    f.writelines([
        'import exputils as eu', '\n',
        '', '\n',
        'if __name__ == \'__main__\':', '\n',
        '   assert eu.misc.get_experiment_name() ' + experiment_name, '\n',
    ])
    f.close()

    os.chdir(path)

    subprocess.check_output(['python', 'check_experiment_name.py'])


def _check_get_repetition_name(path, repetition_name):

    if repetition_name is None:
        repetition_name = 'is None'
    else:
        repetition_name = '== \'' + repetition_name + '\''

    f = open(os.path.join(path,'check_repetition_name.py'), 'a')
    f.writelines([
        'import exputils as eu', '\n',
        '', '\n',
        'if __name__ == \'__main__\':', '\n',
        '   assert eu.misc.get_repetition_name() ' + repetition_name, '\n',
    ])
    f.close()

    os.chdir(path)

    subprocess.check_output(['python', 'check_repetition_name.py'])


def test_tensorboard_logging(tmp_path):
    """
    Creates an experiments folder structure:
        experiments/experiment_000001/repetition_000000

    Creates under each subdir, a code file that checks if the experiment name and repetition name are correctly identified
    """

    assert eu.misc.get_experiment_name() is None
    assert eu.misc.get_repetition_name() is None

    ##
    experiments_dir = tmp_path / eu.DEFAULT_EXPERIMENTS_DIRECTORY
    experiments_dir.mkdir()

    _check_get_experiment_name(str(experiments_dir), None)
    _check_get_repetition_name(str(experiments_dir), None)

    ##
    experiment_dir = experiments_dir / eu.EXPERIMENT_DIRECTORY_TEMPLATE.format(1)
    experiment_dir.mkdir()

    _check_get_experiment_name(str(experiment_dir), 'experiment_000001')
    _check_get_repetition_name(str(experiment_dir), None)

    ##
    repetition_0_dir = experiment_dir / eu.REPETITION_DIRECTORY_TEMPLATE.format(0)
    repetition_0_dir.mkdir()

    _check_get_experiment_name(str(repetition_0_dir), 'experiment_000001')
    _check_get_repetition_name(str(repetition_0_dir), 'repetition_000000')