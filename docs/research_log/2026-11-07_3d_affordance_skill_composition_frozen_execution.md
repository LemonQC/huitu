> **SUPERSEDED / 已撤回（2026-11-07）**：用户指出本文件的 KeyedPartPickInsert 方案只是抓取/IK/碰撞/插入，缺乏真正的 3D functional affordance。**请勿执行本文件中的 Codex 指令或任务、不要继续开展旧计划中的仿真实验。**替代文件：[真正的功能可供性组合纠正方案](2026-11-07_functional_affordance_composition_correction.md)。原文留存仅用于审计，不代表现行决策。

---

# 2026-11-07 — 技能组合研究冻结执行方案（不可自动改题）

> 状态：研究假设/工程任务书。**尚无实验结果、尚未证明 T-RO 级创新**。
> 本文件仅记录此轮已明确的方向与 Codex 执行安排，不冒充已经实现。
> 本方案独立于既有 Cross-Behavior 研究线，不修改原来的 T1/T2/IHCL 实验证据。

## 0. 为什么这次冻结方向

已审阅 `huitu` 中 M0/M1、M1b、Tool-Reuse-2 的源码与报告：
- 旧 IHCL 任务：多个已适配的 BC/Future-Q-CEM/STAP/GSC 在有限任务配置近乎满分；旧任务区分度不足，适配版本不能称为完整官方复现。
- T1：23/24 开发集 Oracle，但反事实 P/Q 不同时满足同一固定 staging marker，且距离偏好没有反转，**不构成有效科学问题证据**。
- T2：19/24 开发结果，主要受接触/抓取和规划器工程问题影响；修复后仍未证明技能组合固有困难。
- Tool-Reuse-2：代码和报告工具包含双任务反事实，最新仓库源码中的报告生成器写有 NO_NOVEL_GAP 规则；截至本次检查，没有直接核验本次候选方向的任何新物理实验。
- `LemonQC/chatgpts` 访问返回 404，此次无法独立核实该仓库。

决定：**不再以堆叠、工具归位/复用或 IHCL 为核心任务；不复活旧论文方法。**

## 1. 唯一锁定的科学问题

**3D Affordance 引导的跨技能物理可行性规划（不使用 LLM）**

工作标题（待结果支持后再定）：
*3D Affordance-Guided Feasibility Planning for Compositional Robotic Manipulation*

问题：在物体几何非对称且目标操作受接触/空间约束时，一个本身成功的抓取可能改变下游插入技能的可行条件。是否存在**已知、匹配的强几何/前瞻规划基线不能可靠解决**的可重复问题？若不存在，**停止该选题，不为制造差距更换课题**。

禁止提前宣称：“3D affordance 转移预测”本身为新颖贡献；STAP/GSC/TASP/Skill-RRT/affordance 研究已覆盖大量相邻机制。

## 2. 唯一启动任务（先不扩展到第二家族）

在现有 ManiSkill 3.0.1 / SAPIEN / Panda 环境构建
`KeyedPartPickInsert-v0`：

- 非对称键形零件 + 有实体碰撞的狭窄插槽；资产可以用多长方体刚体组合生成，不依赖新的大型数据集。
- 连续物理过程：Grasp → Reorient → Insert，不允许阶段之间 reset、teleport 或对象位姿直接写入。
- 同一个**真实初始状态**，两个都满足第一阶段成功条件的抓取方案 P/Q；两个都正常合法的后继插入目标 A/B（插槽朝向/进入方向可变）。
- 候选抓取的合法性由真实夹爪抓取/抬升/静止判定，插入成功由实际碰撞/深度/姿态/稳定判定。**不可事先人为标记 P 对 A 好、Q 对 B 好**。
- 正常的 IK、碰撞检查、重抓和执行反馈对所有方法开放；不能为了让新方法赢禁用强基线能力。
- 需要记录 object/target/robot 的 6D 状态和局部接触几何；RGB-D/点云作为后续可能引入的正常观测，不在首日成为训练阻碍。

## 3. 执行顺序与硬限制

**D0–D1：只把已有环境复用起来**：
- 沿用已有 `.conda/tro-baseline`（如用户服务器路径仍有效）和固定的 ManiSkill/SAPIEN 版本；不重装、不迁移其他仓库。
- 复用 CPU PhysX 物理轨迹记录、初态 hash、视频、成功判据、唯一 reset 及预算 guard。
- 实现环境和可靠 Oracle，分别核验 Grasp、Reorient、Insert。若原子动作可靠性不过关，记录工程障碍，**不把控制失败写作组合失败**。

**D2–D3：预注册的反事实/强 baseline 检查**：
- 调试用 3 个初态不纳入统计；冻结任务参数后，以 12 个新初态 × A/B 两后继目标 × P/Q 两个合法抓取组成最多 48 个基本反事实组合。
- 优先实际比较：B1 贪心当前抓取；B2 完整几何规划 + 反馈重抓（强主基线）；B3 同观测、相同前向仿真预算的 rollout/CEM；B4 离线穷举 Oracle（只作为上界，不能在执行时泄露真值）。
- 必须记录：同一初态和相同前缀、P/Q 同时合法、阶段成功、真实接触、插入深度、重抓次数、规划时间、规划调用/物理 rollouts、失败归因及视频。
- 反事实优选反转需来源于实际成功/碰撞/可达性差异；仅路径长度反转不算科学证据。
- 上述 48 次只是 **机制筛选**，不是可用于论文结论的正式统计样本。

**D4：决策，不训练新方法**：
- 如无法产生合理合法的 P/Q 同时成功的第一阶段，归类为任务/控制工程问题而不是科学问题。
- 如 B2/B3 使用正常反馈与预算已接近离线 Oracle，判定 `NO_NOVEL_GAP`，**立即停止此候选研究，不自动设计新环境、改阈值或扩展模型**。
- 如能够稳定复现“前驱成功、后继失败且原因是跨技能接触/可行性变化”，且强基线确有差距，再批准 D5–D7 的小型学习测试。

**D5–D7（有条件）：学习式 3D 表征必要性**：
- 用训练初态与测试初态严格隔离的仿真数据，同时训练 State-MLP（精确 6D 状态、目标和技能）以及 3D-contact-affordance 模型（同等可用信息 + 局部三维交互特征）。
- 同样目标、训练样本、参数/时间/搜索预算，比较 B2/B3 与两个学习模型。
- 若 3D 模型相对 State-MLP 与 rollout-CEM 没有可重复优势，或只是增加信息、计算预算带来优势，停止。
- 正式进入论文开发前，再做 STAP、GSC、TASP、Skill-RRT 等的原论文机制审计与同协议忠实适配；适配不完整要明确标注，`NOT_RUN` 不写性能。

**硬规则：7 个工作日内只允许这一条任务线；不得通过改变任务定义“寻找新方法的胜利”。所有 Go/No-Go 均可得出终止结论。**

## 4. 向 Codex 交付的最小文件

```text
projects/affordance_skill_composition/
  README.md
  configs/frozen_v0.yaml
  envs/keyed_part_pick_insert.py
  skills/grasp.py
  skills/reorient.py
  skills/insert.py
  planners/myopic.py
  planners/geometry_replan.py
  planners/budgeted_rollout.py
  scripts/verify_oracle.py
  scripts/run_counterfactual.py
  scripts/evaluate_baselines.py
  reports/GO_NO_GO.md
  outputs/  # 用户 GPU 服务器本地保存，勿上传大文件
```

部署与运行必须使用用户现有环境的真实路径，以 `--help` 和测试确认命令，不凭空声称任何命令在服务器执行过。

## 5. 最低验收报告

必须用同一份报告答复：
1. 哪些成功的前驱动作会在真实碰撞/接触层面破坏后继技能？有多少合法匹配对？
2. 能否通过正常 IK/反馈重抓/全局几何搜索解决？B2/B3 与离线 Oracle 的差距是多少？
3. 若确有差距，3D 交互信息是否提供 6D 精确状态无法给出的额外价值？是否公平匹配了计算量？
4. 当前结果对应 **GO / ENGINEERING_BLOCKED / NO_NOVEL_GAP** 中哪一种？无论结果如何，不自动换题。

**当前状态：PLAN_ONLY；代码、环境和新实验尚未执行。**
