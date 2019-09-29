import torch
import torch.nn as nn
import torch.nn.functional as F


class Reinforce(nn.Module):
    def __init__(self, classes, hidden_size, num_params):
        super(Reinforce, self).__init__()
        self.reward_buffer = []
        self.state_buffer = []
        self.num_params = num_params
        self.embedding = nn.Embedding(classes, hidden_size)
        self.rnn_cell = nn.LSTMCell(hidden_size, hidden_size)
        self.decoders = nn.ModuleList([nn.Linear(hidden_size, classes) for _ in range(num_params)])

    def call_rnn(self, inputs, param_id, hidden_states=None):
        embed = self.embedding(inputs) if param_id != 0 else inputs
        encoded, hidden_states = self.rnn_cell(embed, hidden_states)
        output = self.decoders[param_id](encoded)
        return output, hidden_states

    def forward(self, inputs, hidden_states, is_sample=False):
        outputs = []
        for param_id in range(self.num_params):
            output, hidden_states = self.call_rnn(inputs, param_id, hidden_states)
            action_prob = F.softmax(output, -1)
            inputs = action_prob.multinomial(num_samples=1).data
            outputs.append(inputs) if is_sample else outputs.append(output)
        return torch.stack(tuple(outputs), dim=1)
