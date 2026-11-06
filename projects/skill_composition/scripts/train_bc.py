#!/usr/bin/env python3
"""Deterministic, episode-disjoint BC-MLP pilot trainer with validation-only checkpoint selection."""
import argparse
from pathlib import Path
import numpy as np
import torch
from torch.utils.data import DataLoader, TensorDataset
from skillcomp.bc import BCMLP
from skillcomp.utils import split_episode_ids, set_seed, save_json


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--data", required=True)
    p.add_argument("--epochs", type=int, default=100)
    p.add_argument("--batch-size", type=int, default=256)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    p.add_argument("--checkpoint", default="outputs/bc_best.pt")
    p.add_argument("--hidden", type=int, default=256)
    p.add_argument("--lr", type=float, default=0.0003)
    a = p.parse_args()
    set_seed(a.seed)
    pack = np.load(a.data)
    x, y, ep = pack["obs"], pack["actions"], pack["episode_ids"]
    tr, va = split_episode_ids(ep, val_fraction=0.2, seed=a.seed)
    mean = x[tr].mean(axis=0)
    std = np.maximum(x[tr].std(axis=0), 1e-5)
    x = ((x - mean) / std).astype(np.float32)
    device = torch.device(a.device)
    model = BCMLP(x.shape[1], y.shape[1], hidden=a.hidden).to(device)
    optim = torch.optim.Adam(model.parameters(), lr=a.lr)
    ds = TensorDataset(torch.as_tensor(x[tr]), torch.as_tensor(y[tr]))
    dl = DataLoader(ds, batch_size=a.batch_size, shuffle=True)
    val_x = torch.as_tensor(x[va], device=device)
    val_y = torch.as_tensor(y[va], device=device)
    best = float("inf")
    history = []
    path = Path(a.checkpoint)
    path.parent.mkdir(parents=True, exist_ok=True)
    for epoch in range(a.epochs):
        model.train()
        losses = []
        for bx, by in dl:
            pred = model(bx.to(device))
            loss = ((pred - by.to(device)) ** 2).mean()
            optim.zero_grad(set_to_none=True)
            loss.backward()
            optim.step()
            losses.append(float(loss.item()))
        model.eval()
        with torch.no_grad():
            val_loss = float(((model(val_x) - val_y) ** 2).mean().item())
        history.append({"epoch": epoch + 1, "train_mse": float(np.mean(losses)), "val_mse": val_loss})
        if val_loss < best:
            best = val_loss
            torch.save({
                "model": model.state_dict(),
                "in_dim": x.shape[1], "out_dim": y.shape[1], "hidden": a.hidden,
                "mean": torch.as_tensor(mean, dtype=torch.float32),
                "std": torch.as_tensor(std, dtype=torch.float32),
                "train_seed": a.seed, "val_mse": best,
                "identity": "PROXY", "env": "StackCube-v1",
                "controller": "pd_ee_delta_pose",
            }, path)
        if epoch == 0 or (epoch + 1) % 10 == 0:
            print(f"epoch={epoch+1} train={history[-1]['train_mse']:.6f} val={val_loss:.6f}")
    save_json(path.with_suffix(".json"), {
        "data": a.data, "train_episodes": int(len(np.unique(ep[tr]))),
        "val_episodes": int(len(np.unique(ep[va]))), "best_val_mse": best,
        "seed": a.seed, "epochs": a.epochs, "checkpoint": str(path),
        "note": "Model identity PROXY; NOT a full skill-composition algorithm.",
        "history": history,
    })
    print(f"Best validation MSE {best:.6f}, saved {path}")


if __name__ == "__main__":
    main()
