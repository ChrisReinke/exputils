
# Introduction

Experiment Utilities (exputils) contains various tool for the execution of scientific experiments. 


# <a name="team-members"></a>Team Members

* [Chris Reinke](http:www.scirei.net) <chris.reinke@inria.fr>


# <a name="setup"></a>Setup

## <a name="requirements"></a>Requirements

Developed for Python 3.6.

Needs the following additional python packages which will be automatically installed:
* numpy
* [odfpy](https://github.com/eea/odfpy) (Anaconda: https://anaconda.org/conda-forge/odfpy) 
* [defusedxml](https://github.com/tiran/defusedxml) (Anaconda: https://anaconda.org/conda-forge/defusedxml)

## Installation

To install the current version of the library:
`pip install .`

To install the library to allow that changes to the source code are directly usable:
`pip install -e .`


# <a name="documentation"></a>Documentation

## <a name="dev_notes"></a>Generate experiment files to test different configurations / parameters

The function `generate_experiment_files` can be used to generate experiment files for different configurations and parameters.
The parameters can be defined in an ODS file (LibreOffice Spreadsheet)

TODO: More documentation


# TODO
* add code to allow to rerun experiments even if they are finished