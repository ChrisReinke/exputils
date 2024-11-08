# Welcome to ExpUtils

Version: `0.3.6`

The Experiment Utilities (exputils) contain various tools for the management of scientific experiments and their experimental data. 
It is especially designed to handle experimental repetitions, including to run different repetitions, to effectively store and load data for them, and to visualize their results.

__Main features:__

 - Easy definition of default configurations using nested python dictionaries.
 - Setup of experimental configuration parameters with an ODS file for [Libreoffice](https://www.libreoffice.org/) (open-source alternative to MS Excel).
 - Running experiments and their repetitions in parallel.
 - Logging of experimental data (numpy, json) with tensorboard support.
 - Loading and filtering of experimental data.
 - Interactive Jupyter widgets to load, select and plot data as line, box and bar plots.

You can find the project with its source code here: [github.com/ChrisReinke/exputils](https://github.com/ChrisReinke/exputils) 

## Getting Started

## Installation

__1) Exputils Package__

*Via PIP*

    pip install experiment-utilities

(Unfortunately the name 'exputils' was already taken.)

*From Source*

Clone the repository via git and install via pip:
    
    git clone https://github.com/ChrisReinke/exputils.git .
    pip install ./exputils

(To install the library as a developer so that changes to its source code are directly usable in other projects:
`pip install -e ./exputils`)


__2) Jupiter Notebook__

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