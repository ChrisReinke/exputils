#!/bin/bash 


echo "Generate experiments ..."
python -c "import exputils
exputils.run.generate_experiment_files()"

echo "Finished."

#$SHELL
