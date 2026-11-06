#!/usr/bin/env python3
"""Evaluate checkpoint on real ManiSkill3 episodes with unique reset seeds."""
import argparse
import numpy as np
from skillcomp.bc import load_policy
from skillcomp.bench import StackCubePilot
from skillcomp.utils import save_rows, set_seed


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--checkpoint", required=True)
    p.add_argument("--episodes", type=int, default=20)
    p.add_argument("--steps", type=int, default=160)
    p.add_argument("--base-seed", type=int, default=500000)
    p.add_argument("--device", default="cpu")
    p.add_argument("--out", default="outputs/eval_bc.csv")
    a = p.parse_args()
    set_seed(42)
    policy, ckpt = load_policy(a.checkpoint, device=a.device)
    env = StackCubePilot(max_episode_steps=a.steps)
    results = []
    try:
        for k in range(a.episodes):
            obs, _ = env.reset(seed=a.base_seed + k)
            for _ in range(a.steps):
                # State observation from official ManiSkill is batched (1, D).
                action = np.clip(policy(obs), -1, 1)
                obs, _, done, _ = env.step(action)
                if done:
                    break
            row = env.rec.to_dict()
            row.update({
                "method": "bc_mlp", "identity": "PROXY",
                "task": "StackCube-Pilot", "train_seed": ckpt["train_seed"],
            })
            results.append(row)
            print(f"reset={row['reset_seed']} task_success={row['complete_success']} stage={env.rec.stage_reached}")
    finally:
        env.close()
    save_rows(a.out, results)
    print(f"Completed {a.episodes} distinct reset seeds; full success: {sum(r['complete_success'] for r in results)}/{len(results)}")
    print("No publication-level conclusion: single-skill official demo, pilot stage definitions only.")


if __name__ == "__main__":
    main()
