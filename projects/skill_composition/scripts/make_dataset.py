#!/usr/bin/env python3
"""Extract flat state->action BC samples from REPLAYED ManiSkill3 HDF5.

Must use a replay in obs_mode=state AND same controller pd_ee_delta_pose.
This tool fails loudly on omitted obs; does not generate fake samples.
"""
import argparse
import json
from pathlib import Path
import h5py
import numpy as np


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--traj", required=True, help="Replayed trajectory H5 with state observations")
    p.add_argument("--out", default="outputs/stackcube_state_bc.npz")
    p.add_argument("--expected-controller", default="pd_ee_delta_pose")
    a = p.parse_args()
    src = Path(a.traj)
    meta = src.with_suffix(".json")
    if not meta.exists():
        raise FileNotFoundError(f"Trajectory JSON metadata required: {meta}")
    info = json.loads(meta.read_text(encoding="utf-8"))
    env_info = info.get("env_info", {})
    # Store metadata rather than guessing if the version's schema differs.
    controller = str(env_info.get("env_kwargs", {}).get("control_mode", ""))
    if controller and controller != a.expected_controller:
        raise ValueError(f"Controller mismatch: {controller} != {a.expected_controller}")
    xs, ys, ids = [], [], []
    with h5py.File(src, "r") as f:
        groups = sorted((k for k in f.keys() if k.startswith("traj_")), key=lambda s: int(s.split("_")[-1]))
        for index, key in enumerate(groups):
            group = f[key]
            if "obs" not in group or not isinstance(group["obs"], h5py.Dataset):
                raise ValueError(f"{key} lacks a flat obs array: replay with -o state and --save-traj")
            obs = np.asarray(group["obs"], dtype=np.float32)
            acts = np.asarray(group["actions"], dtype=np.float32)
            if obs.ndim != 2 or acts.ndim != 2 or obs.shape[0] != acts.shape[0] + 1:
                raise ValueError(f"{key} has inconsistent obs/action shapes {obs.shape}/{acts.shape}")
            xs.append(obs[:-1])
            ys.append(acts)
            ids.append(np.full((len(acts),), index, dtype=np.int32))
    if not xs:
        raise ValueError("No trajectories found")
    x, y, ep = np.concatenate(xs), np.concatenate(ys), np.concatenate(ids)
    if not np.isfinite(x).all() or not np.isfinite(y).all():
        raise ValueError("NaN / Inf encountered in demonstration")
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(out, obs=x, actions=y, episode_ids=ep)
    print(f"Saved {out} | episodes={len(xs)} steps={len(x)} obs={x.shape[1]} actions={y.shape[1]}")
    print("Check original JSON and replay metadata before training. This data alone does NOT show skill composition.")


if __name__ == "__main__":
    main()
