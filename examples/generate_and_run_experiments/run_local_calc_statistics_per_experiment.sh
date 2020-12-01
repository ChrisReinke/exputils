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
  start_scripts='calc_statistics_per_experiment.sh',
  is_parallel=False,
  is_chdir=True,
  verbose=True,
  post_start_wait_time=0.5,
  is_rerun=$is_rerun)"

echo "Finished"

