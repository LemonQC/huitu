# 研究方案 v0.1 — Baseline First，不预设新算法

日期：2026-11-06。目标：IEEE T-RO（不承诺录用）。

## 研究问题

学习到的原子技能在新的物理连续组合中，进入与独立训练不同的状态后，是否会出现**超过原子技能自身误差累积的、可重复的额外组合失败**？哪些可由常规感知反馈、连接策略和重规划修复，哪些不能？

不可将已被研究的「考虑后续技能 / 交接优化 / 连接策略 / 状态偏移」直接宣称原创。实验必须先定位真正剩余的不足。

## 唯一主体仿真与两阶段任务

- 引擎：ManiSkill 3 / SAPIEN；Linux + NVIDIA，统一版本记录。
- 机器人：Franka Panda 单机械臂+夹爪；无触觉，第一轮 state，第二轮 RGB-D。
- 动作接口：从 `pd_ee_delta_pose` 开始固定；所有模型接受同样动作权限，若需其他控制器应先转换并记录。
- 统一物理连续 episode；禁止 skill seam 处调用 `reset()` 或直接 `set_pose`。
- **Phase 0（代码已提供的 smoke）**：官方 `StackCube-v1` 场景，依次记 Pick / Move / Stack。检验观察、动作、日志和 seed 记录；因为任务简单**不能用于 T-RO 新颖性论证**。
- **Phase 1（Codex 实现的主任务）**：`HandoffRegraspStack-v0`：同一 Panda + 红绿方块 + 一处真实中间工作区；①提起红块；②放到临时工作区并松爪；③改变抓持方式重新抓取；④将红块堆叠到绿块上。通过工作区位置、目标方向、非穿透几何障碍和有限可达空间产生合理差异。至少提供两条合法实现路径，**不是预写固定成功的两选一停车动作**。
- **Phase 2（只有 Phase 1 通过后）**：同一连续场景的工具复用或受限空间取物；避免为了方法胜出而任意调难度。

## 训练/验证/测试

- 单独原子技能训练数据覆盖其真正可能遇到的入口状态；需在相关入口状态下单测成功率。
- 训练：若干已见合法技能顺序和布局；验证：独立 seeds 与布局；测试：未见且物理合法的组合/顺序、几何布局和物体状态；组合类别必须在训练前固定、逐项登记。
- test 不应与 train 共享完整初始状态，不能把同一 reset 的多种配置记成独立随机初态。
- 按**训练 episode/完整轨迹**划分数据，不得按帧随机打乱；组合数据是否用于训练需明确标注。训练数据量和计算预算在相同能力比较下对齐，强方法可附额外预算曲线。
- 建议初步 3 个训练随机种子、每个测试 setting 至少 100 个独立物理初态作为目标预算；未达到时只能称 pilot。

## 不可省略的六项核对

1. 单技能在组合入口状态可靠性；理想初始化下的高成功率不足以替代。
2. 真实连续执行与原子技能单测；记录前后物体位置/姿态、夹爪、TCP、接触/碰撞。
3. 同状态正确反馈、普通重规划、通用 connector 修复后，还是否留有失败。
4. 区分 observation shift、物理不可达、执行误差、规划缺陷、预算不足。
5. 区分 same-seed 再跑、独立 reset 与跨训练 seed；报告独立样本数和置信区间。
6. 真实机器人与更复杂场景只有核心机制证实后才进入，避免低价值投资。

## 决策门槛

A. 任务真实、原子技能可靠；B. 匹配强 baseline 存在可重复失败；C. 通用补救和合理预算仍不能解决；D. 不同几何/任务族仍有剩余缺口。**只有 A–D 成立才讨论创新算法**。如果 BC/Q-CEM/STAP 都接近 100%，停掉当前任务，不再改到自家方法获胜。

## 数据与结果结构

`results/<run_id>/{config.json,versions.txt,episodes.csv,summary.json,video/,checkpoint/}`（results 不提交 GitHub，只保留小型报告和链接）。episode.csv 至少包含 method, identity, train_seed, reset_seed, task, condition, complete_success, stage_1..4, failure_type, steps, walltime, action_budget, data_count。

复现实验必须分别标记：OFFICIAL / FAITHFUL_REIMPL / ADAPTED / PROXY / NOT_RUN。