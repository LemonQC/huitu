# M1 engineering run statistics
No learning method comparison and no final-test inference. Wilson intervals describe each dev batch only. Repeated states across code versions are not independent new samples.

| Run | Success | Wilson 95% | Status |
|---|---:|---|---|
| T1_v1_pilot24 | 23/24 | [0.798, 0.993] | DEV_ONLY |
| T1_v1_smoke | 3/3 | [0.439, 1.000] | DEV_ONLY |
| T2_v1_controller_fixed | 0/3 | [0.000, 0.561] | DEV_ONLY |
| T2_v1_smoke | 0/3 | [0.000, 0.561] | DEV_ONLY |
| T2_v2_pilot24 | 19/24 | [0.595, 0.908] | DEV_ONLY |
| T2_v2_smoke | 3/3 | [0.439, 1.000] | DEV_ONLY |
| T2_v3_budgeted24 | 12/22 | [0.347, 0.731] | INVALID_BUDGET_OR_INTERRUPTED |
| T2_v3_frame_fixed_smoke | 2/3 | [0.208, 0.939] | DEV_ONLY |
| T2_v3_grasp_fixed_smoke | 0/3 | [0.000, 0.561] | INVALID_BUDGET_OR_INTERRUPTED |
| T2_v3_pilot24 | 5/10 | [0.237, 0.763] | INVALID_BUDGET_OR_INTERRUPTED |
| T2_v3_smoke | 0/3 | [0.000, 0.561] | DEV_ONLY |
| T2_v3_strict_smoke | 1/3 | [0.061, 0.792] | DEV_ONLY |
| audit_smoke | 2/2 | [0.342, 1.000] | DEV_ONLY |
| pilot20 | 19/20 | [0.764, 0.991] | DEV_ONLY |

Recorded completed rows: 126
Unique physical initial-state hashes across these rows: 70

Initial 3-episode collection, official StackCube/Tool smoke and random smoke are additionally preserved in their original CSV/JSON/H5. Interrupted active episodes without a completed CSV row are not silently invented; see completeness_audit.json.