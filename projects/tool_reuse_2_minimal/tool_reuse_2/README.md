# Tool-Reuse-2 minimal local execution code

Continuous Panda/SAPIEN CPU-PhysX task: acquire the same L tool, contact-pull cube1, stably release the tool on the table, regrasp it, then contact-pull cube2 to a goal specified at episode start. No scene reset or robot/object teleport during skill switches.

This source is intended for the existing `/home/users/lemon/TRO/` workspace and its `.conda/tro-baseline` environment with ManiSkill3.0.1. It does not install dependencies or fetch source. Place this `tool_reuse_2` package under that workspace; module commands run from the workspace root.

- `env.py`, `task_config.json`: common task, normal P/Q table poses, public A/B goals and state monitor.
- `controller.py`, `legacy_v2.py`: state-feedback GEO-REPLAN with normal tool regrasp and native screw/RRT motion planning, based on the final M1b v2 patch.
- `state_bc.py`: goal-conditioned state BC with the same `pd_joint_pos` action labels/controller and initial-state-disjoint validation. Checkpoints and all observations/actions stay local.
- `audit.py`, `run_episode.py`: pre-step1200 control-step cap, one-reset/state-write guards, complete local recording and safe finalization.
- `study.py`: reservation-before-launch limit of16 complete physical trials, including process errors/aborts. It refuses duplicate attempts; never clear the attempt ledger to obtain more trials.
- `make_report.py`: local paired legality/cost/feedback checks and conservative stop decision. Action-validation loss is never substituted for physical success.

Entry points, gated in order:
```
.conda/tro-baseline/bin/python -m tool_reuse_2.study 1
# Only if batch1 supports proceeding:
.conda/tro-baseline/bin/python -m tool_reuse_2.state_bc
.conda/tro-baseline/bin/python -m tool_reuse_2.study 2
.conda/tro-baseline/bin/python -m tool_reuse_2.make_report
```
The batch2 caller must obey the task's stop gates. Batch3 is intentionally not auto-launched: it requires reviewing the paired physical evidence and unused budget. No command above grants permission to bypass a stop condition or increase the cap.

The same geometric environment and controller are used throughout. GEO reads privileged exact grasp/contact queries; BC receives flattened state, public goal and phase. This information difference must be disclosed in any comparison. BC's tiny demonstration dataset is only a feasibility baseline; it is not a faithful reproduction of a named paper method.

The source package is published under the user's explicit code-upload instruction. No measured experiment results, model checkpoints, logs, trajectories, videos or local report documents are included. Local output root: `outputs/T2_reuse_one_shot/`. No T1, T2v3, IHCL or other method is modified. ManiSkill's installed native planners and physics definitions are dependencies; `legacy_v2.py` retains the earlier M1b helper provenance.
