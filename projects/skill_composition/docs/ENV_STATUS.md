# HandoffRegraspStack-v0 环境状态（2026-11-06）

已编写 custom `HandoffRegraspStack-v0`，基于 ManiSkill 官方 `StackCubeEnv`（同一 Panda，同一物理 scene，持续状态，无 skill seam reset），四个阶段通过 simulator evaluator 检查：
1. 抓住红方块抬起；
2. 在蓝色 staging 标记上放下、松开并稳定；
3. 再次抓起；
4. 在绿色方块上堆叠并稳定，松开夹爪。

公开的 `state` 模式可包括阶段 one-hot 和 staging 标记位姿；所有策略须同样可用。**阶段/评估接口可以用 ground truth，但不能隐式向普通视觉策略输入特权 simulator 状态**。

运行：`python scripts/smoke_handoff.py --episodes 2 --steps 30`。

注意：
- **未在用户安装的 ManiSkill 环境验证**，需 Codex 校验当前官方 API。该环境是代码初稿，不是已证明可完成的正式 Benchmark。
- 临时工作区目前是*无碰撞视觉标记*，红绿方块使用真实动力学；需要先从原生运动规划解算器得到 ≥1 组成功示范与视频，再设计障碍和多种合法路径。
- 当前任务只有一个固定技能序列，**不得称为已经验证未见组合泛化**。需要在正式测试前加入至少两种自然合法的组合配置、固定训练/测试组合划分。
- 本文件不能以「随机策略失败」作为研究瓶颈证据；先完成 oracle / BC / 强重规划 / STAP 等对照。
