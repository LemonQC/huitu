# Skill Composition — 统一环境研究（独立课题）

**状态：v0.1 Baseline First；没有完成 T-RO 创新验证。**

与本仓库现有的 Cross-Behavior / Cross-Embodiment 项目不同，本目录只研究**单机器人技能组合、状态交接和未见任务组合**。不得混用已有项目结果。

## 立即运行

Linux + NVIDIA，Python 3.10+。在本目录执行：

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e .
python scripts/smoke.py --episodes 2 --steps 20
python -m mani_skill.examples.motionplanning.panda.run -e StackCube-v1 --save-video
```

运行后首先核验版本、控制模式、视频和成功判据。这个 `StackCube-v1` Pick→Move→Stack 阶段划分**仅是流水线自检，不是发表级 Benchmark**。

接下来用官方演示（请查 docs/PLAN_ZH.md）建立第一版 BC 并测试其泛化；再实现同一连续场景的 `HandoffRegraspStack-v0`（中间放置、再抓、再堆叠；包括真实合法的未见组合和状态变化）。禁止在前一个技能和后一个技能之间 reset 物理环境。

## 研究文档

- [固定问题、任务划分、实验门槛](docs/PLAN_ZH.md)
- [算法清单、复现身份、优先级](docs/BASELINES_ZH.md)
- [交付给 Codex 的任务与验收](AGENTS.md)
- [讨论记录](../../docs/research_log/2026-11-06_skill_composition.md)

## 复现基本原则

- 一个目标 ManiSkill/SAPIEN 物理环境，一个 Panda 机器人，统一控制模式和 episode 协议。
- 算法可以重新实现，但应保留论文关键模型/目标和规划机制；标明官方/忠实重实现/适配/简化版。
- 不能把官方单技能示范直接当作未见组合训练数据。
- 所有报告来自真实运行记录；无证据不得填 100%、SOTA 或 T-RO 已达标。
- 视频、独立 reset 和独立训练随机种子均需记录。