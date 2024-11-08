Current version: 0.3.6 (05/11/2024)

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

Developed and tested on Python 3.11 on Linux (Ubuntu 24) but is compatible also with older Python versions.

Note: Jupter notebook is used for visualization. Due to some constraints only an older version of Jupyter can be used:
* notebook <= 6.5.6  
* ipywidgets >= 7.5.1,<= 7.6.5  # needs older version due to https://github.com/quantopian/qgrid/issues/372


## Installation 

__1) Exputils__

*Via PIP*

    pip install experiment-utilities

*From Source*

Clone the repository via git and install via pip:
    
    git clone git@gitlab.inria.fr:creinke/exputils.git .
    pip install ./exputils

(To install the library as a developer so that changes to its source code are directly usable in other projects:
`pip install -e ./exputils`)


__2) Jupiter Notebook__

For using the exputils GUIs for loading and plotting of data in Jupyter Notebook, the *qgrid* widget must be activated.
(Note: The GUI is currently only tested for Jupyter notebooks. For Jupyterlab, other installation procedures are necessary.)
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

To generate the documentation manually from the source code use MkDocs which needs to be installed: 
 * mkdocs: `pip install mkdocs`
 * mkdocs python handler: `pip install mkdocstrings-python`
 * material template: `pip install mkdocs-material`

Then run: `mkdocs serve`

## Development

If you wish to further develop the exputils or adapt them, then it is useful to run its unittests.
They are written for pytest which needs to be installed:
 * pytest: `pip install pytest`

To run all tests (otherwise some will be skipped), you need some additional packages:
 * torch: `pip install torch`