#!/usr/bin/env python3
"""Instantiates custom continuous task and executes REAL random physics.

This is only an API/scene smoke test. A working oracle must be added before
training/benchmarking, and random failure does not establish a research gap.
"""
import argparse
import csv
from pathlib import Path

import gymnasium as gym
import mani_skill.envs
import skillcomp.handoff_env  # registers HandoffRegraspStack-v0
from skillcomp.utils import as_bool, to_numpy


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--episodes", type=int, default=2)
    p.add_argument("--steps", type=int, default=30)
    p.add_argument("--out", default="outputs/handoff_smoke.csv")
    a = p.parse_args()
    env = gym.make(
        "HandoffRegraspStack-v0",
        num_envs=1, obs_mode="state", control_mode="pd_ee_delta_pose",
        sim_backend="physx_cpu", reward_mode="sparse", render_mode=None,
    )
    rows = []
    try:
        for k in range(a.episodes):
            obs, _ = env.reset(seed=150000 + k)
            info = {}
            steps = 0
            for t in range(a.steps):
                obs, _, terminated, truncated, info = env.step(env.action_space.sample())
                steps = t + 1
                if as_bool(terminated) or as_bool(truncated) or as_bool(info["success"]):
                    break
            row = {
                "seed": 150000 + k, "steps": steps,
                "stage": int(to_numpy(info["stage_id"]).reshape(-1)[0]),
                "success": int(as_bool(info["success"])),
                "identity": "RANDOM_SMOKE",
            }
            rows.append(row)
            print(row)
    finally:
        env.close()
    dest = Path(a.out)
    dest.parent.mkdir(parents=True, exist_ok=True)
    with dest.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print("Scene check finished. DO NOT claim this environment has a verified successful oracle.")


if __name__ == "__main__":
    main()
