#!/bin/bash

# registers the current repetition as a job to the OAR scheduler

##########################
# Parameters

NUM_PROCESSES=$EU_PRJ_GRICAD_DEFAULT_NUM_PROCESSES
WALLTIME=$EU_PRJ_GRICAD_DEFAULT_WALLTIME
PROJECT=$EU_PRJ_GRICAD_DEFAULT_PROJECT
RUN_REPETITION_SCRIPT=$EU_PRJ_DEFAULT_RUN_REPETITION_SCRIPT

##########################
# Execution

while getopts ":n:w:r" arg; do
  case $arg in
    n) NUM_PROCESSES=$OPTARG;;
    w) WALLTIME=$OPTARG;;
  esac
done

echo "Register current repetition as a job ..."
oarsub -l /nodes=1/core=$NUM_PROCESSES,walltime=$WALLTIME --project $PROJECT --stdout gricad_run_repetition.out.log --stderr gricad_run_repetition.err.log ./$RUN_REPETITION_SCRIPT
echo "Finished."
