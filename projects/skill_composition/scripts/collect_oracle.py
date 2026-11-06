#!/usr/bin/env python3
"""Collect candidate, real motion-planned trajectories for continuous task.

No false-success filling: failed episodes are explicitly reported, and full
evaluation comes from env.success. This is a prototype, not a tested oracle.
"""
import argparse
import json
import time
from pathlib import Path

import gymnasium as gym
import mani_skill.envs  # noqa
import skillcomp.handoff_env
from mani_skill.utils.wrappers.record import RecordEpisode
from skillcomp.oracle import run_oracle
from skillcomp.utils import as_bool, save_json


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--episodes", type=int, default=3)
    p.add_argument("--seed", type=int, default=200000)
    p.add_argument("--record-dir", default="outputs/oracle")
    p.add_argument("--video", action="store_true")
    p.add_argument("--debug", action="store_true")
    a = p.parse_args()
    if a.episodes < 1:
        p.error("--episodes must be positive")
    Path(a.record_dir).mkdir(parents=True, exist_ok=True)
    env = gym.make(
        "HandoffRegraspStack-v0",
        num_envs=1, obs_mode="none",
        control_mode="pd_joint_pos", sim_backend="physx_cpu",
        reward_mode="sparse", max_episode_steps=400,
        render_mode="rgb_array" if a.video else None,
    )
    env = RecordEpisode(
        env, output_dir=a.record_dir, save_video=a.video,
        save_trajectory=True, trajectory_name="handoff_oracle",
        save_on_reset=True, source_type="motionplanning",
        source_desc="Experimental Panda motion planner for continuous handoff regrasp stack",
    )
    records = []
    try:
        for ep in range(a.episodes):
            started = time.monotonic()
            error = ""
            try:
                run_oracle(env, seed=a.seed + ep, debug=a.debug)
            except Exception as exc:
                error = f"{type(exc).__name__}: {exc}"
                print(f"Episode {ep} FAILED: {error}")
            raw = env.unwrapped
            # stage_id comes only from physical phase transitions, never assigned here.
            stage = int(raw.stage_id[0].item())
            success = (stage == 4)
            record = {
                "seed": a.seed + ep, "stage": stage,
                "complete_success": success, "error": error,
                "walltime_seconds": round(time.monotonic() - started, 3),
            }
            records.append(record)
            print(record)
    finally:
        env.close()
    save_json(Path(a.record_dir) / "oracle_report.json", {
        "environment": "HandoffRegraspStack-v0",
        "identity": "PRIVILEGED_ORACLE",
        "controller": "pd_joint_pos", "episodes": records,
        "total_success": sum(x["complete_success"] for x in records),
        "warning": "Unverified candidate; success is never filled from geometry alone. Needs video inspection and independent reset audit.",
    })
    print(f"Verified success flags {sum(x['complete_success'] for x in records)}/{len(records)}; inspect video and failure logs before using data.")


if __name__ == "__main__":
    main()
