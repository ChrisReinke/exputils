TODO

https://pytorch.org/tutorials/beginner/basics/quickstart_tutorial.html


Experiments are stored in a specific folder structure which allows to save and load experimental data in a structured manner.
Please note that  it represents a default structure which can be adapted if required.
Elements in brackets (\<custom name>\) can have custom names.   
Folder structure:
 * **\<main\>** folder: Holds several experimental campaigns. A campaign holds experiments of the same kind but with different parameters.
    * **analyze** folder: Scripts such as Jupyter notebooks to analyze the different experimental campaigns in this main-folder.
    * **\<experimental campaign\>** folders:
        * **analyze** folder: Scripts such as Jupyter notebooks to analyze the different experiments in this experimental campaign. 
        * **experiment_configurations.ods** file: ODS file that contains the configuration parameters of the different experiments in this campaign.
        * **src** folder: Holds code templates of the experiments.
            * **\<repetition code\>** folders: Code templates that are used under the repetition folders of th experiments. These contain the acutal experimental code that should be run.
            * **\<experiment code\>** folders: Code templates that are used under the experiment folder of the experiment. These contain usually code to compute statistics over all repetitions of an experiment.
        * **generate_code.sh** file: Script file that generates the experimental code under the **experiments** folder using the configuration in the **experiment_configurations.ods** file and the code under the **src** folder.               
        * **experiments** folder: Contains generated code for experiments and the collected experimental data.
            * **experiment_{id}** folders:
                * **repetition_{id}** folders:
                    * **data** folder: Experimental data for the single repetitions, such as logs.
                    * code files: Generated code and resource files.
                * **data** folder: Experimental data for the whole experiment, e.g. statistics that are calculated over all repetitions.   
                * **\<code\>** files: Generated code and resource files.
        * **\<run scripts\>.sh** files: Various shell scripts to run experiments and calculate statistics locally or on clusters.




    ./get_status.sh

Output: 

    2024/11/09 20:24:13 ./experiments/experiment_000001/repetition_000000/run_repetition.py.status - running  train epoch 4
    2024/11/09 20:24:15 ./experiments/experiment_000001/repetition_000001/run_repetition.py.status - running  train epoch 4
    2024/11/09 20:24:24 ./experiments/experiment_000001/repetition_000002/run_repetition.py.status - running  train epoch 4
    2024/11/09 20:24:16 ./experiments/experiment_000001/repetition_000003/run_repetition.py.status - running  train epoch 4
    2024/11/09 20:25:06 ./experiments/experiment_000001/repetition_000004/run_repetition.py.status - finished 
    2024/11/09 20:24:39 ./experiments/experiment_000002/repetition_000000/run_repetition.py.status - finished 
    2024/11/09 20:25:09 ./experiments/experiment_000002/repetition_000001/run_repetition.py.status - running  train epoch 5
    2024/11/09 20:25:06 ./experiments/experiment_000002/repetition_000002/run_repetition.py.status - finished 
    2024/11/09 20:24:22 ./experiments/experiment_000002/repetition_000003/run_repetition.py.status - running  train epoch 4
    2024/11/09 20:24:22 ./experiments/experiment_000002/repetition_000004/run_repetition.py.status - running  train epoch 4
    2024/11/09 20:24:40 ./experiments/experiment_000003/repetition_000000/run_repetition.py.status - running 
    2024/11/09 20:25:06 ./experiments/experiment_000003/repetition_000001/run_repetition.py.status - running 
    2024/11/09 20:25:07 ./experiments/experiment_000003/repetition_000002/run_repetition.py.status - running 
    2024/11/09 20:19:42 ./experiments/experiment_000003/repetition_000003/run_repetition.py.status - todo 
    2024/11/09 20:19:42 ./experiments/experiment_000003/repetition_000004/run_repetition.py.status - todo 
    total: 15 | todo: 2 | running: 10 | error: 0 | finished: 3 
