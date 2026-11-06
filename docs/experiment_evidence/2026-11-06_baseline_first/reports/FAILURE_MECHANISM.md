# Failure mechanisms — tentative engineering diagnosis only

No M4 causal experiment was run. No claimed compositional generalization gap.

1. `INTERFACE_OR_IMPLEMENTATION`: inherited SSH DISPLAY caused both initial physics processes to SIGSEGV; headless environment variables fixed this. Pure evaluator/state serialization and action budget issues were independently corrected/tested. Native tool planner can return empty paths and downstream callers ignore truncation.
2. `CONTACT_DYNAMICS` (tentative): T2v2 episodes14/17 have negligible cube displacement and no measured tool-cube contact; episode10 tool z≈0.0696m and nonstatic at supposed table return, consistent with obstructed settling. Additional causal interventions are needed before identifying grasp/contact as the unique cause.
3. `REACHABILITY` (tentative): pipeline seed220017 and T1 seed230023 planner failures. An IK/path search failure is not proof the state is physically infeasible.
4. `TIMEOUT_BUDGET`: v3 trial batches exceeded600 steps because upstream planner ignored truncation and first spec-based guard saw no limit. Explicit limit + actual 2-step integration test fixed enforcement. Prior overbudget trajectories remain invalid for performance comparison.
5. `UNKNOWN`: planner random source was not uniformly controlled; several source changes coincide. Inter-version changes cannot be interpreted as controlled causal effects.

Successful T1 and T2 trajectories are retained alongside failures. Review examples in videos_index.md; all original videos remain uncut. Only selected storyboard frames plus numeric final-state/contact checks were inspected here; the required five full-success/five full-failure frame-by-frame review is not complete, another reason not to accept M1.

T1's square-block symmetry and freely reachable intermediate region have not established a need for long-term physical reasoning. T2 has not demonstrated a stable reusable tool skill. Changing tolerances or removing difficult seeds to manufacture a gap would invalidate the study; neither was done.
