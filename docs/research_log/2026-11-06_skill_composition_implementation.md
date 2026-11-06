# 2026-11-06 — 技能组合方案落地与代码提交记录

> 研究对话摘要（不含用户聊天逐字备份）。如需逐字完整聊天，仍需由 ChatGPT 界面导出后手动保存；当前工具无法自动读取完整历史消息。禁止将公共 GitHub 用于保存 token 和个人隐私。

## 用户本轮要求

> 注意，咱们每次的聊天记录都需要记录成md，并且保存到 https://github.com/LemonQC/huitu。我建议尽可能的方法都在一个环境，算法可以重新实现呀，并且确定好到底现在该干啥，需要弄哪些代码，你弄好，我让codex去复现。

## 决定与依据

1. 当前 GitHub 主分支还存在其他研究项目 Cross-Behavior / Cross-Embodiment；这条技能组合研究单独存放在 `projects/skill_composition/`，保留根目录已有资料。
2. 统一 ManiSkill3/SAPIEN、Panda 单机械臂、第一阶段状态观测、同一连续物理场景；允许外部方法忠实重实现，但不可把概念近似伪称原论文。
3. Phase0 用官方 StackCube 做 pilot，校验回放、BC、训练/验证按 episode 分组、评测日志；这不是发表级的长时序任务。
4. Phase1 `HandoffRegraspStack-v0` 物理连续抓取、临时放置、松爪、重新抓取、最终堆叠任务。已编写初版环境代码，但尚未 GPU/物理成功验证；暂不声称“未见组合泛化”。
5. Codex 首先完成环境 smoke、oracle 成功轨迹、正式数据协议、BC/Q-CEM/重规划；之后 STAP、GSC、SPIN 的忠实重实现。先失败分析、后新算法；不继续扩展旧 IHCL。
6. T-RO 目标需要强 baseline 难以解决的真实问题、机制证据、跨任务/真机验证；当前绝不承诺能够完成投稿或发表。

## 已提交代码

- `projects/skill_composition/src/skillcomp/bench.py`：官方 StackCube 单场景三阶段物理监视。
- `projects/skill_composition/src/skillcomp/handoff_env.py`：自定义连续四阶段任务初版。
- `scripts/smoke.py`、`scripts/smoke_handoff.py`：真实物理调用的测试入口。
- `scripts/make_dataset.py`、`scripts/train_bc.py`、`scripts/eval_bc.py`：官方演示重放后 state/动作数据、BC 训练评测。
- `src/skillcomp/bc.py`、`src/skillcomp/utils.py`、`tests/test_splits.py`：模型、记录和 episode split 单测。
- `docs/PLAN_ZH.md`、`docs/BASELINES_ZH.md`、`docs/ENV_STATUS.md`、`AGENTS.md`、`docs/CODEX_EXECUTION_PROMPT_ZH.md`。

## 实际提交记录

- `5485b98` 文档与研究日志
- `8ea2a09` StackCube + BC 实验代码
- `d51acee` HandoffRegraspStack 初版环境
- `97a9a60` 环境 robot_uids 初始化修复
- `ac34c34` Codex 执行任务书
- 后续导航文档补充另行提交

## 验收状态

| 项目 | 状态 |
|---|---|
| GitHub 文档及代码写入 | VERIFIED：GitHub 写入返回 commit SHA |
| Python 语法/单元测试 | NOT_RUN：当前执行环境不能安装本项目 ManiSkill 依赖 |
| `StackCubePilot` 物理 smoke | NOT_RUN：需要用户的 Linux/SAPIEN 环境 |
| `HandoffRegraspStack-v0` oracle | NOT_STARTED |
| 多种独立学到的技能策略 | NOT_STARTED |
| BC/DP/ACT/Q-CEM/STAP/GSC/SPIN 正式统一对比 | NOT_STARTED |
| 完整投稿级实验、真机实验 | NOT_STARTED |

## Codex 首轮验收门槛

按 `projects/skill_composition/docs/CODEX_EXECUTION_PROMPT_ZH.md` 的 M0/M1 先跑通安装、单测、真实物理和至少三个独立 reset 的四阶段真实 oracle 全成功示范。未达到不进行大量模型训练。

下一次对话继续维护独立 MD，不可假定后台自动同步。
