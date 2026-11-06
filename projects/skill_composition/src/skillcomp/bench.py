"""Physical-continuity *pilot* based on the official ManiSkill StackCube scene.

Not the planned publication benchmark. No reset between stages.
The stage monitor uses simulator state ONLY for evaluation, not the policy input.
"""
from dataclasses import dataclass, field

import numpy as np

from .utils import as_bool, to_numpy


STAGES = ("pick", "transport", "stack")


@dataclass
class EpisodeRecord:
    seed: int
    episode_steps: int = 0
    stage_reached: int = 0
    complete_success: bool = False
    simulator_done: bool = False
    events: list = field(default_factory=list)
    last_state: dict = field(default_factory=dict)

    def to_dict(self):
        return {
            "reset_seed": self.seed,
            "steps": self.episode_steps,
            "stage_pick": int(self.stage_reached >= 1),
            "stage_transport": int(self.stage_reached >= 2),
            "stage_stack": int(self.stage_reached >= 3),
            "complete_success": int(self.complete_success),
            "simulator_done": int(self.simulator_done),
            "events": "|".join(f"{x['stage']}@{x['t']}" for x in self.events),
            "last_state": str(self.last_state),
        }


class StackCubePilot:
    """Three sequential stage labels in ONE real StackCube physical episode."""

    def __init__(self, max_episode_steps=160, sim_backend="physx_cpu"):
        import gymnasium as gym
        import mani_skill.envs  # noqa: F401; registers official environments

        self.env = gym.make(
            "StackCube-v1",
            num_envs=1,
            obs_mode="state",
            control_mode="pd_ee_delta_pose",
            robot_uids="panda",
            sim_backend=sim_backend,
            render_mode=None,
            max_episode_steps=max_episode_steps,
        )
        self.rec = None
        self.obs = None
        self.done = False

    def reset(self, seed):
        self.obs, info = self.env.reset(seed=int(seed))
        self.rec = EpisodeRecord(seed=int(seed))
        self.done = False
        return self.obs, info

    def _physical_state(self):
        raw = self.env.unwrapped
        a = np.asarray(to_numpy(raw.cubeA.pose.p)).reshape(-1, 3)[0]
        b = np.asarray(to_numpy(raw.cubeB.pose.p)).reshape(-1, 3)[0]
        held = as_bool(raw.agent.is_grasping(raw.cubeA))
        return a, b, held

    def step(self, action):
        if self.done:
            raise RuntimeError("step() called after episode termination; reset first")
        obs, reward, terminated, truncated, info = self.env.step(action)
        self.rec.episode_steps += 1
        a, b, held = self._physical_state()
        stage = self.rec.stage_reached

        # Stages are evaluated successively, not retrospectively.
        if stage == 0 and held and a[2] > 0.055:
            self.rec.stage_reached = 1
            self.rec.events.append({"stage": STAGES[0], "t": self.rec.episode_steps})
        elif stage == 1 and held and np.linalg.norm(a[:2] - b[:2]) < 0.060 and a[2] > b[2] + 0.055:
            self.rec.stage_reached = 2
            self.rec.events.append({"stage": STAGES[1], "t": self.rec.episode_steps})
        elif stage == 2 and as_bool(info.get("success", False)):
            self.rec.stage_reached = 3
            self.rec.complete_success = True
            self.rec.events.append({"stage": STAGES[2], "t": self.rec.episode_steps})

        self.rec.last_state = {
            "cube_a_xyz": np.round(a, 4).tolist(),
            "cube_b_xyz": np.round(b, 4).tolist(),
            "grasped": bool(held),
        }
        self.obs = obs
        self.done = bool(self.rec.complete_success or as_bool(terminated) or as_bool(truncated))
        self.rec.simulator_done = bool(as_bool(terminated) or as_bool(truncated))
        return obs, reward, self.done, info

    def sample_action(self):
        return self.env.action_space.sample()

    def close(self):
        self.env.close()
