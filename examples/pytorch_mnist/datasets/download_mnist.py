#!/usr/bin/env python

# Download the FashionMNIST dataset to ./mnist

from torchvision import datasets

# Download training data from open datasets.
datasets.FashionMNIST(root="mnist", download=True)