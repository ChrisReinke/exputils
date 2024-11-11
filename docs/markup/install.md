# Installation

## 1) Exputils Package

Two options are available, either via pip or directly from the source code. 

__PIP (recommended)__

    pip install experiment-utilities

__From Source__

Clone the repository via git and install via pip:
    
    git clone https://github.com/ChrisReinke/exputils.git .
    pip install ./exputils

(To install the library as a developer so that changes to the exputils source code are directly usable in other projects use
`pip install -e ./exputils`)


## 2) Jupiter Notebook

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