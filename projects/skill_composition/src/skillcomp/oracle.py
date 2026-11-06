"""Motion-planning ORACLE candidate for HandoffRegraspStack-v0.

Based on ManiSkill's official Panda StackCube planner. Privileged simulator
geometry is used ONLY for data-generation/physics feasibility, NOT as a learned
method baseline. Runs pd_joint_pos, not the learning-policy controller.
This draft REQUIRES on-server testing and possible API adjustments.
"""
import numpy as np
import sapien
from transforms3d.euler import euler2quat

from mani_skill.examples.motionplanning.panda.motionplanner import PandaArmMotionPlanningSolver
from mani_skill.examples.motionplanning.base_motionplanner.utils import (
    compute_grasp_info_by_obb, get_actor_obb
)


def _try_pose(planner, pose, step_name):
    result = planner.move_to_pose_with_screw(pose)
    if isinstance(result, (int, np.integer)) and result == -1:
        raise RuntimeError(f"Motion planner returned -1 during {step_name}")
    return result


def _grasp_pose(raw, planner):
    obb = get_actor_obb(raw.cubeA)
    approaching = np.array([0, 0, -1])
    closing_axis = raw.agent.tcp.pose.to_transformation_matrix()[0, :3, 1].cpu().numpy()
    info = compute_grasp_info_by_obb(
        obb, approaching=approaching, target_closing=closing_axis, depth=0.025
    )
    pose = raw.agent.build_grasp_pose(
        approaching, info["closing"], info["center"]
    )
    # Reuse the official StackCube fallback search for a kinematically feasible grasp.
    angles = np.arange(0, np.pi * 2 / 3, np.pi / 2)
    angles = np.repeat(angles, 2)
    angles[1::2] *= -1
    for angle in angles:
        candidate = pose * sapien.Pose(q=euler2quat(0, 0, float(angle)))
        candidate_result = planner.move_to_pose_with_screw(candidate, dry_run=True)
        if not (isinstance(candidate_result, (int, np.integer)) and candidate_result == -1):
            return candidate
    raise RuntimeError("No feasible grasp pose for red cube")


def _as_np(tensor):
    return np.asarray(tensor.detach().cpu().numpy()).reshape(-1)


def _current_tcp(raw):
    return raw.agent.tcp.pose.sp


def _transport_cube_to(raw, planner, goal_cube_xyz, step_name):
    current_cube = _as_np(raw.cubeA.pose.p)
    current_tcp = _current_tcp(raw)
    delta = np.asarray(goal_cube_xyz, dtype=float) - current_cube
    target = sapien.Pose(current_tcp.p + delta, current_tcp.q)
    _try_pose(planner, target, step_name)


def _require_phase(raw, expected, action):
    # read evaluator result but do NOT manually set any stage/success
    phase = int(raw.stage_id[0].item())
    if phase < expected:
        raise RuntimeError(f"After {action}, got stage {phase}; expected >= {expected}")


def run_oracle(env, seed, debug=False):
    """One physical episode; reset only here, never at a stage transition."""
    env.reset(seed=int(seed))
    raw = env.unwrapped
    if raw.control_mode not in ("pd_joint_pos", "pd_joint_pos_vel"):
        raise ValueError("Official PandaArmMotionPlanningSolver needs pd_joint_pos control")
    planner = PandaArmMotionPlanningSolver(
        env, debug=debug, vis=False,
        base_pose=raw.agent.robot.pose,
        visualize_target_grasp_pose=False,
        print_env_info=False,
    )
    result = None
    try:
        # Skill 1: grasp and lift red cube
        grasp = _grasp_pose(raw, planner)
        _try_pose(planner, grasp * sapien.Pose([0, 0, -0.05]), "reach1")
        _try_pose(planner, grasp, "grasp1")
        planner.close_gripper(t=10)
        _try_pose(planner, sapien.Pose([0, 0, 0.10]) * grasp, "lift1")
        _require_phase(raw, 1, "pickup")

        # Skill 2: move physically to staging, RELEASE, and wait for stability
        stage_xyz = _as_np(raw.stage_marker.pose.p)
        stage_xyz[2] = 0.02
        _transport_cube_to(raw, planner, stage_xyz, "move-to-staging")
        planner.open_gripper(t=18)
        _require_phase(raw, 2, "physical staging / release")

        # Retreat away from the cube and then pick it again
        tcp = _current_tcp(raw)
        retreat = sapien.Pose(tcp.p + np.array([0.0, 0.0, 0.09]), tcp.q)
        _try_pose(planner, retreat, "retreat-from-staging")

        # Skill 3: new real grasp; no teleports or state restoration
        grasp = _grasp_pose(raw, planner)
        _try_pose(planner, grasp * sapien.Pose([0, 0, -0.05]), "reach2")
        _try_pose(planner, grasp, "grasp2")
        planner.close_gripper(t=10)
        _try_pose(planner, sapien.Pose([0, 0, 0.11]) * grasp, "lift2")
        _require_phase(raw, 3, "regrasp")

        # Skill 4: place red cube on green cube and release
        goal_xyz = _as_np(raw.cubeB.pose.p) + np.array([0.0, 0.0, 0.04])
        _transport_cube_to(raw, planner, goal_xyz, "move-to-stack")
        result = planner.open_gripper(t=20)
        _require_phase(raw, 4, "stack / release")
        return result
    finally:
        planner.close()
