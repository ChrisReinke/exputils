#!/bin/bash

# registers the current repetition as a job to the OAR scheduler

##########################
# Parameters
WALLTIME=$EU_PRJ_INRIA_CLUSTER_DEFAULT_WALLTIME
CLUSTER=$EU_PRJ_INRIA_CLUSTER_DEFAULT_CLUSTER
RUN_REPETITION_SCRIPT=$EU_PRJ_DEFAULT_RUN_REPETITION_SCRIPT

##########################
# Execution

while getopts ":w:c" arg; do
  case $arg in
    w) WALLTIME=$OPTARG;;
    c) CLUSTER=$OPTARG;;
  esac
done

# identify if the repetition needs to run to only create a job if necessary
NUM_REPETITIONS_TO_EXECUTE=`eu_gricad_python -c "
import exputils

n_scripts = exputils.manage.get_number_of_scripts_to_execute(
  directory='.',
  start_scripts='$RUN_REPETITION_SCRIPT')

print(n_scripts)"`

if [ $NUM_REPETITIONS_TO_EXECUTE -gt 0 ]; then

  # Create a script that runs the job. It has two features:
  # 1) identify if the repetition still has to run
  # 2) activate the conda environment
  echo "NUM_REPETITIONS_TO_EXECUTE=\`eu_inria_singularity python -c \"
import exputils

n_scripts = exputils.manage.get_number_of_scripts_to_execute(
  directory='.',
  start_scripts='$RUN_REPETITION_SCRIPT')

print(n_scripts)\"\`

if [ \$NUM_REPETITIONS_TO_EXECUTE -gt 0 ]; then
  eu_inria_singularity ./\$EU_PRJ_DEFAULT_RUN_REPETITION_SCRIPT
fi" > oar_job_run_repetition.sh
  chmod +x oar_job_run_repetition.sh

  echo "Register current repetition as a job ..."
  oarsub -l /host=1/gpudevice=1,walltime=$WALLTIME -p "cluster='$CLUSTER'" -t besteffort --stdout inria_cluster_run_repetition.out.log --stderr inria_cluster_run_repetition.err.log ./oar_job_run_repetition.sh
  echo "Finished."
fi