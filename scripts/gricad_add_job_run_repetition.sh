#!/bin/bash

# registers the current repetition as a job to the OAR scheduler

##########################
# Parameters

NUM_PROCESSES=$EU_PRJ_GRICAD_DEFAULT_NUM_PROCESSES
WALLTIME=$EU_PRJ_GRICAD_DEFAULT_WALLTIME
PROJECT=$EU_PRJ_GRICAD_DEFAULT_PROJECT

##########################
# Execution

while getopts ":n:w:r" arg; do
  case $arg in
    n) NUM_PROCESSES=$OPTARG;;
    w) WALLTIME=$OPTARG;;
  esac
done


# before executing the actual script, we need to activate the conda environment
# this has to be done in a extra script that is called by the OAR system
# this script activates the conda env and then executes the repetition
echo "
CONDA_ENV=\$EU_PRJ_GRICAD_DEFAULT_CONDA_ENV

if ! command -v conda &> /dev/null
then
  source /applis/environments/conda.sh
fi

if [ \"\$CONDA_DEFAULT_ENV\" != \"\$CONDA_ENV\" ]; then
  conda activate \$CONDA_ENV
fi

./\$EU_PRJ_DEFAULT_RUN_REPETITION_SCRIPT" > oar_job_run_repetition.sh
chmod +x oar_job_run_repetition.sh

echo "Register current repetition as a job ..."
oarsub -l /nodes=1/core=$NUM_PROCESSES,walltime=$WALLTIME --project $PROJECT --stdout gricad_run_repetition.out.log --stderr gricad_run_repetition.err.log ./oar_job_run_repetition.sh
echo "Finished."
