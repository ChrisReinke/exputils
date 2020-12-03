#!/bin/bash

# if param "rerun" is given then rerun all scripts
is_rerun=False
if [ "$1" = "rerun" ]
then
  is_rerun=True
fi

echo "Start experiments via slurm ..."
python -c "import exputils
exputils.manage.start_experiments(
  start_scripts='run_experiment.sh',
  parallel=False,
  is_chdir=True,
  verbose=True,
  post_start_wait_time=0.0,
  is_rerun=$is_rerun)"

echo "Finished"

