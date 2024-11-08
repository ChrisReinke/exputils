



https://pytorch.org/tutorials/beginner/basics/quickstart_tutorial.html



## Setup

Create a conda environment (you can also use a venv) and activate it:

`conda create -n exputils_demo python=3.11`

`conda activate exputils_demo`

Install the latest exputils library from PyPI:

`pip install experiment-utilities`

For using the exputils GUIs for loading and plotting of data in Jupyter Notebook, the *qgrid* widget must be activated.

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

`pip install -e. ./src/my_dl_lib`

Installing the libray will also install missing packages such as PyTorch and torchvision. 

## Usage

### Download the FashionMNIST dataset

First lets download the FashionMNIST dataset:

    cd datasets
    ./download_mnist.py
    cd ..

Output:

    Downloading http://fashion-mnist.s3-website.eu-central-1.amazonaws.com/train-images-idx3-ubyte.gz
    Downloading http://fashion-mnist.s3-website.eu-central-1.amazonaws.com/train-images-idx3-ubyte.gz to mnist/FashionMNIST/raw/train-images-idx3-ubyte.gz
    100.0%
    Extracting mnist/FashionMNIST/raw/train-images-idx3-ubyte.gz to mnist/FashionMNIST/raw
    
    Downloading http://fashion-mnist.s3-website.eu-central-1.amazonaws.com/train-labels-idx1-ubyte.gz
    Downloading http://fashion-mnist.s3-website.eu-central-1.amazonaws.com/train-labels-idx1-ubyte.gz to mnist/FashionMNIST/raw/train-labels-idx1-ubyte.gz
    Extracting mnist/FashionMNIST/raw/train-labels-idx1-ubyte.gz to mnist/FashionMNIST/raw
    
    Downloading http://fashion-mnist.s3-website.eu-central-1.amazonaws.com/t10k-images-idx3-ubyte.gz
    100.0%
    Downloading http://fashion-mnist.s3-website.eu-central-1.amazonaws.com/t10k-images-idx3-ubyte.gz to mnist/FashionMNIST/raw/t10k-images-idx3-ubyte.gz
    100.0%
    Extracting mnist/FashionMNIST/raw/t10k-images-idx3-ubyte.gz to mnist/FashionMNIST/raw
    
    Downloading http://fashion-mnist.s3-website.eu-central-1.amazonaws.com/t10k-labels-idx1-ubyte.gz
    Downloading http://fashion-mnist.s3-website.eu-central-1.amazonaws.com/t10k-labels-idx1-ubyte.gz to mnist/FashionMNIST/raw/t10k-labels-idx1-ubyte.gz
    Extracting mnist/FashionMNIST/raw/t10k-labels-idx1-ubyte.gz to mnist/FashionMNIST/raw
    
    100.0%




To run experiments go to the 







