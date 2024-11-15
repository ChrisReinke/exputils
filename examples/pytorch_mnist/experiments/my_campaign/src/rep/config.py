import exputils as eu
import my_dl_lib
import torch
from torchvision import datasets
from torch import nn

# config for the my_dl_lib.run_training function
config = eu.AttrDict(
    # the seed if each repetition is different to have different network parameter initializations
    seed = <repetition_id>,

    # number of epochs with default of 5
    n_epochs = <n_epochs,10>,

    # batch size with default of 10
    batch_size = <batch_size,10>,

    # the loss and dataset is the same for all experiments in this campaign
    dataset = eu.AttrDict(
        cls = datasets.FashionMNIST,
        root = '../../../../../datasets/mnist'
    ),
    loss = eu.AttrDict(
        cls = nn.CrossEntropyLoss
    ),

    # as models can have different parameters, we allow to set them generally through the
    # <model_parameters> placeholder, which can have a list of them, for example: "n_layers=3, n_neurons=128"
    model = eu.AttrDict(
        cls = my_dl_lib.models.<model>,
        <model_parameters>
    ),

    optimizer = eu.AttrDict(
        cls = torch.optim.<optimizer>,
        lr = <lr>,
    ),
)
