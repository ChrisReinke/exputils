# Manage

Functions to manage the generation and execution of experiments.

All functions can be accessed under the module: ``exputils.manage``

## Generation & Execution 

::: exputils.manage.experimentgenerator

::: exputils.manage.experimentstarter
    options:
        members:
            - start_experiments

## Helper

A couple of extra functions exist that can be used to determine how to best start experiments.
For example by identifying how many scripts need to be executed and asking a cluster manager to 
provide to required resources such as the number of cores.

::: exputils.manage.experimentstarter
    options:
        members:
            - get_scripts
            - get_script_status
            - get_number_of_scripts
            - get_number_of_scripts_to_execute
