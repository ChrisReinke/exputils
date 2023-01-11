##
## This file is part of the exputils package.
##
## Copyright: INRIA
## Year: 2022, 2023
## Contact: chris.reinke@inria.fr
##
## exputils is provided under GPL-3.0-or-later
##
import exputils as eu
import torch
import os

def test_dill_pytorch_models(tmp_path):
    """Tests if dill io functions can save and load pyTorch models correctly."""

    tmp_path = str(tmp_path)

    n_hidden = 100

    #########################
    # save and load model

    eu.misc.seed(1)

    # create model
    pytorch_model = torch.nn.Sequential(
        torch.nn.Linear(3,n_hidden),
        torch.nn.Linear(n_hidden,n_hidden),
        torch.nn.Linear(n_hidden,1))

    x1 = pytorch_model(torch.tensor([1.0,2.0,3.0])).item()

    # save and load the model
    eu.io.save_dill(
        pytorch_model,
        os.path.join(tmp_path, 'test.dill')
    )
    loaded_pytorch_model = eu.io.load_dill(
        os.path.join(tmp_path, 'test.dill')
    )

    x2 = pytorch_model(torch.tensor([1.0, 2.0, 3.0])).item()

    # check if the model is correctly loaded
    assert x1 == x2


    #########################
    # save and load model, but use state_dict of it

    eu.misc.seed(1)

    # create model
    pytorch_model_org = torch.nn.Sequential(
        torch.nn.Linear(3, n_hidden),
        torch.nn.Linear(n_hidden, n_hidden),
        torch.nn.Linear(n_hidden, 1))

    pytorch_model_copy = torch.nn.Sequential(
        torch.nn.Linear(3, n_hidden),
        torch.nn.Linear(n_hidden, n_hidden),
        torch.nn.Linear(n_hidden, 1))
    pytorch_model_copy.load_state_dict(pytorch_model_org.state_dict())

    x1 = pytorch_model_copy(torch.tensor([1.0, 2.0, 3.0])).item()

    # save and load the model
    eu.io.save_dill(
        pytorch_model,
        os.path.join(tmp_path, 'test.dill')
    )
    loaded_pytorch_model = eu.io.load_dill(
        os.path.join(tmp_path, 'test.dill')
    )

    pytorch_model_copy = torch.nn.Sequential(
        torch.nn.Linear(3, n_hidden),
        torch.nn.Linear(n_hidden, n_hidden),
        torch.nn.Linear(n_hidden, 1))
    pytorch_model_copy.load_state_dict(loaded_pytorch_model.state_dict())

    x2 = pytorch_model_copy(torch.tensor([1.0, 2.0, 3.0])).item()

    # check if the model is correctly loaded
    assert x1 == x2




