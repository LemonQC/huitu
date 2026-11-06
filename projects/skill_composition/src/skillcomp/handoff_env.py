"""Handoff→regrasp→stack task in ONE continuous SAPIEN scene.

EXPERIMENTAL v0.1: needs oracle validation and may require ManiSkill API adjustments.
Simulator stages are goal/metric state; no object teleport between stages.
"""
import sapien
import torch

from mani_skill.envs.tasks.tabletop.stack_cube import StackCubeEnv
from mani_skill.utils.building import actors
from mani_skill.utils.registration import register_env
from mani_skill.utils.structs.pose import Pose


@register_env("HandoffRegraspStack-v0", max_episode_steps=200)
class HandoffRegraspStackEnv(StackCubeEnv):
    """Panda pick A -> stage and RELEASE A -> regrasp A -> stack A on B.

    This first revision is task-engineering work, not proof of a novel algorithm.
    Stage labels can be used as evaluation-only ground truth.
    """
    SUPPORTED_ROBOTS = ["panda", "panda_wristcam"]

    def __init__(self, *args, **kwargs):
        self.stage_id = None
        kwargs.setdefault("robot_uids", "panda")
        super().__init__(*args, **kwargs)

    def _load_scene(self, options: dict):
        super()._load_scene(options)
        self.stage_marker = actors.build_box(
            scene=self.scene,
            half_sizes=[0.055, 0.055, 0.001],
            color=[0.2, 0.35, 1.0, 0.5],
            name="stage_marker",
            body_type="kinematic",
            add_collision=False,
            initial_pose=sapien.Pose(p=[0.05, -0.15, 0.001]),
        )

    def _initialize_episode(self, env_idx: torch.Tensor, options: dict):
        # The only allowed teleport/set_pose is during episode reset.
        super()._initialize_episode(env_idx, options)
        if self.stage_id is None:
            self.stage_id = torch.zeros(self.num_envs, dtype=torch.long, device=self.device)
        self.stage_id[env_idx] = 0
        b = len(env_idx)
        with torch.device(self.device):
            pos_a = torch.zeros((b, 3))
            pos_b = torch.zeros((b, 3))
            # Controlled, collision-free regions, to be broadened only after oracle validation.
            pos_a[:, 0] = -0.14 + (torch.rand(b) - 0.5) * 0.03
            pos_a[:, 1] = -0.02 + (torch.rand(b) - 0.5) * 0.03
            pos_b[:, 0] = 0.14 + (torch.rand(b) - 0.5) * 0.03
            pos_b[:, 1] = 0.10 + (torch.rand(b) - 0.5) * 0.03
            pos_a[:, 2] = 0.02
            pos_b[:, 2] = 0.02
            quat = torch.tensor([[1.0, 0.0, 0.0, 0.0]]).repeat(b, 1)
            self.cubeA.set_pose(Pose.create_from_pq(p=pos_a, q=quat))
            self.cubeB.set_pose(Pose.create_from_pq(p=pos_b, q=quat))
            marker = torch.zeros((b, 3))
            marker[:, 0] = 0.05
            marker[:, 1] = -0.15
            marker[:, 2] = 0.001
            self.stage_marker.set_pose(Pose.create_from_pq(p=marker))

    def evaluate(self):
        original = super().evaluate()
        if self.stage_id is None:
            # Framework may inspect the env before the first seeded reset.
            self.stage_id = torch.zeros(self.num_envs, dtype=torch.long, device=self.device)
        old = self.stage_id.clone()
        a = self.cubeA.pose.p
        b = self.cubeB.pose.p
        is_grasped = original["is_cubeA_grasped"].bool()
        flat_xyz = self.stage_marker.pose.p
        on_marker = torch.linalg.norm(a[:, :2] - flat_xyz[:, :2], dim=-1) <= 0.037
        on_table = torch.abs(a[:, 2] - 0.02) < 0.012
        is_static = self.cubeA.is_static(lin_thresh=1e-2, ang_thresh=0.5)

        pickup = (old == 0) & is_grasped & (a[:, 2] >= 0.065)
        staged = (old == 1) & on_marker & on_table & is_static & (~is_grasped)
        regrasp = (old == 2) & is_grasped & (a[:, 2] >= 0.065)
        stacked = (old == 3) & original["success"].bool()

        next_stage = old + pickup.long() + staged.long() + regrasp.long() + stacked.long()
        self.stage_id = next_stage
        success = next_stage == 4
        original.update({
            "success": success,
            "stage_id": next_stage,
            "phase_pick": next_stage >= 1,
            "phase_staged": next_stage >= 2,
            "phase_regrasp": next_stage >= 3,
            "phase_stack": next_stage >= 4,
            "staging_xy_distance": torch.linalg.norm(a[:, :2] - flat_xyz[:, :2], dim=-1),
        })
        return original

    def _get_obs_extra(self, info: dict):
        obs = super()._get_obs_extra(info)
        # If task phase is publicly observable, make it available equally to all methods.
        if self.stage_id is None:
            self.stage_id = torch.zeros(self.num_envs, dtype=torch.long, device=self.device)
        if "state" in self.obs_mode:
            obs.update(
                stage_onehot=torch.nn.functional.one_hot(self.stage_id.clamp(0, 4), num_classes=5).float(),
                staging_marker_pose=self.stage_marker.pose.raw_pose,
            )
        return obs
