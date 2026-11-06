"""Common, deterministic experiment record helpers. No simulator dependency."""
import csv
import json
from pathlib import Path
import random

import numpy as np


def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    try:
        import torch
        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)
    except ImportError:
        pass


def split_episode_ids(episode_ids, val_fraction=0.2, seed=42):
    """Split at the episode level; never shuffle observation frames across splits."""
    distinct = np.unique(np.asarray(episode_ids))
    if len(distinct) < 2:
        raise ValueError("Need at least two *independent episodes* for train/validation split")
    rng = np.random.default_rng(seed)
    distinct = rng.permutation(distinct)
    n_val = max(1, int(round(len(distinct) * val_fraction)))
    if n_val >= len(distinct):
        n_val = len(distinct) - 1
    val = distinct[:n_val]
    train = distinct[n_val:]
    assert not np.intersect1d(train, val).size
    return np.isin(episode_ids, train), np.isin(episode_ids, val)


def to_numpy(value):
    if hasattr(value, "detach"):
        return value.detach().cpu().numpy()
    return np.asarray(value)


def as_bool(value) -> bool:
    a = np.asarray(to_numpy(value))
    if a.size != 1:
        raise ValueError(f"Expected single-environment boolean, got shape {a.shape}")
    return bool(a.item())


def save_rows(path, rows):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = list(rows)
    if not rows:
        raise ValueError("Refusing to write empty result set")
    keys = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(rows)
    return path


def save_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")
