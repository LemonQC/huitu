# 给 Codex 的执行指令（复制下面全文作为任务）

仓库：https://github.com/LemonQC/huitu
工作目录：`projects/skill_composition/`。
**只操作本项目目录、必要的独立实验日志；不要修改根目录 Cross-Behavior 项目。**

## 研究目标

Baseline First。用同一个 ManiSkill 3 + Panda 的**连续物理环境**检验技能之间因实际状态变化导致的额外失败。第一阶段先确保任务物理可执行，再训练/比较外部强方法；没有真实 gap 不做新 IHCL。

## 立即执行任务（按顺序，禁止跳过）

### 0. 环境与基础代码核验

1. `git pull`，读取 `AGENTS.md`、`docs/PLAN_ZH.md`、`docs/BASELINES_ZH.md`、`docs/ENV_STATUS.md`。
2. 按项目 pyproject 安装环境（推荐复用当前兼容的 ManiSkill 3 Python 环境），输出 `python -V`、`pip freeze`、`nvidia-smi`、ManiSkill/SAPIEN/Torch 版本；锁定可复现版本，不改已有 Cross-Behavior conda 环境。
3. 运行 `pytest -q tests/`、`python scripts/smoke.py --episodes 2 --steps 20`、`python scripts/smoke_handoff.py --episodes 2 --steps 20`。
4. 修复真实 API 不兼容；不能通过吞掉异常、dummy policy、手动设置 success 等方式伪装成功。把命令、退出码、堆栈、修复 commit 写入 `reports/M0.md`。

### 1. 主环境物理可执行性（**本轮最高优先级**）

在 `HandoffRegraspStack-v0` 同一连续 scene（红方块、绿方块、蓝色工作区、Panda）中，使用 ManiSkill 官方 Panda motion planner API 编写 `scripts/collect_oracle.py` 与 `src/skillcomp/oracle.py`。明确实现：
- Pick red cube (held & lifted)
- Transport red cube to staging area, place physically, release and wait static
- Regrasp red cube physically, lift
- Stack cube on green cube, release and wait static

不许在技能切换时 `reset()`、`set_pose()`、重置机器人 qpos，也不允许将近似几何“成功”代替仿真反馈。记录每阶段执行帧、退出情况、失败原因、物体姿态、夹爪状态及视频。固定同一 test set 的初态。至少先找到 3 个独立 reset 真正贯穿全任务的成功物理轨迹（最低可行性门槛，不代表够发表）；如果不成功先分析环境/机械结构，**停止训练**。

`HandoffRegraspStack-v0` 目前只是初稿：检查仿真是否存在早期虚假成功、阶段状态多次 evaluate 更新、接触不稳定、环境初始化碰撞和物理可达性。修复后冻结场景版本并提交 `reports/M1_oracle.md`。

### 2. 规范示范数据与技能训练

1. 原子技能定义与入口状态分布实际对应，至少收集/切分 Pick、PlaceOnStaging、Regrasp、Stack。
2. 统一动作控制器、state 观测、时间步、场景版本、条件向量和训练集分组；显式验证动作重放轨迹；按完整 episode seed 划分训练/验证/测试。
3. `scripts/make_dataset.py` + `train_bc.py` + `eval_bc.py` 为官方 StackCube pilot，不直接宣称是正式任务的 baseline；为真实主任务另实现 `scripts/collect_skills.py`、`scripts/train_skills.py`、`scripts/eval_skill_chain.py`。
4. 先评估独立技能在真实后续技能入口状态下的可靠性，再报告完整组合成功率。

### 3. 同一环境的强 baseline（先必选，再 P2）

P1 必做：BC-MLP（本仓库为 pilot 代理，实现正式条件版）、BC-RNN、Diffusion Policy、ACT、Future Q + CEM、Geometry + Correct-State Replanning。保留同样观察、底层技能、动作机会与未来条件；标注特权规划器的信息。
P2 文献重实现按优先级 STAP（Q、dynamics、长程技能参数联合优化）→ GSC（扩散式前置/动作/结果分布与测试时采样组合）→ SPIN/Skill-RRT（applicability, object-pose sampling, connector, planning-to-policy distillation）。每个需要论文公式映射、源文献仓库/commit、sanity check 和清楚的 REIMPL/ADAPTED 身份；不能套名为 STAP-MLP、GSC-Q 或 SPIN-CEM。
基础能力首次比较先交付 P1（至少 BC、Q+CEM、正确状态重规划）+ 一个可信 P2，再决定是否继续大规模重实现。

### 4. 固定后续正式评测（不要先设计 IHCL）

- 相同机器人/场景/控制器，测试不见过的合法几何配置与阶段入口状态；若没有新增**未见合法技能顺序**，禁止写 zero-shot skill-order generalization。
- 3 训练 seeds 是目标，不足时报告 pilot；每测试条件至少100独立物理 reset 是目标，不能把同一 reset 下6个配置当6个独立样本。
- 报告 stage success、complete success、最长技能链、失败类型、训练数据量、GPU小时、规划预算、时延、训练/测试划分。
- 普通状态反馈 / 重规划 / connector 修复成功则不能宣称需要复杂新机制。
- 实验结果保存 `results/`（被 gitignore），轻量摘要和命令写 `reports/` 及本项目讨论日志。

## 需要创建的文件

```text
src/skillcomp/oracle.py
src/skillcomp/skills.py
src/skillcomp/policies/{bc_rnn,diffusion,act,q_cem,geometric}.py
src/skillcomp/planners/{stap,gsc,skill_rrt}.py   # 只有对应忠实复现后才使用这些名字
scripts/collect_oracle.py
scripts/collect_skills.py
scripts/train_skills.py
scripts/eval_skill_chain.py
scripts/eval_methods.py
configs/task_splits.json
configs/baselines.yaml
tests/test_handoff_env.py
tests/test_no_reset_at_seam.py
tests/test_data_controller.py
reports/M0.md
reports/M1_oracle.md
reports/BASELINE_FAILURE_REPORT.md
```

文件名是交付规划而非已存在的代码。禁止生成空实现和虚假指标占位以宣称完成。

## 完成一次交付的定义

提供可复制 shell 命令、真实 exit code、成功视频、完整原始 log、seed 列表、baseline 归属、git commit sha。若任一关键环节失败，明确显示 BLOCKED 并停止下一阶段，不进行未经支持的论文设计。
