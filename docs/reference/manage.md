# Manage

Functions to manage the generation and execution of experiments.

All functions can be accessed under the module: ``exputils.manage``




Experiments are recommended to be stored in a specific folder structure which allows to save and load experimental data in a structured manner.
Please note that it represents a default structure which can be adapted if required.
Elements in brackets (<custom name\>) can have custom names. 

Folder structure:

* **<experiments\>** folder: Holds all your campaigns.
    * **<experimental campaign\>** folders:
        * **<analyze\>** folder: Scripts such as Jupyter notebooks to analyze the different experiments in this experimental campaign. 
        * **experiment_configurations.ods** file: ODS file that contains the configuration parameters of the different experiments in this campaign.
        * **src** folder: Holds code templates of the experiments.
            * **rep** folder: Code templates that are used under the repetition folders of th experiments. These contain the acutal experimental code that should be run.
            * **exp** folder: Code templates that are used under the experiment folder of the experiment. These contain usually code to compute statistics over all repetitions of an experiment.
        * **experiments** folder: Contains generated code for experiments and the collected experimental data.
            * **experiment_{id}** folders:
                * **repetition_{id}** folders:
                    * **data** folder: Experimental data for the single repetitions, such as logs.
                    * code files: Generated code and resource files.





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

::: exputils.manage.misc
    options:
        members:
            - get_number_of_scripts
            - get_number_of_scripts_to_execute
            - get_experiments_status
