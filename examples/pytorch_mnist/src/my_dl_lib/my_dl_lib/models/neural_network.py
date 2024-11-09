import exputils as eu
from torch import nn

class NeuralNetwork(nn.Module):

    @staticmethod
    def default_config():
        # exputils: This method defined the default configuration of the class.
        #           It is used in the __init__ method to set defaults.
        return eu.AttrDict(
            n_hidden_neurons=512
        )

    def __init__(self, config=None, **kwargs):
        super().__init__()

        # exputils: combine the given config with the default config
        self.config = eu.combine_dicts(kwargs, config, self.default_config())

        # exputils: create the network structure with the number of hidden neurons according
        #           to the configuration
        self.flatten = nn.Flatten()
        self.linear_relu_stack = nn.Sequential(
            nn.Linear(28*28, self.config.n_hidden_neurons),
            nn.ReLU(),
            nn.Linear(self.config.n_hidden_neurons, self.config.n_hidden_neurons),
            nn.ReLU(),
            nn.Linear(self.config.n_hidden_neurons, 10)
        )

    def forward(self, x):
        x = self.flatten(x)
        logits = self.linear_relu_stack(x)
        return logits