#!/usr/bin/env bash

function usage {
  echo "Usage: $(basename $0) [-h]" 2>&1
  echo "Generates experiments using a ./experiment_configurations.ods file in the ./experiments/ directory."
  echo "  Options:"
  echo "   -h           Shows this message."
}

# handle arguments
while getopts ":h" arg; do
  case $arg in
    h) usage ; exit 1 ;;
  esac
done

echo "Generate experiments ..."
python -c "import exputils
exputils.manage.generate_experiment_files('experiment_configurations.ods', directory='./experiments/')"

echo "Finished."
