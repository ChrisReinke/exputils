# Experiment Utilities (exputils)

Current version: 0.3.7 (15/11/2024)

Experiment Utilities (exputils) contains various tools for the management of scientific experiments and their experimental data.
It is especially designed to handle experimental repetitions, including to run different repetitions, to effectively store and load data for them, and to visualize their results.  
 
Main features:
* Easy definition of default configurations using nested python dictionaries.
* Setup of experimental configuration parameters using an ODF file (Libreoffice alternative of MS Excel).
* Running experiments and their repetitions in parallel.
* Logging of experimental data (numpy, json) with tensorboard support.
* Loading and filtering of experimental data.
* Interactive Jupyter widgets to load, select and plot data as line, box and bar plots.  

You can find the documentation online: [https://chrisreinke.github.io/exputils/](https://chrisreinke.github.io/exputils/)


## Requirements

Developed and tested on Python 3.11 on Linux (Ubuntu 24) but is compatible also with older Python versions >= 3.8.

Note: Jupter notebook is used for visualization. Due to some constraints (https://github.com/quantopian/qgrid/issues/372) only an older version of Jupyter can be used:
* notebook <= 6.5.6  
* ipywidgets >= 7.5.1,<= 7.6.5


## Installation 

### 1) Exputils Package

Two options are available, either via pip or directly from the source code. 

__PIP (recommended)__

    pip install experiment-utilities

__From Source__

Clone the repository via git and install via pip:
    
    git clone https://github.com/ChrisReinke/exputils.git .
    pip install ./exputils

### 2) Jupiter Notebook

For using the exputils GUIs for loading and plotting of data in Jupyter Notebook, the *qgrid* widget must be activated.
(Note: The GUI is currently only working for Jupyter notebooks <= 6.5.)
Activate *qgrid* with:

    jupyter contrib nbextension install --user
    jupyter nbextension enable --py --sys-prefix widgetsnbextension
    jupyter nbextension enable --py --sys-prefix qgrid

It is recommended to use the [Jupyter Notebooks Extensions](https://github.com/ipython-contrib/jupyter_contrib_nbextensions) to allow folding of code and headlines.
This makes the notebooks more readable.
Activate the extensions with:

    jupyter nbextension enable codefolding/main
    jupyter nbextension enable collapsible_headings/main


## Documentation

The documentation can be found online at [https://chrisreinke.github.io/exputils/](https://chrisreinke.github.io/exputils/).

To generate the documentation MkDocs needs to be installed which can be done via the `docs` option:

    pip install experiment-utilities[docs]

Then run: 

    mkdocs serve
    

## Development

If you wish to further develop the exputils, then it is useful to install it in _editable_ mode and to run its unittests.
Download and install the source code via: 

    git clone https://github.com/ChrisReinke/exputils.git .
    pip install -e ./exputils[test]

To run the tests call:

    pytest