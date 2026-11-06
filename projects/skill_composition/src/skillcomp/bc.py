"""Simple BC-MLP reference. This is *not* STAP/GSC/SPIN or an official RoboMimic implementation."""
import torch
from torch import nn


class BCMLP(nn.Module):
    def __init__(self, in_dim, out_dim, hidden=256):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(in_dim, hidden),
            nn.ReLU(),
            nn.Linear(hidden, hidden),
            nn.ReLU(),
            nn.Linear(hidden, out_dim),
            nn.Tanh(),
        )

    def forward(self, x):
        return self.net(x)


def load_policy(path, device="cpu"):
    pack = torch.load(path, map_location=device, weights_only=True)
    model = BCMLP(int(pack["in_dim"]), int(pack["out_dim"]), int(pack["hidden"])).to(device)
    model.load_state_dict(pack["model"])
    model.eval()
    mean = pack["mean"].to(device)
    std = pack["std"].to(device)

    @torch.no_grad()
    def act(obs):
        x = torch.as_tensor(obs, dtype=torch.float32, device=device)
        x = x.reshape(-1, int(pack["in_dim"]))
        return model((x - mean) / std).cpu().numpy()

    return act, pack
