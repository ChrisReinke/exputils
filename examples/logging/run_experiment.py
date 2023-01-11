##
## This file is part of the exputils package.
##
## Copyright: INRIA
## Year: 2022, 2023
## Contact: chris.reinke@inria.fr
##
## exputils is provided under GPL-3.0-or-later
##
import exputils
import  exputils.data.logging as log
from sub_experiment import run_subexperiment

def run_experiment():
    n_sub_experiments = 4

    for exp_idx in range(n_sub_experiments):

        log.add_value('experiment_idx', exp_idx)
        run_subexperiment()

    log.save()


def display_log():

    # load the saved logging
    mylog = exputils.data.Logger()
    mylog.load()

    for prop_name, prop_values in mylog.items():
        print('{}: {}'.format(prop_name, prop_values))


if __name__ == '__main__':
    run_experiment()
    display_log()

