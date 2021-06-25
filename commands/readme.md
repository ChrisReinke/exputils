# Exputils Commands


## General Commands

#### eu_activate

Activates the given project for which a project file with the same name needs to exists under *exputils/projects*.
Needs to be called using the source command.

__Example:__ 

    source eu_activate MY_PROJECT 

#### eu_active_project

Prints the name of the active project.

__Example:__

    eu_active_project
    > MY_PROJECT


## Local Commands

The following commands operate locally.

#### eu_local_generate_experiments

Creates the experimental files for all configurations listed in the _experiments_configuration.ods_ of an experiments folder.
Existing code that matches the IDs in the _experiment_configuration.ods_ will be overwritten, but the command will not delete any files. 

__Example:__

    eu_local_generate_experiments

    
#### eu_local_run_experiments

Runs experiment repetitions under the current experiment folder on the local machine.
Ignores repetitions that have been already finished or that are currently running.

Options:

* _-n_ NUMBER: Number of processes (repetitions) that should run in parallel.
               If not specified, then the EU_PRJ_LOCAL_DEFAULT_NUM_PROCESSES from the project configuration file are used. 
* _-r_: Run all experiments, including already finished experiments.

__Examples:__

Default:

    eu_local_run_experiments

Rerun all experiments:

    eu_local_run_experiments -r

Run experiments using 3 parallel processes:

    eu_local_run_experiments -n 3
