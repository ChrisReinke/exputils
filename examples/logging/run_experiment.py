import exputils
from exputils.logging import log
from sub_experiment import run_subexperiment

def run_experiment():
    n_sub_experiments = 4

    for exp_idx in range(n_sub_experiments):

        log.add_value('experiment_idx', exp_idx)
        run_subexperiment()

    log.save()


def display_log():

    # load the saved logging
    mylog = exputils.logging.Logger()
    mylog.load()

    for prop_name, prop_values in mylog.items():
        print('{}: {}'.format(prop_name, prop_values))


if __name__ == '__main__':
    run_experiment()
    display_log()

