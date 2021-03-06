from torch import nn
from torch.optim import Adam
from trunk.pyt_nasnet.shared_cnn import CNN
from sklearn.metrics import accuracy_score
import numpy as np


class NetManager:
    def __init__(self, num_input,
                 in_channel,
                 num_classes,
                 learning_rate,
                 train_loader,
                 test_loader,
                 device,
                 bathc_size=100):

        self.num_input = num_input
        self.in_channel = in_channel
        self.num_classes = num_classes
        self.learning_rate = learning_rate
        self.train_loader = train_loader
        self.test_loader = test_loader

        self.bathc_size = bathc_size
        self.device = device

    def get_reward(self, action):
        mean_val_acc = []
        model = CNN(self.num_input, self.in_channel, self.num_classes, action).to(self.device)
        loss_func = nn.CrossEntropyLoss()
        optimizer = Adam(model.parameters(), lr=self.learning_rate)
        model.train()
        for i in range(1):
            for step, (tx, ty) in enumerate(self.train_loader):
                tx = tx.to(self.device)
                optimizer.zero_grad()
                to = model(tx)
                loss = loss_func(to, ty.to(self.device))
                loss.backward()
                optimizer.step()
                # if step % 100 == 0:
                #     out = np.argmax(to.cpu().detach().numpy(), axis=1)
                #     y = ty.cpu().detach().numpy()
                #     print("Step " + str(step) +
                #           ", Minibatch Loss= " + "{:.4f}".format(loss) +
                #           ", Current accuracy= " + "{:.3f}".format(accuracy_score(y, out)))
            model.eval()
            for step, (tx, ty) in enumerate(self.test_loader):
                tx = tx.to(self.device)
                to = model(tx)
                out = np.argmax(to.cpu().detach().numpy(), axis=1)
                val_acc = accuracy_score(ty.cpu().detach().numpy(), out)
                mean_val_acc.append(val_acc)
        return np.mean(mean_val_acc)
