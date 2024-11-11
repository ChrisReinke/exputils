#!/bin/bash

echo "Start experiments via slurm ..."
python -c "import exputils
exputils.manage.start_experiments(
  start_scripts='calc_statistics_per_experiment.sh',
  parallel=False,
  is_chdir=True,
  verbose=True,
  post_start_wait_time=0.0)"

echo "Finished"

