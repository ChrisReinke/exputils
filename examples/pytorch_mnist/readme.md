# Exputils Demo: PyTorch - FashionMNIST 

The demo introduces the main functionality of the [exputils](https://github.com/ChrisReinke/exputils) package.
It can also be used as a template for experimental campaigns that use the exputils.

Please follow the exputils tutorial to understand use and understand the demo: https://chrisreinke.github.io/exputils/tutorials/

The demo code is based on the PyTorch tutorial that introduces the basic operations to train a DNN on the example of 
classification: https://pytorch.org/tutorials/beginner/basics/quickstart_tutorial.html

## Setup

Create a conda environment (you can also use a venv) and activate it.

    conda create -n exputils_demo python=3.11
    conda activate exputils_demo

Install the latest exputils library from PyPI.

    pip install experiment-utilities

For using the exputils GUIs to load and plot data in Jupyter Notebook, the *qgrid* widget must be activated.

    jupyter contrib nbextension install --user
    jupyter nbextension enable --py --sys-prefix widgetsnbextension
    jupyter nbextension enable --py --sys-prefix qgrid

It is recommended to use the [Jupyter Notebooks Extensions](https://github.com/ipython-contrib/jupyter_contrib_nbextensions) to allow folding of code and headlines.
This makes the notebooks more readable.
Activate the extensions with:

    jupyter nbextension enable codefolding/main
    jupyter nbextension enable collapsible_headings/main

With this we have finished the installation of the exputils package.

Now, we have to install your custom python library which contains the code that is used in experiments.
In the case of the demo, this is the `my_dl_lib` which is located under `pytorch_mnist/src`.
Here we install it in developer mode (`-e`) so that changes to the code are used when the package is imported by other python code.

    pip install -e. ./src/my_dl_lib

Installing the libray will also install missing packages such as PyTorch and torchvision. 

## Usage

### Download the FashionMNIST dataset

First lets download the FashionMNIST dataset:

    cd datasets
    ./download_mnist.py
    cd ..

### Run Experiments

To generate, run and get the status of the experiments use the bash scripts in the experimental campaign folder:

    cd ./experiments/my_campaign

To generate the code for experiments under the `./experiments` folder without executing them:

    ./generate_experiments.sh 

To run experiments (and generate their code if not done so far):

    ./run_experiments.sh

To run experiments in parallel on several cores use the `-n` option to define how many should run in parallel:
 
    ./run_experiments.sh -n 10

To get the status of the experiments:

    ./get_status.sh

### Analyze Experiment Results

After the experiments have finished, you can analyze them by using Jupyter notebook:

    jupyter notebook

Then navigate to the `./analyze` folder under the experimental campaign (_my_campaign_) and start the notebook `analyze.ipynb`.



