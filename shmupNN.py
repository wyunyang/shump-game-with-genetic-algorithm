import torch
import torch.nn as nn
import random

class Net(nn.Module):
    def __init__(self, n_input, n_hidden1, n_hidden2, n_output, weights):
        super(Net, self).__init__()

        self.a = n_input
        self.b = n_hidden1
        self.c = n_hidden2
        self.d = n_output

        self.fc1 = nn.Linear(n_input, n_hidden1)
        self.fc2 = nn.Linear(n_hidden1, n_hidden2)
        self.out = nn.Linear(n_hidden2, n_output)
        self.relu = nn.ReLU()
        self.sigmoid = nn.Sigmoid()

        self.update_weights(weights)

    def update_weights(self, weights):
        weights = torch.FloatTensor(weights)

        with torch.no_grad():
            x = self.a * self.b
            xx = x + self.b
            y = xx + self.b * self.c
            yy = y + self.c
            z = yy + self.c * self.d
            via = weights[0:x]
            self.fc1.weight.data = via.reshape(self.b, self.a)
            self.fc1.bias.data = weights[x:xx]
            via = weights[xx:y]
            self.fc2.weight.data = via.reshape(self.c, self.b)
            self.fc2.bias.data = weights[y:yy]
            via = weights[yy:z]
            self.out.weight.data = via.reshape(self.d, self.c)
            self.out.bias.data = weights[z:]

    def forward(self, x):
        y = self.fc1(x)
        y = self.relu(y)
        y = self.fc2(y)
        y = self.relu(y)
        y = self.out(y)
        y = self.sigmoid(y)
        return y
    
    def predict(self, input):
        input = torch.tensor([input]).float()
        y = self(input)
        return torch.argmax(y, dim=1).tolist()[0]