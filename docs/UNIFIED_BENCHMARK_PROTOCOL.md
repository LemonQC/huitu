# 统一 Baseline 复现实验协议（草案 v0.1）

## 为什么统一

本项目不再以「分别运行作者自己的数据集」构成主比较。原生仓库可用于验证算法正确性，但**论文主表必须在同一目标仿真任务、同一目标机器人和可说明的训练/测试划分下复现**。

## 平台和预算

- GPU：单卡 RTX 4090 24GB。
- 主环境：已运行的 ManiSkill / PyTorch 环境 `cbl4090`；固定版本并输出 `pip freeze`、CUDA/驱动版本。
- 状态-only 基线：PickCube-v1 可做流程验证；**不能由此证明跨本体/跨行为**。
- 视觉跨行为基线：需要额外生成相机图像、物体掩码/轨迹，并设计同任务多行为示范。
- 优先维持同一 Python 环境；如 AnimateDiff/Stable Diffusion 等复杂视觉前处理与主体环境冲突，先离线处理并持久化统一中间表示。

## 方法身份分级

| 标签 | 含义 | 是否可以在主表以论文名标注 |
|---|---|---|
| OFFICIAL | 作者官方实现，原代码或仅合理环境适配 | 可以，需披露修改 |
| FAITHFUL_REIMPL | 按论文结构/损失/监督重实现，关键公式与消融核对 | 可以标“reimplementation”，不能称官方 |
| ADAPTED | 方法机制保留，但更换输入/骨干以适配统一任务 | 标“adapted”，强调可比性限制 |
| PROXY | 简化近似/概念验证 | 不可伪称论文复现；不作为强基线 |
| NOT_RUN | 无可验证代码或数据 | 不得报告成功率 |

## 实验记录要求

每个运行保存：`method`、`method_identity`、论文链接/commit、数据版本、任务、观察模态、动作空间、数据条数、train seed、eval seed、训练步数/epoch、GPU小时、checkpoint选择规则、Success Once、Success at End、测试 episode 数、平均任务长度、崩溃/超时信息。

评测优先使用独立随机种子与每种子 >=50 episodes；多训练种子至少3个作为目标预算。最优 checkpoint 必须由独立验证集选出，在测试集上只评一次。DP/ACT 的迭代数与 epoch 不可直接视作同样预算。

## 方法接入序列

1. 对官方 DP、ACT 做固定 checkpoint 的独立复测。
2. RoboMimic BC 家族接入 ManiSkill 数据，检验状态与动作映射，先做 action replay 和 imitation sanity check。
3. 加入 PushCube/PushT 等操作类型，但不把多任务当跨行为。
4. 新建**同一目标**下 push / pick-place 等不同成功行为数据；统一 RGB、状态、动作、掩码/flow。
5. 对 Im2Flow2Act、XSkill、Object Flow、CORE、UniSkill 逐篇核实论文关键机制、代码开放程度与数据条件，再按分级重实现。
6. 设计非平凡任务，使普通目标条件 DP 与已有流/终态方法有可检验的差异，不依赖凭空设置的未知摩擦参数。

## 重要提醒

作者原生性能和自建 ManiSkill 任务结果只能分表报告。示范数量、公平的监督级别（视频/状态/预训练权重）、评测任务不可被静默改变。