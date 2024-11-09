#!/usr/bin/env bash

function usage {
  echo "Usage: $(basename $0) [-h] [n n_parallel]" 2>&1
  echo "Generates and runs experiments and repetitions."
  echo "  Options:"
  echo "   -h             Shows this message."
  echo "   -n n_parallel  Defines how many processes should be run in parallel if n_parallel is a number."
  echo "                  If True: All experiments and repetitions will be run in parallel."
  echo "                  If False (default): Experiments and repetitions run sequentially."
}

# handle arguments
NUM_PROCESSES=True
while getopts ":hn:" arg; do
  case $arg in
    h) usage ; exit 1 ;;
    n) NUM_PROCESSES=$OPTARG;;
  esac
done

echo "Start experiments ..."
python -c "import exputils

exputils.manage.generate_experiment_files('experiment_configurations.ods', directory='./experiments/')

exputils.manage.start_experiments(
  start_scripts='run_*.py',
  parallel=$NUM_PROCESSES)"

echo "Finished"
