
Current version: 0.2.0 (01/12/2020)

# Introduction

Experiment Utilities (exputils) contains various tools for the management of scientific experiments and their experimental data.
It is especially designed to handle experimental repetitions, including to run different repetitions and to effectively store and load data for them.  
 
Main features:
* Setup of experimental configuration parameters using an ODF file.
* Running of experiments and their repetitions locally or on clusters.
* Logging of experimental data (numpy, json).
* Loading and filtering of experimental data.
* Interactive Jupyter widgets to load, select and plot data as line, box and bar plots.  

# <a name="setup"></a>Setup

## <a name="requirements"></a>Requirements

Developed and tested for Python 3.6.

Needs several additional python packages which will be automatically installed during the installation:
* numpy
* [odfpy](https://github.com/eea/odfpy) (Anaconda: https://anaconda.org/conda-forge/odfpy) 
* [defusedxml](https://github.com/tiran/defusedxml) (Anaconda: https://anaconda.org/conda-forge/defusedxml)

## Installation

To install the current version of the library:
`pip install .`

To install the library to allow that changes to the source code are directly usable:
`pip install -e .`

Jupyter Gui extensions:

`conda install -c plotly plotly` 

`jupyter nbextension enable --py widgetsnbextension`

# <a name="overview"></a>Overview

Besides the exputils package contains the project also example code and unittests. 
It is recommended to look at these items to learn about the usage of the exputils components. 

The exputils package has the following structure:
 - **manage**: Managing of experiments. Generation of experiments from ODS configurations and source templates. Running of experiments and repetitions (can be used to run experiments on clusters.)   
 - **data**: Logging and loading of experimental data including filtering of data. 
 - **gui**: GUI components for Jupyter to load and plot experimental data.
 - **misc**: Miscellaneous helper functions.
 - **io**: Input-output functions to save and load data of various formats, including numpy, json.

Experiments are stored in a specific folder structure which allows to save and load experimental data in a structured manner.
Please note that  it represents a default structure which can be adapted if required.
Elements in brackets (\<custom name>\) can have custom names.   
Folder structure:
 * **\<main folder\>**: Holds several experimental campaigns. A campaign holds experiments of the same kind but with different parameters.
    * **analyze**: Scripts such as Jupyter notebooks to analyze the different experimental campaigns in this main-folder.
    * **\<experimental campaign\>** folders:
        * **analyze**: Scripts such as Jupyter notebooks to analyze the different experiments in this experimental campaign. 
        * **experiment_configurations.ods**: ODS file that contains the configuration parameters of the different experiments in this campaign.
        * **src**: Holds code templates of the experiments.
            * **\<repetition code\>**: Code templates that are used under the repetition folders of th experiments. These contain the acutal experimental code that should be run.
            * **\<experiment code\>**: Code templates that are used under the experiment folder of the experiment. These contain usually code to compute statistics over all repetitions of an experiment.
        * **generate_code.sh**: Script file that generates the experimental code under the **experiments** folder using the configuration in the **experiment_configurations.ods** file and the code under the **src** folder.               
        * **experiments**: Contains generated code for experiments and the collected experimental data.
            * **experiment_{id}** folders:
                * **repetition_{id}** folders:
                    * **data**: Experimental data for the single repetitions, such as logs.
                    * code files: Generated code and resource files.
                * **data**: Experimental data for the whole experiment, e.g. statistics that are calculated over all repetitions.   
                * code files: Generated code and resource files.
        * run scripts: Various possible shell scripts to run experiments and calculate statistics.

# <a name="team-members"></a>Development Team

* [Chris Reinke](http:www.scirei.net) <chris.reinke@inria.fr>