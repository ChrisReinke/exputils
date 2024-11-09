import exputils as eu
import exputils.data.logging as log

import torch
from torch.utils.data import DataLoader
from torchvision import datasets
from torchvision.transforms import ToTensor

from .models.neural_network import NeuralNetwork


def run_training(config=None, **kwargs):
    """Runs the training of a pytorch model on some dataset."""

    # exputils: define the default configuration
    default_config = eu.AttrDict(
        seed=None,
        n_epochs=5,
        batch_size=10,
        dataset=eu.AttrDict(
            cls=datasets.FashionMNIST,
            root='./mnist',
        ),
        model=eu.AttrDict(
            cls=NeuralNetwork
        ),
        loss=eu.AttrDict(
            cls=torch.nn.CrossEntropyLoss
        ),
        optimizer=eu.AttrDict(
            cls=torch.optim.SGD,
            lr=0.01
        )
    )

    # exputils: use the seed property in the config to seed random, numpy.random and torch.random
    eu.misc.seed(config)

    #####################################
    # Load Data

    # exputils: combine the given config with the default configuration
    config = eu.combine_dicts(kwargs, config, default_config)

    # exputils: load training data dataset
    training_data = eu.create_object_from_config(
        config.dataset,
        train=True,
        transform=ToTensor(),
    )
    # exputils: load test data dataset
    test_data = eu.create_object_from_config(
        config.dataset,
        train=True,
        transform=ToTensor(),
    )

    train_dataloader = DataLoader(training_data, batch_size=config.batch_size)
    test_dataloader = DataLoader(test_data, batch_size=config.batch_size)

    #####################################
    # Create Model

    # Get cpu, gpu or mps device for training.
    device = (
        "cuda"
        if torch.cuda.is_available()
        else "mps"
        if torch.backends.mps.is_available()
        else "cpu"
    )
    print(f"Using {device} device")

    # exputils: create model from config
    model = eu.create_object_from_config(config.model).to(device)

    #####################################
    # Optimizing the Model Parameters

    loss_fn = eu.create_object_from_config(config.loss)
    optimizer = eu.create_object_from_config(config.optimizer, model.parameters())

    # do a test with a random model before first training
    test(test_dataloader, model, loss_fn, device)

    for t in range(config.n_epochs):
        # exputils: update the status of the experiment in the status file
        eu.update_status(f"train epoch {t+1}")

        print(f"Epoch {t+1}\n-------------------------------")
        train(train_dataloader, model, loss_fn, optimizer, device)
        test(test_dataloader, model, loss_fn, device)

    # exputils: save the log
    log.save()

    print("Done!")


def train(dataloader, model, loss_fn, optimizer, device):
    size = len(dataloader.dataset)
    model.train()
    for batch, (X, y) in enumerate(dataloader):
        X, y = X.to(device), y.to(device)

        # Compute prediction error
        pred = model(X)
        loss = loss_fn(pred, y)

        # Backpropagation
        loss.backward()
        optimizer.step()
        optimizer.zero_grad()

        loss = loss.item()
        if batch % 100 == 0:
            current = (batch + 1) * len(X)
            print(f"loss: {loss:>7f}  [{current:>5d}/{size:>5d}]")

        # exputils: log the loss of each training batch with exputils
        log.add_value('train/loss', loss)


def test(dataloader, model, loss_fn, device):
    size = len(dataloader.dataset)
    num_batches = len(dataloader)
    model.eval()
    test_loss, correct = 0, 0
    with torch.no_grad():
        for X, y in dataloader:
            X, y = X.to(device), y.to(device)
            pred = model(X)
            test_loss += loss_fn(pred, y).item()
            correct += (pred.argmax(1) == y).type(torch.float).sum().item()
    test_loss /= num_batches
    correct /= size
    print(f"Test Error: \n Accuracy: {(100*correct):>0.1f}%, Avg loss: {test_loss:>8f} \n")

    # exputils: log the accuracy and loss of each test evaluation with exputils
    log.add_value('test/accuracy', 100*correct)
    log.add_value('test/loss', test_loss)