# Baseline 注册表（强对照与实现身份）

状态截至 2026-11-06：**本项目没有完成以下论文方法的统一重实现。严禁将计划中的方法称为已跑通**。

| 优先级 | Method | 核心能力 | 本项目状态 | 对应来源 |
|---|---|---|---|---|
| P0 | Random/No Repair | 物理及执行下限 | smoke 中实现 random | 自定义控制组 |
| P0 | 官方 Panda Motion Planner | 在 StackCube 作 oracle sanity check | 调用官方脚本，未跑 | ManiSkill motionplanning 示例 |
| P0 | Conditioned BC-MLP | 同状态与动作数据的学习基线 | v0.1 实现（未在服务器验证） | 通用行为克隆；不是论文复现 |
| P1 | BC-RNN | 历史状态与动作条件 | 待实现 | RoboMimic 机制/官方 |
| P1 | Diffusion Policy | 强模仿学习条件策略 | 待接入/重训练 | Chi 等, RSS 2023 |
| P1 | ACT | 动作块策略 | 待接入/重训练 | Zhao 等, RSS 2023 |
| P1 | Future Q + CEM | 同等长期信息的价值搜索 | 待实现 | 通用价值学习与 CEM，自定义强基线 |
| P1 | Geometric Planner + Feedback | 正确状态重规划与恢复 | 待实现 | 规划控制组，标记可用特权信息 |
| P2 | STAP | 独立技能 Q + dynamics + 跨技能参数优化 | 待忠实重实现 | Agia 等, ICRA 2023 |
| P2 | GSC | 条件/动作/结果联合分布与测试时组合 | 待忠实重实现 | Mishra 等, CoRL 2023 |
| P2 | SPIN / Skill-RRT | 可行性检查、中间状态采样、connector、蒸馏 | 待忠实重实现 | Jung 等, CoRL 2025 |
| P2 | TAMPURA | 不确定性与风险规划 | 作为后期可选匹配对照 | Curtis 等, RSS 2024 |

**前期应优先让 BC、Future Q+CEM、Geometric+Feedback 与一个最匹配的强论文方法可信运行，而不是追求 12/12 全部跑通。**

身份规则：
- OFFICIAL：原论文官方仓库机制及实现，披露环境适配。
- FAITHFUL_REIMPL：明确重实现论文各模型、数学目标、训练算法，验证关键消融；标注“reimplementation”。
- ADAPTED：核心方法在，但模块或监督已变化；公开差异。
- PROXY：仅抽象思想或简化模型。不得借论文名冒充。
- NOT_RUN：不填任何数据。

公平性：同一完整训练/验证/测试集和环境、物理初态、动作接口；明确控制与感知权限、额外在线交互、训练数据和搜索预算。允许各算法需要的数据形式不同，但必须公开差异与增量实验。

论文链接与官方入口：
- STAP https://arxiv.org/abs/2210.12250
- GSC https://proceedings.mlr.press/v229/mishra23a.html
- SPIN https://proceedings.mlr.press/v305/jung25a.html
- ManiSkill https://maniskill.readthedocs.io/en/latest/
- Diffusion Policy https://diffusion-policy.cs.columbia.edu/
- ACT https://tonyzhaozh.github.io/aloha/
- TAMPURA https://tampura.github.io/

引用链接是待核验文献/项目，不自动代表训练代码、权重、数据都完整开放。