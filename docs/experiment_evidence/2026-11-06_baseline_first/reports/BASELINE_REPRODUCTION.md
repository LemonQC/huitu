# Baseline reproduction audit — implementation NOT STARTED (M1 gate)

No performance values exist for learned/planning paper baselines. Source audit is separate from original-environment reproduction and from a unified ManiSkill port. All downloaded public source remains local.

## STAP
Paper: [STAP](https://arxiv.org/abs/2210.12250). Official repository [agiachris/STAP](https://github.com/agiachris/STAP), downloaded commit `0fe0dcbd5ede5ce4ee3d952642f70b5550a0813c`, MIT. Original task NOT_RUN; unified port NOT_IMPLEMENTED.

Read local `stap/planners/utils.py` trajectory evaluation: per-step skill critics, skill decoding and log-sum/exp joint success; `planners/cem.py` provides sequence planning. This is not interchangeable with a local one-step scorer. A future port must retain learned skill Q, dynamics rollout, whole-chain objective, CEM and calibrated physical validation. Official PyBullet dependencies and its symbolic/SCOD stack require separate original-task setup. We have not attempted to install/run them and therefore do not claim an environment failure. Optional uncertainty omission must be disclosed later.

## GSC
[Paper](https://proceedings.mlr.press/v229/mishra23a.html), [official code](https://github.com/generative-skill-chaining/gsc-code), commit `b8f5bc0d44bd453827f3f254ca1b03ec049849c5`, MIT. Original task NOT_RUN; unified port NOT_IMPLEMENTED.

Read local `scripts/eval/eval_hook_reach.py` chained denoising loop and `mixed_diffusion/sde_cont.py`: per-skill transition scores, overlapping state reconciliation with dependency weights, conditioned sampling and feasibility ranking. Official code also contains transition-model conditioning; this does not justify replacing all diffusion/chaining with an MLP. Required future mapping: joint precondition/parameter/effect distributions, diffusion objective, state permutations, overlap composition and geometric constraints. Official PyBullet task geometry/state dimensions differ from Panda low-level execution here.

## SPIN
[Paper](https://proceedings.mlr.press/v305/jung25a.html), [project](https://sites.google.com/view/skill-rrt). Project and targeted searches did not reveal an official code link during this audit; this is not proof no public implementation exists. Original run NOT_RUN; implementation NOT_STARTED.

Paper distinguishes Skill-RRT task/object-pose search, applicability and connectors from policy distillation with noise-based replay. Any future connector-only implementation must not be called full SPIN. A paper-based port needs applicability datasets, goal-conditioned connector policies and disturbance measurements before faithful identification.

## Other requested methods
BC source is an untrained MLP proxy, not verified goal-conditioned skill BC. DP, ACT, FutureQ and normal replanning remain NOT_RUN_GATE_M1. No checkpoints were created. No simplified method is entered under a paper method's name.

## Recent overlap
[OSS skill-seam paper](https://arxiv.org/abs/2610.10810) exists and discusses scene restoration and resumption. This audit verifies its relevance; it does not reproduce its experiments. A future state-vs-visual causal study must distinguish that setting from genuine physical executability. External BOSS/LIBERO numbers are not mixed into our ManiSkill data.

Downloaded archive SHA256 and commits: `references/source_manifest.json`. Original prototype snapshot had no root license file; retained locally under user's supplied recovery instruction. No public redistribution was performed.
