#!/usr/bin/env python3
"""Smoke test of genuine ManiSkill3 physics + reproducible CSV; random policy NOT a scientific baseline."""
import argparse
import sys
from pathlib import Path
from skillcomp.bench import StackCubePilot
from skillcomp.utils import save_rows, set_seed


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--episodes", type=int, default=2)
    parser.add_argument("--steps", type=int, default=20)
    parser.add_argument("--out", default="outputs/smoke.csv")
    parser.add_argument("--sim-backend", default="physx_cpu")
    a = parser.parse_args()
    if a.episodes < 1 or a.steps < 1:
        parser.error("--episodes and --steps must be positive")
    set_seed(42)
    env = StackCubePilot(max_episode_steps=max(160, a.steps), sim_backend=a.sim_backend)
    rows = []
    try:
        for i in range(a.episodes):
            env.reset(seed=100000 + i)
            for _ in range(a.steps):
                _, _, done, _ = env.step(env.sample_action())
                if done:
                    break
            row = env.rec.to_dict()
            row.update({"method": "random", "identity": "PROXY", "task": "StackCube-Pilot"})
            rows.append(row)
            print(row)
    finally:
        env.close()
    save_rows(a.out, rows)
    print(f"Wrote {len(rows)} real physics episodes to {Path(a.out).resolve()}")


if __name__ == "__main__":
    main()
