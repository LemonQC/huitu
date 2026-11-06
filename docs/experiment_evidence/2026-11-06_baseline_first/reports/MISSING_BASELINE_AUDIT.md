# Missing baseline audit

All algorithm work is gated by M1. The unresolved condition is a reliable second physical task family, not permission to download or write code.

| Method | Available evidence | Missing implementation | Next prerequisite |
|---|---|---|---|
| STAP | Paper + official MIT source locally pinned | Skill Q training, dynamics, sequence CEM port, identity/unit/physical validation | M1 then M2 reliable skills/data; original PyBullet run separately |
| GSC | Paper + official MIT source locally pinned | Joint skill diffusion training, chained sampler, constraints and physical replay | M1 then M2; original PyBullet setup separately |
| Skill-RRT / SPIN | Paper/project verified, no official repo identified in this audit | Applicability, connectors, RRT; then noise replay/distillation | M1/M2 + suitable connector data; paper-based identity if no official code |
| DP | Official project identified in input | Action diffusion/normalization/rolling controller | M1/M2 controller-consistent data |
| ACT | Paper identified in input | CVAE/action chunks/temporal ensemble, feasibility trial | M1/M2 |
| FutureQ+CEM / replanning | Protocol specification | Goal/skill interfaces and matched compute budget | M1/M2 |

Training GPU-hour estimates are NOT_MEASURED, not invented. Current training GPU hours=0. Workload estimates require successful data/skill smoke before scheduling expensive training. More available source does not authorize skipping M1.

Compose-by-Focus audit: complete archive download was interrupted after spending excessive time; targeted public source downloads succeeded. Commit66a3c810552648e8f420d094ed03664341c43671 and exact selected paths are recorded in references/compose_audit/manifest.json. README says ManiSkill2, while actual selected source uses mani_skill batched APIs; this discrepancy needs real compatibility validation, not a blanket engine-version assumption.
