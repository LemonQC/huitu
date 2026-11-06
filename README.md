# Cross-Behavior / Cross-Embodiment Learning — T-RO Research Log

> 本仓库记录**当前对话**中围绕机器人跨行为与跨本体学习的研究决策、Baseline、数据、真实实验结果及后续规划，不引用其他聊天内容。2026-11-06 建立。

## 核心目标

围绕 **Learning Task-Equivalent Behaviors Across Embodiments（跨本体任务等价行为学习）**，验证能否从不同本体、不同动作方式的示范中学习任务约束及允许变化的行为自由度，让目标机器人在自身动作空间中完成同一任务。

**重要状态**：这是待验证研究假设，并非已完成、已证明优于现有方法的算法。

## 研究日志

- [2026-11-06：当前对话完整阶段记录](docs/research_log/2026-11-06_cross_behavior_research.md)
- [统一复现实验协议](docs/UNIFIED_BENCHMARK_PROTOCOL.md)

## 工程原则

1. **同一目标仿真环境**：先沿用 ManiSkill 的 PickCube-v1 等任务；真正的 Cross-Behavior 实验必须构造**同目标、多操作方式**示范，不能把不同任务硬拼。
2. **单卡 RTX 4090（24GB）**：小规模数据、可控模型和单卡可行性优先，不默认下载 TB 级数据或训练大型视频生成器。
3. **统一优先，不是强行一个依赖集合**：目标策略训练和 rollout 使用同一 `cbl4090` 环境及统一接口；如第三方视频预处理确有冲突，允许隔离预处理环境，输出统一数据格式，不污染主体环境。
4. **官方实现 / 作者方法的重新实现分清楚**：记录方法来源、commit、实现差异、监督条件、模态、训练预算和评测协议，不把轻量近似当作原论文复现。
5. **结果可核查**：真实成功率、训练损失、初始评估、最优训练评估、独立测试分开；报告多个种子与置信区间。
6. **对话留档**：每次在本对话中形成新的决策或收到实验结果时，更新研究日志并提交到本仓库；此过程需要对话触发，**不会在离线或后台自动执行**。

## 当前已知结果（2026-11-06）

PickCube-v1，100条机器人示范，随机种子42：官方 DP 30,000 iterations，最后评估 Success Once=100%、Success at End=70%；官方 ACT 最后记录位于 29,000 iterations，Success Once=30%、Success at End=0%。两者评估每次20 episodes，尚不足以作为论文最终统计。

详见研究日志。

## 独立技能组合课题（新研究线）

- [机器人技能组合 / 同一 ManiSkill 环境的 Baseline First 项目](projects/skill_composition/README.md)
- [给 Codex 的直接执行指令](projects/skill_composition/docs/CODEX_EXECUTION_PROMPT_ZH.md)

该项目与上述 Cross-Behavior / Cross-Embodiment 研究独立，实验、数据与论文结论不得混用。
