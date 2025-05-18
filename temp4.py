# == Full Implementation (concatenated steps) ==
import numpy as np
import pandas as pd
from typing import Tuple
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset
# ----- Data Preprocessing -----
# Load and fix CSV formatting
with open('multithreaded_memory_log_BT7274_BT7274.csv','r') as f:
    lines = f.readlines()
header = lines[0].strip().split(',')
raw_lines = lines[1:]
fixed_lines, buffer = [], ""
for line in raw_lines:
    if buffer:
        buffer += line.strip()
        if buffer.count(',') == len(header)-1:
            fixed_lines.append(buffer)
            buffer = ""
        else:
            continue
    else:
        if line.count(',') == len(header)-1:
            fixed_lines.append(line.strip())
        else:
            buffer = line.strip()
data = pd.DataFrame([l.split(',') for l in fixed_lines], columns=header)
for col in ['Timestamp','RAM_Usage_MB','Swap_Usage_MB','CPU_Usage','Page_Faults_Delta']:
    dtype = float if col!='Page_Faults_Delta' else int
    data[col] = data[col].astype(dtype)
# Label actions based on RAM change
eps = 1.0
actions = []
for i in range(len(data)-1):
    diff = data.loc[i+1,'RAM_Usage_MB'] - data.loc[i,'RAM_Usage_MB']
    actions.append(2 if diff>eps else 1 if diff<-eps else 0)
actions.append(0)
data['action'] = actions
# Create transitions (s,a,s',r)
states = data[['RAM_Usage_MB','Swap_Usage_MB','CPU_Usage']].values[:-1]
next_states = data[['RAM_Usage_MB','Swap_Usage_MB','CPU_Usage']].values[1:]
actions = np.array(actions[:-1])
rewards = -data['Page_Faults_Delta'].values[1:] # negative page faults
# ----- Environment Proxy -----
class MemoryEnv:
    def __init__(self, states, actions, next_states, rewards):
        self.states = states
        self.actions = actions
        self.next_states = next_states
        self.rewards = rewards
        self.action_indices = {a: np.where(actions == a)[0] for a in np.unique(actions)}
    def reset(self):
        return self.states[0]
    def step(self, state: np.ndarray, action: int) -> Tuple[np.ndarray,float]:
        idxs = self.action_indices.get(action, [])
        if len(idxs) == 0:
            return state, 0.0
        dist = np.sum((self.states[idxs] - state)**2, axis=1)
        best = idxs[np.argmin(dist)]
        return self.next_states[best], self.rewards[best]
env = MemoryEnv(states, actions, next_states, rewards)
# ----- Q-Network and Training -----
class QNetwork(nn.Module):
    def __init__(self, state_dim, action_dim):
        super().__init__()
        self.net = nn.Sequential(
        nn.Linear(state_dim, 64), nn.ReLU(),
        nn.Linear(64, 64), nn.ReLU(),
        nn.Linear(64, action_dim)
        )
    def forward(self, x):
        return self.net(x)